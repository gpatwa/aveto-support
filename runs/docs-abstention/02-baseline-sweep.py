"""docs-abstention A2 baseline: per-question signals and a fixed-grid abstention sweep.

Read-only with respect to the product: it imports aveto_support and calls load_index,
OnnxEmbedder, Searcher, retrieve and load_eval_set; it changes nothing under aveto_support/.

Usage, from the repo root (paths are relative to --repo-root, default "."):
  uv run --offline python runs/docs-abstention/02-baseline-sweep.py collect --out-dir runs/docs-abstention
  uv run --offline python runs/docs-abstention/02-baseline-sweep.py sweep   --out-dir runs/docs-abstention

`collect` needs index/ and models/ (offline). `sweep` reads only the CSV `collect` wrote.

GRID, FIXED BEFORE ANY RESULT WAS LOOKED AT:
  threshold t = 0.40 .. 0.90 step 0.01 (51 values); abstain when top1 < t.
  margin    m = 0.000 .. 0.100 step 0.005 (21 values); abstain when margin < m.
  combined: abstain when top1 < t OR margin < m, over the full 51 x 21 grid.
SIGNAL (primary, scope C2): per returned file (the five files `retrieve` returns), the file's
  score = the best dense cosine similarity over ALL passages of that file. top1 = the highest of
  the five, top2 = the second highest of the five (distinct files), margin = top1 - top2.
SECONDARY margin (declared up front because "top-2" is ambiguous): pmargin = top1 minus the second
  highest passage similarity among all passages of the five returned files (may be the same file).
  It is swept for the margin family only and is labelled secondary everywhere.
BARS: Bar 1 = unanswerable questions abstained / unanswerable. Bar 2 = answerable questions whose
  accepted file is in the five returned files (before any abstention) and that are NOT abstained /
  those answerable questions (scope C4).
LOSO: for each set H held out, over the other three sets pick the cell maximising
  min(Bar1 fraction, Bar2 fraction), ties to the lowest t then the lowest m; score it on H.
"""

from __future__ import annotations

import argparse
import csv
import os
import statistics
import sys
from pathlib import Path

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_name] = "1"

SETS = [
    ("retrieval", "evals/retrieval.toml"),
    ("heldout", "evals/retrieval-heldout.toml"),
    ("heldout-3", "evals/retrieval-heldout-3.toml"),
    ("heldout-4", "evals/retrieval-heldout-4.toml"),
]
T_GRID = [round(0.40 + 0.01 * i, 2) for i in range(51)]
M_GRID = [round(0.005 * i, 3) for i in range(21)]
COLS = [
    "set", "id", "label", "hard_negative", "in_top5", "rank", "top1", "top2", "margin",
    "pmargin", "top1_printed_global", "top1_shown", "files",
]


def collect(root: Path, out_dir: Path) -> None:
    sys.path.insert(0, str(root))
    from aveto_support.embed import OnnxEmbedder
    from aveto_support.evaluate import check_commit, load_eval_set
    from aveto_support.index import load_index
    from aveto_support.search import INT8_UNIT, Searcher, retrieve  # noqa: F401

    index = load_index(root / "index/docs-index.json")
    embedder = OnnxEmbedder.load(root / "models", index.params.embedding)
    try:
        searcher = Searcher(index, embedder)
        rows: list[dict[str, object]] = []
        for set_name, rel in SETS:
            eval_set = load_eval_set(root / rel)
            check_commit(index, eval_set)
            for q in eval_set.questions:
                result = retrieve(searcher, q.question)
                sims = searcher.passage_sims(embedder.embed_query(q.question))
                by_file: dict[str, list[float]] = {}
                for passage, sim in zip(index.passages, sims, strict=True):
                    by_file.setdefault(passage.path, []).append(sim)
                returned = [f.path for f in result.files]
                file_scores = sorted((max(by_file[p]) for p in returned), reverse=True)
                pass_scores = sorted((s for p in returned for s in by_file[p]), reverse=True)
                shown = [
                    sims[i]
                    for i, passage in enumerate(index.passages)
                    if any(
                        passage.path == f.path and passage.line_start == m.passage.line_start
                        for f in result.files
                        for m in f.passages
                    )
                ]
                rank = ""
                if q.answerable:
                    ranks = [f.rank for f in result.files if f.path in q.sources]
                    rank = min(ranks) if ranks else ""
                rows.append(
                    {
                        "set": set_name, "id": q.id,
                        "label": "answerable" if q.answerable else "unanswerable",
                        "hard_negative": int(q.hard_negative),
                        "in_top5": int(rank != "") if q.answerable else "",
                        "rank": rank if rank != "" else "none",
                        "top1": repr(file_scores[0]), "top2": repr(file_scores[1]),
                        "margin": repr(file_scores[0] - file_scores[1]),
                        "pmargin": repr(pass_scores[0] - pass_scores[1]),
                        "top1_printed_global": repr(result.top_score),
                        "top1_shown": repr(max(shown)),
                        "files": "|".join(returned),
                    }
                )
    finally:
        embedder.close()
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "02-baseline-questions.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows")


# ---------------------------------------------------------------- sweep


def load_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open() as handle:
        for r in csv.DictReader(handle):
            rows.append(
                {
                    **r,
                    "top1": float(r["top1"]), "top2": float(r["top2"]),
                    "margin": float(r["margin"]), "pmargin": float(r["pmargin"]),
                    "top1_printed_global": float(r["top1_printed_global"]),
                    "top1_shown": float(r["top1_shown"]),
                }
            )
    return rows


def abstains(
    r: dict[str, object], t: float | None, m: float | None, mkey: str = "margin",
    tkey: str = "top1",
) -> bool:
    if t is not None and float(r[tkey]) < t:  # type: ignore[arg-type]
        return True
    return m is not None and float(r[mkey]) < m  # type: ignore[arg-type]


def counts(
    rows: list[dict[str, object]], t: float | None, m: float | None, mkey: str = "margin",
    tkey: str = "top1",
) -> tuple[int, int, int, int]:
    """(unans abstained, unans total, hits not abstained, hits total)."""
    ua = ut = hn = ht = 0
    for r in rows:
        ab = abstains(r, t, m, mkey, tkey)
        if r["label"] == "unanswerable":
            ut += 1
            ua += ab
        elif r["in_top5"] == "1":
            ht += 1
            hn += not ab
    return ua, ut, hn, ht


def pct(a: int, b: int) -> str:
    return f"{100 * a / b:.1f}%" if b else "n/a"


def ge(a: int, b: int, p: int) -> bool:
    """a/b >= p/100 in integers (p=80 or 90)."""
    return b > 0 and a * 100 >= b * p


def minfrac(c: tuple[int, int, int, int]) -> float:
    ua, ut, hn, ht = c
    return min(ua / ut if ut else 1.0, hn / ht if ht else 1.0)


def cells(family: str) -> list[tuple[float | None, float | None]]:
    if family == "threshold":
        return [(t, None) for t in T_GRID]
    if family == "margin":
        return [(None, m) for m in M_GRID]
    return [(t, m) for t in T_GRID for m in M_GRID]


def lab(c: tuple[float | None, float | None]) -> str:
    t, m = c
    return f"t={t:.2f}" if m is None else (f"m={m:.3f}" if t is None else f"t={t:.2f},m={m:.3f}")


def stats(vals: list[float]) -> str:
    if not vals:
        return "n=0"
    return f"n={len(vals)} min={min(vals):.3f} med={statistics.median(vals):.3f} max={max(vals):.3f}"


def sweep(out_dir: Path) -> None:
    rows = load_rows(out_dir / "02-baseline-questions.csv")
    names = [n for n, _ in SETS]
    by_set = {n: [r for r in rows if r["set"] == n] for n in names}
    md: list[str] = []

    # ---- integrity
    ids = [(r["set"], r["id"]) for r in rows]
    texts_dupe = len(rows) - len({r["files"] for r in rows})  # not used; kept out of the report
    del texts_dupe
    md.append("## Integrity\n")
    md.append(f"- rows: {len(rows)}; answerable {sum(r['label'] == 'answerable' for r in rows)}, "
              f"unanswerable {sum(r['label'] == 'unanswerable' for r in rows)}")
    md.append(f"- (set, id) pairs unique: {len(ids) == len(set(ids))}; ids repeated across sets: "
              f"{sorted({i for _, i in ids if [x for _, x in ids].count(i) > 1})}")
    hits = [r for r in rows if r["in_top5"] == "1"]
    md.append(f"- answerable with accepted file in top 5 (Bar 2 denominator): {len(hits)}; "
              f"answerable misses: {sum(r['in_top5'] == '0' for r in rows)}")
    diff_g = [r for r in rows if abs(float(r["top1"]) - float(r["top1_printed_global"])) > 1e-12]  # type: ignore[arg-type]
    diff_s = [r for r in rows if abs(float(r["top1"]) - float(r["top1_shown"])) > 1e-12]  # type: ignore[arg-type]
    md.append(f"- top1 (best passage of the five returned files) differs from the printed global "
              f"`Top score` on {len(diff_g)} questions: {[(r['set'], r['id']) for r in diff_g]}")
    md.append(f"- top1 differs from the best SHOWN passage on {len(diff_s)} questions: "
              f"{[(r['set'], r['id']) for r in diff_s]}")
    md.append("")

    # ---- step 4 distributions
    md.append("## Top-1 score distribution (primary signal), by group\n")
    md.append("| set | answerable-hit | answerable-miss | unanswerable |")
    md.append("|---|---|---|---|")
    groups = {
        "hit": lambda r: r["label"] == "answerable" and r["in_top5"] == "1",
        "miss": lambda r: r["label"] == "answerable" and r["in_top5"] == "0",
        "unans": lambda r: r["label"] == "unanswerable",
    }
    for n in names + ["POOLED"]:
        sub = rows if n == "POOLED" else by_set[n]
        cell = [stats([float(r["top1"]) for r in sub if g(r)]) for g in groups.values()]  # type: ignore[arg-type]
        md.append(f"| {n} | " + " | ".join(cell) + " |")
    md.append("")
    md.append("## Margin (top1 - top2 file) distribution, by group\n")
    md.append("| set | answerable-hit | answerable-miss | unanswerable |")
    md.append("|---|---|---|---|")
    for n in names + ["POOLED"]:
        sub = rows if n == "POOLED" else by_set[n]
        cell = [stats([float(r["margin"]) for r in sub if g(r)]) for g in groups.values()]  # type: ignore[arg-type]
        md.append(f"| {n} | " + " | ".join(cell) + " |")
    md.append("")
    h4 = [float(r["top1"]) for r in by_set["heldout-4"] if groups["hit"](r)]  # type: ignore[arg-type]
    md.append("## Intent paragraph, set 4 (heldout-4)\n")
    md.append(f"- answerable hits top-1: min {min(h4):.3f}, max {max(h4):.3f} (n={len(h4)}); "
              f"sorted: {[round(x, 3) for x in sorted(h4)]}")
    for r in by_set["heldout-4"]:
        if r["label"] == "unanswerable":
            md.append(f"- {r['id']}: top1 {float(r['top1']):.3f} (printed global {float(r['top1_printed_global']):.3f}), "  # type: ignore[arg-type]
                      f"above every answerable hit on this set: {float(r['top1']) > max(h4)}")  # type: ignore[arg-type]
    md.append("")

    # ---- sweeps
    summary: list[str] = []
    for family, mkey in (("threshold", "margin"), ("margin", "margin"), ("margin", "pmargin"),
                         ("combined", "margin")):
        fam_name = family if mkey == "margin" else "margin-secondary(pmargin)"
        csv_name = f"02-baseline-sweep-{fam_name.split('(')[0]}.csv"
        with (out_dir / csv_name).open("w", newline="") as handle:
            w = csv.writer(handle)
            head = ["t", "m", "pooled_B1_num", "pooled_B1_den", "pooled_B2_num", "pooled_B2_den"]
            for n in names:
                head += [f"{n}_B1_num", f"{n}_B1_den", f"{n}_B2_num", f"{n}_B2_den"]
            w.writerow(head)
            results = []
            for t, m in cells(family):
                pooled = counts(rows, t, m, mkey)
                line = ["" if t is None else f"{t:.2f}", "" if m is None else f"{m:.3f}", *pooled]
                for n in names:
                    line += list(counts(by_set[n], t, m, mkey))
                w.writerow(line)
                results.append(((t, m), pooled))
        best = max(results, key=lambda x: (minfrac(x[1]), -(x[0][0] or 0), -(x[0][1] or 0)))
        room = [lab(c) for c, p in results if ge(p[0], p[1], 90) and ge(p[2], p[3], 90)]
        both80 = [lab(c) for c, p in results if ge(p[0], p[1], 80) and ge(p[2], p[3], 80)]
        summary.append(
            f"- **{fam_name}** ({len(results)} cells): best pooled min(Bar1,Bar2) = "
            f"{minfrac(best[1]):.3f} at {lab(best[0])} (Bar1 {best[1][0]}/{best[1][1]}, "
            f"Bar2 {best[1][2]}/{best[1][3]}; first cell reaching that max in lowest-t, lowest-m "
            f"order). Cells with both bars >= 90% pooled: {len(room)}"
            + (f" {room[:10]}" if room else "")
            + f". Cells with both bars >= 80% pooled: {len(both80)}"
            + (f" (first/last: {both80[0]} / {both80[-1]})" if both80 else "")
        )
        if family == "threshold" or (family == "margin" and mkey == "margin"):
            md.append(f"## Sweep: {fam_name} rule, pooled and per set (counts)\n")
            md.append("Bar1 = unanswerable abstained/den; Bar2 = hits not abstained/den.\n")
            md.append("| cell | pooled B1 | pooled B2 | " + " | ".join(f"{n} B1 | {n} B2" for n in names) + " |")
            md.append("|---|---|---|" + "---|---|" * len(names))
            for c, p in results:
                per = []
                for n in names:
                    q = counts(by_set[n], c[0], c[1], mkey)
                    per += [f"{q[0]}/{q[1]}", f"{q[2]}/{q[3]}"]
                md.append(f"| {lab(c)} | {p[0]}/{p[1]} ({pct(p[0], p[1])}) | {p[2]}/{p[3]} "
                          f"({pct(p[2], p[3])}) | " + " | ".join(per) + " |")
            md.append("")
        if family == "combined":
            # Pareto frontier on (B1 count, B2 count), then list; ties keep the lowest t, lowest m.
            frontier: dict[tuple[int, int], tuple[float | None, float | None]] = {}
            for c, p in results:
                key = (p[0], p[2])
                if key not in frontier:
                    frontier[key] = c
            keys = sorted(frontier)
            nd = [k for k in keys if not any(
                o != k and o[0] >= k[0] and o[1] >= k[1] for o in keys)]
            md.append("## Sweep: combined rule (t OR m), pooled Pareto frontier\n")
            md.append("Cells not dominated on (Bar1 count, Bar2 count); first cell in (t, m) order "
                      "per distinct pair. Full 1071-cell table in 02-baseline-sweep-combined.csv.\n")
            md.append("| cell | pooled B1 | pooled B2 | min frac |")
            md.append("|---|---|---|---|")
            for k in nd:
                p = counts(rows, frontier[k][0], frontier[k][1])
                md.append(f"| {lab(frontier[k])} | {p[0]}/{p[1]} ({pct(p[0], p[1])}) | "
                          f"{p[2]}/{p[3]} ({pct(p[2], p[3])}) | {minfrac(p):.3f} |")
            md.append("")
    md.append("## Pooled sweep summary by family\n")
    md.extend(summary)
    md.append("")

    # ---- secondary: threshold on the printed global top score; and the ingest reference as a counterfactual
    md.append("## Secondary: threshold on the PRINTED global `Top score` (max over all 890 passages)\n")
    md.append("Declared up front as secondary: the existing confidence is this quantity (search.py "
              "`max(sims)`), which differs from the primary signal on some questions.\n")
    gres = [((t, None), counts(rows, t, None, "margin", "top1_printed_global")) for t in T_GRID]
    gbest = max(gres, key=lambda x: (minfrac(x[1]), -(x[0][0] or 0)))
    groom = [lab(c) for c, p in gres if ge(p[0], p[1], 90) and ge(p[2], p[3], 90)]
    g80 = [lab(c) for c, p in gres if ge(p[0], p[1], 80) and ge(p[2], p[3], 80)]
    md.append(f"- best pooled min(Bar1,Bar2) = {minfrac(gbest[1]):.3f} at {lab(gbest[0])} "
              f"(Bar1 {gbest[1][0]}/{gbest[1][1]}, Bar2 {gbest[1][2]}/{gbest[1][3]}); cells with both "
              f">= 90%: {len(groom)}; both >= 80%: {len(g80)}")
    with (out_dir / "02-baseline-sweep-threshold-global.csv").open("w", newline="") as handle:
        w = csv.writer(handle)
        w.writerow(["t", "B1_num", "B1_den", "B2_num", "B2_den"])
        for c, p in gres:
            w.writerow([f"{c[0]:.2f}", *p])
    ref = 0.701717
    md.append("")
    md.append("## Counterfactual: the ingest reference similarity 0.701717 applied as a threshold "
              "(NOT what the default path does today)\n")
    for tk in ("top1", "top1_printed_global"):
        p = counts(rows, ref, None, "margin", tk)
        md.append(f"- signal `{tk}`: Bar1 {p[0]}/{p[1]} ({pct(p[0], p[1])}), Bar2 {p[2]}/{p[3]} "
                  f"({pct(p[2], p[3])})")
    md.append("")

    # ---- LOSO
    md.append("## Leave-one-set-out (committed procedure)\n")
    md.append("Train = the other three sets; best cell maximises min(Bar1 frac, Bar2 frac) on "
              "train, ties to lowest t then lowest m; scored on the held-out set.\n")
    md.append("| family | held-out | chosen cell | train B1 | train B2 | held-out B1 | held-out B2 | "
              ">=80% both |")
    md.append("|---|---|---|---|---|---|---|---|")
    loso_pool: dict[str, list[int]] = {}
    loso_ok: dict[str, list[bool]] = {}
    for family in ("threshold", "margin", "combined"):
        loso_pool[family] = [0, 0, 0, 0]
        loso_ok[family] = []
        for held in names:
            train = [r for r in rows if r["set"] != held]
            test = by_set[held]
            best_c = min(
                cells(family),
                key=lambda c: (-minfrac(counts(train, c[0], c[1])), c[0] or 0.0, c[1] or 0.0),
            )
            tr = counts(train, best_c[0], best_c[1])
            te = counts(test, best_c[0], best_c[1])
            ok = ge(te[0], te[1], 80) and ge(te[2], te[3], 80)
            loso_ok[family].append(ok)
            for i in range(4):
                loso_pool[family][i] += te[i]
            md.append(f"| {family} | {held} | {lab(best_c)} | {tr[0]}/{tr[1]} ({pct(tr[0], tr[1])}) | "
                      f"{tr[2]}/{tr[3]} ({pct(tr[2], tr[3])}) | {te[0]}/{te[1]} | {te[2]}/{te[3]} | "
                      f"{'yes' if ok else 'no'} |")
    md.append("")
    md.append("LOSO pooled over the four folds (sum of held-out counts):\n")
    for family, (ua, ut, hn, ht) in loso_pool.items():
        md.append(f"- {family}: Bar1 {ua}/{ut} ({pct(ua, ut)}), Bar2 {hn}/{ht} ({pct(hn, ht)}); "
                  f"folds with both held-out bars >= 80%: {sum(loso_ok[family])}/4; pooled-fold "
                  f"both >= 80%: {ge(ua, ut, 80) and ge(hn, ht, 80)}")
    (out_dir / "02-baseline-tables.md").write_text("\n".join(md) + "\n")
    print("\n".join(md[:60]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["collect", "sweep"])
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out-dir", default="runs/docs-abstention")
    args = ap.parse_args()
    root = Path(args.repo_root).resolve()
    out_dir = (root / args.out_dir) if not Path(args.out_dir).is_absolute() else Path(args.out_dir)
    if args.command == "collect":
        collect(root, out_dir)
    else:
        sweep(out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
