# ADR 0002: Lexical (BM25) retrieval over heading passages, with a corpus-calibrated "no confident match" threshold

> Architecture Decision Record. Owned by the Architect. It stays **proposed** until
> docs-retrieval-core's Release Gate shows the eval bar is met, and it becomes
> accepted then. While proposed it may be revised (the overfitting protocol allows
> a bounded, versioned method change after a failed gate). Once accepted, a change
> needs a new ADR that supersedes it.

- **Status:** proposed, **revised once (v2, 2026-09-29)**. See "Revision 1" at
  the end. The Decision below describes v1 as it was first proposed.
- **Date:** 2026-09-28 (v1) and 2026-09-29 (v2)
- **Slice:** `runs/docs-retrieval/` (docs-retrieval-core). The full specification,
  including every parameter, is `runs/docs-retrieval/02-tech-spec.md`, sections
  "Retrieval" (v1) and "Retrieval — variant v2".

## Context

The intent asks retrieval to return up to 5 passages, each with its file, heading
and line range, **or "no confident match" rather than the least-bad passages**
(Done-means 4 and 5). It must reach at least 80% on the owner's eval set, and at
least 80% of the unanswerable questions must abstain (Done-means 8). The
unanswerable ones include hard negatives whose keywords appear in the docs in an
unrelated sense. No model may be called, and dependencies should be as few as
possible. The product stance is "grounded or silent". The repo is a template,
so whatever decides confidence has to work on someone else's docs too, not just
Aveto's.

## Decision

- **Passages are ATX-heading sections.** One section is one passage. Headings
  inside code fences and front matter are ignored. There is no size-based
  splitting, so "path + heading + line range" is always an exact citation.
- **Ranking is BM25**, with k1 = 1.2 and b = 0.75. Each passage is scored as body
  tokens, plus its heading trail counted twice, plus its file path counted once,
  a simple approximation of BM25F. The tokenizer casefolds, splits on
  non-alphanumerics, removes the NLTK English stopword list, and folds plurals
  with Harman's S-stemmer. There is no synonym table. A file contributes at most
  2 of the top 5 passages.
- **Confidence is the idf-weighted fraction of the question's terms that the top
  passage contains** ("coverage", in [0, 1]). Terms that appear nowhere in the
  docs stay in the denominator at maximal weight: if what you asked about is not
  in the docs, the docs do not answer you.
- **The threshold τ is calibrated from the corpus at ingest time.** It is the
  90th percentile of coverage over 2000 seeded "cross-file null" questions. Each
  null question uses 2–5 real words, each drawn from a different file, so every
  word is in the docs but no passage answers the combination. τ is stored in the
  index. Below τ, *no* passages are returned.
- **Every parameter is pre-registered** in the tech spec before the eval set is
  run. The eval set is a test, never a tuning set. Each run is committed, and a
  miss is a failed gate handled by a bounded, versioned method revision, not by
  adjusting knobs.

## Alternatives considered

- **Embeddings (a local sentence-transformer, or an embeddings API).** These
  would likely help with paraphrased questions. A local model means large
  dependencies (torch or onnxruntime, plus a model download, which is network
  access outside the approval). An API means a model call, which the intent rules
  out for this slice. Kept as the owner's option if lexical retrieval cannot meet
  the bar.
- **The `rank-bm25` library, or scikit-learn TF-IDF.** These pull in numpy (and
  scipy), and they hide the per-term scores the coverage signal needs. Our BM25 is
  about 60 lines.
- **A fixed, hand-picked score threshold.** BM25 scores are unbounded and depend
  on the question, so one cut-off means different things for different questions.
  A constant picked for Aveto's docs would not carry over to an adopter's docs,
  and picking it would in practice mean tuning it against the eval set.
- **A relative-margin rule (top score versus the second).** This measures
  ambiguity between passages, not whether any passage answers the question. A
  hard negative can have one clear, wrong winner.
- **Fixed-size chunks instead of heading sections.** Citations would lose the
  heading, and chunks would cut across the author's own structure. Rejected,
  because provenance is a "must not break".
- **Porter stemming.** Its more aggressive folding merges unrelated words, which
  works against hard negatives. Plural folding is the conservative choice.

## Consequences

- **Easier:** no runtime dependencies. Retrieval is fully deterministic and fast.
  Every result explains itself (coverage against τ). Pointing the tool at new
  docs re-calibrates automatically. The drafting slice gets a `RetrievalResult`
  whose `hits` is empty whenever it should not draft.
- **Harder:** paraphrases with no shared vocabulary are missed, and the same word
  used in different senses cannot be told apart lexically. The threshold trades
  answerable recall against abstention, and the trade is decided in advance (p90,
  half the owner's tolerated error), not optimised.
- **Revisit if:** the eval bar is missed after the bounded retries, a fresh
  owner-written question set shows the score does not generalise, or the drafting
  slice's checker reports that confident retrievals often lack the answer. Any of
  these would motivate an embeddings ADR. That ADR carries its own dependency
  cost, and a model call if one is involved.

## Revision 1 — v2 (2026-09-29, retry 1, written before it was run)

**What happened.** v1 was implemented as specified. Eval run 1 scored 2/24
answerable (gated) and 6/6 unanswerable. Its ungated recall@5 was 14/24, and τ
calibrated to 1.000. Ranking alone could not reach 20/24, and the threshold
withheld almost everything.

**Why τ was 1.0. The coverage formula was at fault, and calibration exposed
it.** Coverage is presence-only and saturates at 1.0. In a corpus with one
shared process vocabulary, more than 10% of cross-file null questions were fully
contained in some passage, so the 90th percentile was the ceiling. Coverage's
main abstention ingredient, the penalty for words absent from the docs, could not
be calibrated by nulls made only of in-corpus words. It also penalised
answerable questions phrased in user language as much as unanswerable ones.

**Decision changes. v1 bullets superseded where they conflict:**

- The stemmer changes from Harman S to **Porter (1980)**, as published, in plain
  code. It folds inflections (failing/fail, stopped/stop), not just plurals.
- Ranking changes to **ranking-v2**: `0.5 · passage BM25 / max + 0.5 · file
  BM25 / max`. This combines passage-level and document-level evidence (Callan
  1994), because topics are spread across a file's heading sections. Only
  passages sharing at least one question word are candidates.
- Confidence changes to **corroboration**: the idf mass of the question words
  the top passage contains, *minus the single strongest one*. A lone shared
  keyword scores 0. Absent words are neutral. The value does not saturate.
- Calibration keeps the same null generator (seed, count, lengths, p90), applied
  to the new signal. It has fail-closed sentinels for small or degenerate
  corpora.

**Alternatives rejected for v2:** synonym tables, pseudo-relevance feedback,
retuning the quantile, a per-file cap of 1, larger field weights, merging
sections, a frequency stoplist, proximity scoring, and embeddings (out of scope).
The reasons are in the tech spec.

**Consequence to state plainly.** Recorded before the run: the Architect expects
v2 to improve ranking, with ungated recall around 17/24 (range 15–20). It
expects about a 15% chance of meeting both 80% bars on the original questions.
It no longer relies on the absent-word penalty, so unanswerable accuracy may drop
to 4–6 of 6. **Lexical retrieval is probably bounded below 80% on user-phrased
questions.** If v2 misses, the next decision is embeddings, the owner's call
under rules 5 and 6, recorded in a new ADR. It is not a third lexical variant.
The original 30 questions are no longer unseen. The owner's fresh held-out set
is the evidence for or against v2.
