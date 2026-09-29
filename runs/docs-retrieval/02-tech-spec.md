# Tech Spec — docs-retrieval-core

> Owner: Software Architect Agent
> Status: ready for implementation. **Revised for retry 1 (2026-09-29).** The
> retrieval method is now **variant v2** (`ranking-v2` + `corroboration-v1`),
> pre-registered in "Retrieval — variant v2" before it has been run. The v1 text
> is kept and marked superseded. Everything outside retrieval scoring and its
> tests is unchanged.
> **Added 2026-09-29: "Retrieval — variant embed-v3".** This is a SPEC-ONLY
> hybrid embeddings design for the owner to approve or reject. It is not
> approved and not to be implemented. v2 remains the variant that gets built
> unless every embed-v3 approval is recorded. Freeze-first ordering applies:
> implement, stop before any eval, record the frozen SHA, and then the owner's
> fresh set gates.
> Source: short path, so there is no feature spec or UX spec. Requirements come from
> `runs/docs-retrieval/intent.md` ("Done means", "Must not break", "Constraints") and
> the owner-accepted scope in `runs/docs-retrieval/01-scope.md`.
> Depth: standard. Playbook: `/Users/gopalpatwa/opt/agentic-sdlc-playbook` (absolute path,
> the disclosed worktree workaround).
> Date: 2026-09-28

## Summary

This slice adds a small Python 3.12 command-line tool, `aveto_support`, with three
commands:

- **`ingest`** downloads the markdown of one configured GitHub repo at one pinned
  commit (a single read-only HTTPS archive download, approved under rule 5). It
  splits each file into passages at its headings and writes a deterministic JSON
  index file.
- **`retrieve`** takes a question and uses plain-code lexical search to return up
  to 5 passages with path, heading, line range and a permalink. If it is not
  confident, it returns `no confident match`.
- **`eval`** scores retrieval against the owner's `evals/retrieval.toml`. It
  prints both thresholds and exits non-zero on a miss.

Ranking is BM25, a standard keyword-scoring formula, with the passage's heading
and file path counted as part of the passage. The "no confident match" decision
compares one number (how much of the question's specific vocabulary the top
passage contains) against a threshold. `ingest` calibrates that threshold from
the corpus itself and stores it in the index. It is never fitted to the eval set.
Nothing calls a model. The tool has no runtime dependencies beyond the standard
library, and FastAPI is not installed in this slice (see "Stack").

## Traceability — intent "Done means" → design

Item numbers follow `00-slice-plan.md` §"Success criteria". Core owns 1–5, 8 (meeting
the bar), 10 and 11. It verifies 6 and 7. CI owns 8 (enforcing it) and 9.

| # | Done means | Satisfied by (section of this spec) |
|---|------------|-------------------------------------|
| 1 | Clean checkout installs, type-checks, passes tests with commands in `LOCAL_COMMANDS.md` | "Stack" (uv + committed `uv.lock`, mypy strict, pytest). "CLI contract" gives the exact commands. Implementation records them in `.agentic/LOCAL_COMMANDS.md` ("Files touched") |
| 2 | Ingest reads the pinned repo's markdown, splits by heading, reports file + passage counts | "Ingest": `fetch_archive`, `read_markdown`, `split_passages`. "CLI contract": the ingest report lines |
| 3 | Ingest twice on the same commit → byte-identical output | "Index file format": canonical JSON, sorted, no timestamps, seeded calibration, atomic write. Tests: `test_ingest.py::test_ingest_is_byte_identical*` |
| 4 | Retrieve returns ≤5 passages, each with path, heading, line range in that commit | "Retrieval": `Hit` carries `Passage.path/heading/line_start/line_end` plus a commit permalink. "CLI contract": retrieve output |
| 5 | Unanswerable question → "no confident match", not least-bad passages | "The no-confident-match rule": the whole result set is withheld, and no passage text is printed |
| 6 | Eval set ≥20 + ≥5, labelled, committed | Met at intake (`evals/retrieval.toml`, 24 + 6). Verified by QA. `test_evaluate.py` checks that it parses and that its `pinned_commit` equals the configured commit |
| 7 | Eval set written by owner/QA, committed before tuning | Met at intake (`a4e5275`). "Overfitting protocol" keeps it that way: no role edits it, and every eval run is committed |
| 8 | ≥80% answerable in top 5, ≥80% unanswerable → no match; score printed by a command (CI checks it) | "Eval command": integer threshold check, stable summary lines, exit code 1 on a miss |
| 10 | No model call; only network is the pinned-docs fetch | "Adapter boundaries", "Network surface": one `urlopen` call site, a host-restricted redirect handler, and a test-time network block |
| 11 | ADR 0001, ARCHITECTURE.md started, README explains running against your own docs | `docs/adr/0001-python-fastapi-uv-no-agent-framework.md`, `docs/adr/0002-lexical-retrieval-calibrated-abstention.md`, `docs/ARCHITECTURE.md` (written by this stage). README section specified in "Files touched" |

"Must not break" (the `ai-agent-product` floor):
- *Nothing retrieved is presented as an answer.* Retrieve prints verbatim passage
  excerpts under a `Sources` header and ends with a fixed line, `These are sources, not
  an answer.` No text is generated, summarised or reworded. See "Retrieval" and
  INV-2 in "Safety".
- *The user can always see where every passage came from.* Every hit shows the path,
  heading trail, line range and a `?plain=1#Lx-Ly` permalink at the pinned commit.
  A passage cannot be printed without them, because the output function takes a
  `Hit` and nothing else.

## Stack and structure

The owner already decided the stack (`.agentic/PROJECT_CONTEXT.md`, 2026-09-26).
It is recorded in `docs/adr/0001-python-fastapi-uv-no-agent-framework.md`. This
section covers only what this slice exercises.

- **Python 3.12.** `pyproject.toml` sets `requires-python = ">=3.12,<3.13"`, and
  uv selects or downloads a matching interpreter.
- **uv**, with `uv.lock` committed. `[tool.uv] package = false`, so the project is
  not built or installed and there is **no build backend**, which means no
  build-time dependency. The code is a flat package at the repo root and runs
  with `python -m aveto_support`.
- **No FastAPI in this slice.** The intent asks for an "ingest command" and a
  "retrieve command". The first user is the owner at a terminal, and the drafting
  slice will call `search.retrieve()` as a Python function. An HTTP app would add
  a dependency tree (Starlette, Pydantic, AnyIO and others) and a listening
  network surface that Security would have to review, with no Done-means item to
  serve. FastAPI stays the decided framework, per ADR 0001. It arrives with the
  first slice that needs an HTTP surface (the GitHub App webhook). At that point
  a route wraps `search.retrieve()` without changing it.
- **No agent framework, and no Anthropic SDK yet.** Nothing calls a model.

### Dependencies (the complete list)

**Runtime: none.** Everything uses the standard library:

| Need | Stdlib module | Instead of |
|------|---------------|------------|
| HTTPS download of the pinned archive | `urllib.request` | `requests` / `httpx` |
| Reading the `.tar.gz` in memory | `tarfile`, `io`, `gzip` | `git` CLI or GitPython |
| Reading `docs-source.toml` and `evals/retrieval.toml` | `tomllib` (3.11+) | `tomli` / `toml` |
| Writing the index | `json`, `hashlib`, `os.replace` | a database / SQLite |
| Seeded calibration | `random.Random(seed)` | numpy |
| BM25, tokenizer, stemmer | plain code (~150 lines) | `rank-bm25`, `nltk`, `scikit-learn` |

Library alternatives lost for these reasons. `rank-bm25` pulls in numpy and hides
the per-term scores that the coverage signal needs. `nltk` is a large download for
one stopword list and a stemmer. `scikit-learn` brings numpy and scipy for TF-IDF
that fits in about 40 lines.

**Dev only** (a `[dependency-groups] dev` in `pyproject.toml`, synced by default,
never imported by `aveto_support/`):

| Dependency | What it adds | What it costs |
|------------|--------------|---------------|
| `pytest` | The test runner, required by the intent | About 4 small pure-Python transitive packages (iniconfig, packaging, pluggy, pygments) |
| `mypy` | The type-check for Done-means 1, run with `--strict` | About 3 transitive packages (mypy_extensions, typing_extensions, pathspec) and roughly 20 MB installed. pyright lost because it needs Node |
| `ruff` | Evidence for the Tier 2 gate "no new lint warnings" | One self-contained binary wheel with no transitive dependencies |

Versions are whatever `uv add --dev pytest mypy ruff` resolves at implementation
time, pinned exactly by `uv.lock`. Adding any runtime dependency, or any dev
dependency beyond these three, is out of scope for Implementation. It needs a
return to this spec.

**Toolchain network access is not product network access.** `uv sync` downloads
packages from PyPI (and, if needed, a Python build). Done-means 1 ("a clean
checkout installs") requires this. Done-means 10 is about the product: nothing in
`aveto_support/` touches the network except the pinned-docs fetch. Security
should read it that way. The approval (rule 5) covers the product fetch.

### Code layout

```
aveto_support/
  __init__.py      # package marker and one-line docstring
  __main__.py      # argparse CLI: ingest | retrieve | eval; the exit codes
  ingest.py        # SourceConfig, load_source_config, fetch_archive (the ONLY network code),
                   # read_markdown, run_ingest
  index.py         # Passage, Index, split_passages, serialize_index, write_index, load_index
  search.py        # tokenize, stopwords, S-stemmer, Searcher (BM25 + coverage), calibrate,
                   # retrieve, RetrievalResult, Hit
  evaluate.py      # EvalSet, load_eval_set, score, EvalReport, format_report
tests/
  conftest.py      # autouse network block; in-memory tar.gz fixture builder
  test_ingest.py   # config validation, archive reading, commit check, determinism, live fetch
  test_index.py    # heading splitting, line ranges, serialize/load round-trip
  test_search.py   # tokenizer, stemmer, BM25, per-file cap, no-confident-match, calibration
  test_evaluate.py # scoring, thresholds, exit codes, eval-file sanity, CLI
docs-source.toml   # the configured source (repo + pinned commit)
```

Imports run one way only, so there are no cycles. `index` imports no other
project module. `search` imports `index`. `ingest` imports `index` and `search`
(it calls `search.calibrate`). `evaluate` imports `index` and `search`.
`__main__` imports all four.

## Data model deltas

There is no database. The only persisted artefact is the **generated index file**
(gitignored, never committed; see "Index file format") plus one new committed
config file.

| Type | Change | Rationale |
|------|--------|-----------|
| `docs-source.toml` | new, committed | The configurable source (intent constraint): repo + pinned commit. Aveto's docs are the first configured source |
| `SourceConfig` | new (frozen dataclass) | Validated form of `docs-source.toml` |
| `Passage` | new | One heading section of one file. The unit of retrieval and provenance |
| `Index` | new, persisted as JSON | Passages, source, counts and the calibrated threshold, in one generated file |
| `Hit`, `RetrievalResult` | new, in memory only | What `retrieve` returns. The drafting slice will consume this type unchanged |
| `EvalSet`, `EvalReport` | new, in memory only | Parsed `evals/retrieval.toml` and its score |

### `docs-source.toml` (committed, repo root)

```toml
# The documentation this agent answers from. Point it at your own docs:
# change repo and commit, then re-run ingest.
repo   = "gpatwa/agentic-sdlc-playbook"                 # GitHub "owner/name"
commit = "3a83b669a8b53dfdff869a1bbe361bdb156e3a13"     # full 40-hex SHA; branches/tags rejected
exclude = []                                            # repo-relative path prefixes to skip
```

Validation happens in `load_source_config` and raises `ConfigError` on failure:

- `repo` must match `^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$`.
- `commit` must match `^[0-9a-f]{40}$`. A branch, tag or short SHA is rejected
  because "pinned" means immutable.
- `exclude` must be a list of strings. Each is a prefix; a leading `/` or any
  `..` is rejected.
- Unknown keys are rejected, so a typo cannot pass silently.

**Aveto's configured `exclude` stays `[]`.** Changing it for the Aveto source is
a change to what the agent answers from. It is not a retrieval fix, and the
Implementation stage may not make it (see "Overfitting protocol").

### Python shapes

```python
@dataclass(frozen=True)
class SourceConfig:
    repo: str                       # "owner/name"
    commit: str                     # 40 lowercase hex
    exclude: tuple[str, ...] = ()   # path prefixes

@dataclass(frozen=True)
class DocFile:                      # in memory only
    path: str                       # repo-relative, "/"-separated, archive top dir stripped
    text: str                       # decoded UTF-8, "\r\n" and "\r" normalised to "\n"

@dataclass(frozen=True)
class Passage:
    path: str                       # repo-relative, e.g. "docs/GETTING_STARTED.md"
    heading: str                    # this section's own heading text; "" = text before the first heading
    heading_path: tuple[str, ...]   # enclosing heading trail, outermost first, ending with `heading`
    line_start: int                 # 1-based, inclusive: the heading line (or 1 for the preamble)
    line_end: int                   # 1-based, inclusive: last non-blank line of the section
    text: str                       # verbatim lines line_start..line_end joined with "\n"

@dataclass(frozen=True)
class Index:
    repo: str
    commit: str
    files_indexed: int
    skipped: tuple[tuple[str, str], ...]   # (path, reason), sorted by path
    passages: tuple[Passage, ...]          # sorted by (path, line_start)
    threshold: float                       # calibrated confidence threshold τ
    params: RetrievalParams                # frozen constants, see "Retrieval"

@dataclass(frozen=True)
class Hit:
    rank: int                       # 1..5
    passage: Passage
    score: float                    # BM25F score (diagnostic only)
    url: str                        # https://github.com/{repo}/blob/{commit}/{path}?plain=1#L{start}-L{end}

@dataclass(frozen=True)
class RetrievalResult:
    question: str
    confident: bool
    hits: tuple[Hit, ...]           # EMPTY whenever confident is False
    coverage: float                 # confidence signal for the rank-1 candidate (0.0 if none)
    threshold: float
    reason: Literal["ok", "no-searchable-words", "no-passage-matched", "below-threshold"]
    generation_mode: Literal["deterministic"] = "deterministic"
```

`generation_mode` is here now because the `ai-agent-product` floor requires audit
events to carry it. When the drafting slice records an audit event per draft, the
retrieval step's mode is already on the result, so no model-free path gets
mislabelled later.

The `RetrievalResult` invariant is `confident == (reason == "ok") == (len(hits) > 0)`.
It is enforced in `__post_init__`, which raises `ValueError`. So "no confident
match" with passages attached cannot even be constructed.

## Ingest

### Fetch (the only network code in the product)

`ingest.fetch_archive(source, *, opener=None, max_bytes=50_000_000, timeout=60) -> bytes`

- URL: `https://github.com/{repo}/archive/{commit}.tar.gz`. This is GitHub's
  documented source-archive URL, and it answers with a 302 redirect to
  `codeload.github.com`. Only this URL is ever requested.
- **Redirects are host-restricted.** A custom `HTTPRedirectHandler` follows a
  redirect only when the target scheme is `https` and the host is `github.com` or
  `codeload.github.com`. Anything else raises `FetchError`. The default opener is
  `urllib.request.build_opener(<that handler>)`. Tests inject `opener`.
- **Size cap.** Reading stops with `FetchError` past `max_bytes`, so a wrong
  source cannot fill the disk or memory.
- No headers carry credentials. There is no token and no cookie, and the repo is
  public. The `User-Agent` is `aveto-support-ingest`.
- A non-200 final status, a timeout or a `URLError` raises `FetchError`, which
  maps to exit code 3.
- There is no retry loop and no cache. Every `ingest` run fetches once. A cache
  would be a second source of truth for "what the index was built from".

### Reading the archive (in memory, never extracted)

`ingest.read_markdown(archive: bytes, source: SourceConfig) -> tuple[list[DocFile], list[tuple[str, str]]]`

- `tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz")`. Members are read with
  `extractfile`. **Nothing is written to disk**, so tar path traversal cannot
  happen.
- **Commit check.** Every member's first path component must be
  `{repo_name}-{commit}` (GitHub's archive layout). If the archive's pax global
  header has a `comment` (git archive writes the commit SHA there), it must equal
  `commit`. Either mismatch raises `FetchError("archive does not match pinned
  commit")`.
- Only regular files (`member.isfile()`) are kept. Symlinks, hardlinks, devices
  and directories are ignored. Paths are the member name with the first component
  stripped. Any path containing `..` or starting with `/` is ignored.
- A file is kept when its path ends in `.md` (case-insensitive) and does not
  start with any `exclude` prefix.
- The file is decoded as strict UTF-8, with a leading BOM stripped. A decode
  failure adds `(path, "not utf-8")` to `skipped`; the file is not guessed at.
  `\r\n` and lone `\r` become `\n` **without changing the line count**, so line
  numbers still match the commit.
- The result is sorted by `path` (Python `str` order), whatever the tar member
  order was.

### Splitting into passages

`index.split_passages(path: str, text: str) -> list[Passage]`

A small CommonMark-subset heading scanner. It needs no markdown library.

1. Lines are `text.split("\n")`, numbered from 1.
2. **Fenced code.** A line matching `^ {0,3}(`{3,}|~{3,})` opens a fence. The
   fence closes at a later line starting (after up to 3 spaces) with the same
   character repeated at least as many times. Lines inside a fence are never
   headings. An unclosed fence runs to the end of the file.
3. **Front matter.** If line 1 is exactly `---`, everything up to and including
   the next line that is exactly `---` is never a heading. It stays part of the
   preamble text.
4. **ATX heading.** Outside a fence, a line matching `^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$`
   is a heading. The level is the number of `#`. The heading text is group 2
   with any trailing ` #…#` closing sequence removed and then stripped. `#tag`
   with no space is **not** a heading. Setext headings (underlined with `===` or
   `---`) are not recognised; that limitation is accepted and tested as such.
5. **Sections.** Each heading starts a passage that runs to the line before the
   next heading of **any** level. Lines before the first heading form a preamble
   passage with `heading=""`, `heading_path=()`, `line_start=1`.
6. **Heading trail.** A stack of `(level, text)`. On a heading of level L, pop
   every entry with level ≥ L, then push. `heading_path` is the stack's texts.
7. **Trim.** `line_end` is the last non-blank line of the section. A section
   whose body (every line after its heading line) is entirely blank is **dropped**,
   and so is a preamble with no non-blank lines. A heading with no body gives the
   searcher nothing but its title, and it still appears in the heading trail of
   its children. Dropped sections are counted in the ingest report
   (`empty sections dropped: n`).
8. `text` is the verbatim lines `line_start..line_end` joined with `"\n"`.

There is no size-based splitting. One heading section is one passage, however
long it is. That keeps "heading + line range" an exact, checkable citation.

### Orchestration

`ingest.run_ingest(config_path: Path, out_path: Path, *, opener=None) -> IngestReport`

The steps, in order: `load_source_config`, then `fetch_archive`, then
`read_markdown`, then `split_passages` for each file, then `search.calibrate`, then
`index.write_index`. If any step fails, the existing index file is left untouched,
because the write is atomic and happens last.

`IngestReport` holds repo, commit, files_indexed, passages, skipped (list),
empty_sections_dropped, threshold and the `sha256` of the written bytes.

## Index file format

**Location:** `index/docs-index.json` by default (`--out` overrides it). The whole
`index/` directory is **gitignored**. The index is not committed, because
committing passage text would amount to vendoring a docs snapshot, which the scope
review said not to do (`01-scope.md`, "The vendored-snapshot fallback is no
longer needed").

**Encoding.** The file is produced by `index.serialize_index(index) -> bytes`:

```python
json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=1,
           separators=(",", ": "), allow_nan=False).encode("utf-8") + b"\n"
```

Top-level shape (key order below is illustrative; `sort_keys` decides the real
order):

```json
{
 "schema": "aveto-support/index@1",
 "source": {"repo": "gpatwa/agentic-sdlc-playbook", "commit": "3a83b669…"},
 "params": {"tokenizer": "v1", "stopwords": "nltk-english-179", "stemmer": "harman-s",
            "k1": 1.2, "b": 0.75, "heading_weight": 2, "path_weight": 1,
            "top_k": 5, "per_file_cap": 2},
 "calibration": {"method": "cross-file-null-v1", "seed": 20260926, "queries": 2000,
                 "lengths": [2, 3, 4, 5], "quantile": 0.9, "threshold": 0.583333},
 "counts": {"files": 0, "passages": 0, "skipped": 0, "empty_sections_dropped": 0},
 "skipped": [{"path": "…", "reason": "not utf-8"}],
 "passages": [{"path": "README.md", "heading": "…", "heading_path": ["…"],
               "line_start": 1, "line_end": 12, "text": "…"}]
}
```

(The threshold value shown is a placeholder. The real value is whatever
calibration produces.)

**Determinism rules**, all needed for byte-identical output (Done-means 3):

- No timestamps, hostnames, absolute paths, durations or tool versions in the file.
- `passages` are sorted by `(path, line_start)` and `skipped` by `path`.
  Neither depends on tar order.
- Calibration uses `random.Random(20260926)`, a fixed integer seed. It draws
  from `passages` in the sorted order above, and from each passage's tokens as a
  **sorted** list. Only `choice`, `sample` and `randrange` are used, and they are
  deterministic on CPython 3.12 for a fixed integer seed.
- Floating-point sums run over **sorted** term lists. The stored `threshold` is
  `round(τ, 6)`, and `retrieve` compares against that stored value, so ingest
  and retrieve agree exactly.
- Atomic write: `tempfile.NamedTemporaryFile(dir=out.parent, delete=False)`, then
  `write`, then `flush` and `os.fsync`, then `os.replace(tmp, out)`. The parent
  directory is created if it is missing.

**Accepted residual.** `math.log` comes from the platform's libm, so a last-place
floating-point difference between macOS and Linux is possible. It could only show
up if a value rounded to 6 decimals sits exactly on a rounding boundary.
Byte-identity is **required** for re-runs on the same machine and Python, which is
Done-means 3. Cross-platform identity is expected but not guaranteed, and the CI
slice compares within a single runner.

**Loading.** `index.load_index(path) -> Index` raises `IndexFormatError` if the
file is missing, is not JSON, has the wrong `schema`, or has `params` that differ
from the code's `RetrievalParams`. The last case produces the message "index was
built with different retrieval parameters; re-run ingest". That makes it
impossible to score or search with an index the current code did not produce.

## Retrieval

> **SUPERSEDED IN PART by "Retrieval — variant v2" below (retry 1, 2026-09-29).**
> This v1 text is kept as the record of what eval run 1 measured. v2 replaces
> the stemmer, adds file-level evidence to the ranking, and replaces the
> coverage signal with corroboration. The tokenizer's casefold, split and
> stopwords, the passage bag, k1, b, the weights, top_k, per_file_cap, the
> null-query generator, the seed, count, lengths and quantile, and the
> "no hits when not confident" rule all carry over unchanged.

Everything in this section is **fixed now, before any code runs against the eval
set**. The values are textbook defaults or follow from general principle. None was
chosen by looking at a retrieval result. See "Overfitting protocol".

### Text normalisation (`search.tokenize(text) -> list[str]`, `params.tokenizer = "v1"`)

1. `text.casefold()`.
2. `re.findall(r"[^\W_]+", …)`, which keeps Unicode letters and digits and splits
   on everything else. Markdown punctuation, `/`, `-`, `_` and `.` all separate
   tokens.
3. Drop stopwords. The list is **the NLTK English stopword list (179 words),
   reproduced as a constant**, keeping the entries that are purely alphanumeric
   (apostrophe forms like `don't` are already split into `don` + `t`, both of which
   are on the list). `nltk` is not a dependency. This is a fixed, published list;
   the Implementation stage adds nothing to it and removes nothing from it.
4. Stem with **Harman's S-stemmer** (Harman 1991, "How effective is suffixing?").
   Apply the first rule that matches, and only when the word is longer than 3
   characters:
   - ends in `ies`, but not `eies` or `aies`: replace `ies` with `y`
   - ends in `es`, but not `aes`, `ees` or `oes`: replace `es` with `e`
   - ends in `s`, but not `us` or `ss`: drop the `s`

   This is a deliberately weak stemmer. It only folds plurals, so it seldom merges
   unrelated words. Porter-style stemming lost because it conflates more
   aggressively, which works against the hard negatives.

There is **no synonym table and no spelling map.** Either would have to come from
somewhere, and the only question text in the repo is the eval set.

### Passage representation (BM25F-lite)

Each passage is scored as one "bag" of tokens:

- **body**: `tokenize` of the passage lines *after* the heading line (for a
  preamble, all of its lines)
- **heading trail**: `tokenize(" ".join(heading_path))`, repeated
  `heading_weight = 2` times
- **file path**: `tokenize(path without its extension)`, repeated
  `path_weight = 1` time. For example, `agents/on-call-engineer.md` becomes
  `agent, on, call, engineer` after stopwords and stemming.

A section's title and its file's name describe what the section is about. Counting
them in the passage is the standard field-weighting argument, and a 2× title
weight is the conventional starting point. Repeating tokens is the simplest
faithful approximation of BM25F.

### Ranking (`Searcher`)

`search.Searcher(index)` builds an inverted index (term → sorted list of
(passage_id, tf)) plus `df`, bag lengths and `avgdl` once, when it is constructed.

- Query terms are the **unique** tokens of the question, sorted.
- `idf(t) = ln(1 + (N − df(t) + 0.5) / (df(t) + 0.5))`, the non-negative
  Lucene form, where N is the number of passages. A term not in the corpus has
  `df = 0`, which gives it the largest idf.
- `score(p) = Σ_t idf(t) · tf·(k1+1) / (tf + k1·(1 − b + b·dl/avgdl))`, with
  **k1 = 1.2 and b = 0.75** (Robertson's defaults).
- Only passages with `score > 0` are candidates. They are sorted by
  `(−score, path, line_start)`, which gives a total, deterministic order.
- **Per-file cap.** Walk the sorted candidates and keep a passage unless its file
  already has `per_file_cap = 2` kept passages. Stop at `top_k = 5`. This shows
  the reader more distinct sources. It is set once here and is not a tuning
  parameter.

### The confidence signal: term coverage of the top passage

`coverage(q, p) = Σ_{t ∈ q, t ∈ bag(p)} idf(t) / Σ_{t ∈ q} idf(t)`

This is the fraction of the question's *specific* vocabulary, weighted by idf,
that the top-ranked passage actually contains. Sums run over sorted `q`. Terms
that are missing from the corpus stay in the denominator at their maximal idf.
That is deliberate, and it is the "grounded or silent" stance in arithmetic: if
the most specific thing a person asked about appears nowhere in the docs, the docs
do not answer the question, however well the generic words match.

Why coverage and not the raw BM25 score: BM25 scores are unbounded and depend on
the question (longer questions score higher), so no single cut-off means the same
thing for two questions. Coverage is bounded to [0, 1] and comparable across
questions. That is what makes a corpus-calibrated threshold possible.

### The no-confident-match rule (`search.retrieve(searcher, question) -> RetrievalResult`)

Rules are checked in order, and the first one that fires decides the result:

1. The question has no content tokens (empty, or only stopwords): `reason =
   "no-searchable-words"`, no hits.
2. No passage scores above 0: `reason = "no-passage-matched"`, no hits.
3. `coverage(q, rank-1 passage) < index.threshold`: `reason = "below-threshold"`,
   **no hits**. The candidates are dropped, not returned as "low confidence".
   This is Done-means 5: never the least-bad passages.
4. Otherwise `confident = True`, `reason = "ok"`, and the hits are the capped top
   5 in rank order.

Once the set passes, ranks 2–5 are **not** individually re-gated. Deciding
whether weaker supporting passages should reach a drafter belongs to the drafting
slice, and adding a second threshold here would be a second knob.

### The threshold τ is calibrated from the corpus, not from the eval set

`search.calibrate(passages: Sequence[Passage], params) -> float` runs inside
`ingest`, and its result is stored in the index. **Method `cross-file-null-v1`:**

1. `eligible_files` are the sorted paths that have at least one passage with a
   non-empty body token set. If there are **fewer than 5**, calibration cannot
   say anything useful: return `τ = 1.0` and have ingest print a warning. That
   fails closed, because only a passage containing every query term counts.
2. `rng = random.Random(20260926)`. Repeat **2000** times:
   - `L = rng.choice([2, 3, 4, 5])`. That is the typical content-word count of a
     support question after stopword removal. It is fixed a priori and was not
     measured on the eval set.
   - `files = rng.sample(eligible_files, L)`. The files are distinct.
   - For each file, take `p = rng.choice(that file's eligible passages)` (in
     `line_start` order), then `t = rng.choice(sorted(set(body tokens of p)))`.
   - Take the null query `q = sorted(set(those tokens))`. Its coverage `c` is the
     top-1 coverage from the same `Searcher` code path, or 0.0 if nothing
     matches.
3. `τ` is the **nearest-rank 90th percentile** of the 2000 `c` values:
   `sorted(c)[ceil(0.9 · 2000) − 1]`. The stored value is `round(τ, 6)`.

**What the null model represents.** Each null query is made of real words from
the docs, each used in its real context, but taken from files that have nothing
to do with each other. So every word appears in the docs, yet no single passage
answers the combination. That is the lexical signature of the eval set's hard
negatives ("price", "Windows": keywords present in an unrelated sense), built from
the corpus alone. Real unanswerable questions often also contain words that
appear nowhere in the docs, which lowers their coverage further. That makes the
null a conservative stand-in, because it models the *hardest* negatives.

**Why the 90th percentile.** The owner's stated tolerance is that up to 20% of
unanswerable questions may slip through (the ≥80% bar). The synthetic null is
held to **half** of that, 10%. Hard negatives are the worst case, so the
calibration should be stricter than the tolerance it serves. The value follows
from the owner's pre-stated bar. It is not a knob.

**Why this is better than a constant.** A threshold hand-picked for Aveto's docs
would not carry over to someone else's docs, and this repo is a template. A
corpus-calibrated τ is recomputed by every `ingest`, so it adjusts when someone
points `docs-source.toml` at their own docs. It is deterministic (fixed seed), so
it does not break byte-identity. It is also inspectable: the `calibration` block
in the index records the method, seed, count, lengths, quantile and result.

### Retrieve output (text, stdout)

Confident:

```
Sources for: <question>
Docs: gpatwa/agentic-sdlc-playbook @ 3a83b669a8b53dfdff869a1bbe361bdb156e3a13
Confidence: 0.742 (threshold 0.583)  mode: deterministic, no model

1. docs/GETTING_STARTED.md  lines 12-40
   Heading: Getting started > Add it to an existing repo
   https://github.com/gpatwa/agentic-sdlc-playbook/blob/3a83b669…/docs/GETTING_STARTED.md?plain=1#L12-L40
   | <up to the first 3 non-blank body lines, verbatim, each cut at 160 chars>
2. …

These are sources, not an answer.
```

Not confident. The first line is exactly the literal below, so scripts and the
eval can rely on it:

```
no confident match
Docs: gpatwa/agentic-sdlc-playbook @ 3a83b669a8b53dfdff869a1bbe361bdb156e3a13
Reason: below-threshold (best coverage 0.412, threshold 0.583)
```

No path, heading or excerpt of a rejected candidate is printed. Showing "the
closest thing we found" is exactly the least-bad-passage behaviour Done-means 5
forbids. The numbers are shown so the owner can see *why* nothing was confident.

The heading line for a preamble passage reads `Heading: (top of file)`. Excerpt
lines are the passage's own text with no edits beyond truncation. `…` marks a
cut-off line.

## Retrieval — variant v2 (retry 1; pre-registered 2026-09-29, before it is run)

This is retry 1 of 2, per `FAILURE_LOOP.md` and `ESCALATION-1.md` "Resolution"
(owner option A). It is written before any code implements it and before any
eval run of it. Every value below is fixed here. Implementation re-implements
this section and changes nothing else.

### Disclosure: what the Architect has now seen

- I have read `runs/docs-retrieval/eval-run-1.txt` in full. That includes which
  questions missed (22 of 24 answerable were withheld; a02 and a24 returned
  confident but wrong sets), the expected files for each, the per-question
  coverage values (answerable 0.26–0.82, unanswerable 0.26–0.60) and the
  aggregate: ungated recall@5 of 14/24, and τ = 1.000.
- I read the implemented `aveto_support/search.py` and `index.py` to confirm
  they match the v1 spec. They do.
- I did **not** look up any missed question in the corpus, inspect the index for
  specific files, or simulate v2 on any eval question. The changes below are
  argued from retrieval principles and from how this corpus is built: 126 files,
  910 heading passages, and one shared process vocabulary.
- **The original 30 questions are no longer unseen evidence** (Overfitting
  protocol §7). A v2 score on them is a measurement *after* looking. The owner's
  fresh held-out set, which the Architect has not seen, will not look for and
  cannot see, is the evidence that counts (see "What a good result on a fresh
  set looks like").

### Diagnosis: why τ came out at 1.000

**The flaw is in the coverage formula, and calibration exposed it.** The
calibration code did what v1 specified.

1. **Coverage is presence-only and saturates.** It is a ratio of matched to
   total idf mass, so *any* query whose words all appear in one passage scores
   exactly 1.0, however common those words are. This corpus is one team's
   process documentation, so words like agent, stage, slice, run, approval and
   gate recur across most files. Null queries drew words uniformly from each
   passage's vocabulary, so many of them were made of such shared words, and
   some passage contained all of them. More than 10% of the 2000 nulls sat at
   the 1.0 ceiling, so the 90th percentile *was* the ceiling. A threshold at the
   ceiling carries no information: only a perfect match passes.
2. **The signal's main ingredient could not be calibrated.** v1's strongest
   abstention mechanism was that words absent from the docs keep maximal idf in
   the denominator. The null queries are built from words *in* the docs, so they
   never contain an absent word, and calibration never saw the mechanism it was
   meant to set a threshold for. Signal and calibration were mismatched by
   construction.
3. **The absent-word penalty does not separate the classes.** People phrasing
   answerable questions use everyday words the docs do not use, so the penalty
   lands on answerable questions as heavily as on unanswerable ones. That is
   visible in eval run 1's overlapping coverage ranges (disclosed above). It is
   also the general, well-known vocabulary-mismatch problem of lexical
   retrieval.

Fixing only the null generator (for example drawing only rare words) would
lower τ. But it would set that lower τ on a signal whose two classes overlap, so
it would trade withheld answerable questions for leaked unanswerable ones
without separating them. That is why v2 changes the **signal** and keeps the
null generator as it was.

**Ranking is the binding constraint, and it has two general causes in this
corpus.** An ungated recall of 14/24 means ranking alone cannot pass the bar.

- **Passages are small and topics are spread across a file.** 910 passages from
  126 files is about 7 heading sections per file. A question about a file's
  topic ("how does X work") shares words with the file as a whole, spread
  across several sections, while some unrelated short section may contain one
  rare query word. Passage-only BM25, with length normalisation favouring short
  sections, rewards the latter. In IR terms this is the case for combining
  passage-level and document-level evidence (Callan, SIGIR 1994, "Passage-level
  evidence in document retrieval").
- **Plural-only stemming leaves most morphology unmatched.** Users ask with
  verbs and inflections (failing, stopped, installed, writing), while docs
  often use other forms of the same word (failure, stop, install, written).
  Harman's S-stemmer folds only plurals. Stronger stemming is the standard
  lexical answer to inflectional mismatch for short queries. v1 rejected it to
  protect hard negatives, but eval run 1 shows abstention was not where the
  slice failed.

### Change 1: stemmer `porter-1980` (replaces `harman-s`)

`tokenize` keeps v1's casefold, split and NLTK stopwords (removed **before**
stemming). It then applies **Porter's original algorithm** (M.F. Porter, "An
algorithm for suffix stripping", *Program* 14(3), 1980): steps 1a, 1b (with its
cleanup), 1c, 2, 3, 4, 5a and 5b exactly as published, with the published
measure *m* and the conditions `*S`, `*v*`, `*d` and `*o`. This is **not** NLTK's
or Snowball's variant. It is written in plain Python inside `search.py`, in
about 120 lines, with no dependency. Tokens of length ≤ 2 are not stemmed.

Why Porter rather than Porter2 (Snowball English): the 1980 algorithm is frozen
and specified in one short paper, so "implemented as published" can be checked.
Porter2 is still maintained and has changed over time.

### Change 2: ranking `ranking-v2` (file-level evidence added to passage BM25)

For each passage p in file f, and query terms q (unique, sorted):

- **P(p)** is v1's passage BM25 over the passage bag: body, plus the heading
  trail ×2, plus the path ×1, with passage-level idf over N = passage count,
  k1 = 1.2, b = 0.75. It is unchanged apart from the stemmer.
- **F(f)** is BM25 of the same query over **file bags**, with idf computed over
  the file count and the same k1 and b. Length normalisation uses file lengths
  and the average file length. A file bag is the tokens of every indexed
  passage's `text` in that file (heading lines included once, as they appear in
  the text) plus the path tokens × `path_weight` (1), added **once per file**.
- **Candidates** are passages with P(p) > 0. A passage that shares no word with
  the question is never returned, however well its file matches. This keeps
  INV-4: a returned passage always contains question evidence.
- **Combined score** `s(p) = λ · P(p)/P* + (1 − λ) · F(f)/F*`, where P* is the
  largest P and F* the largest F among candidates and their files for this
  query, and **λ = 0.5**. Dividing by the per-query maximum puts both terms on
  [0, 1]. Equal weight is the neutral prior when neither level is known to
  dominate. It was not searched for.
- Order by `(−s, path, line_start)`, then apply v1's per-file cap of 2 and
  top_k of 5, both unchanged.

The effect: a section ranks high when it matches the question itself *and*
sits in a file that is about the question. The per-file cap still makes the top
5 span at least 3 files.

### Change 3: confidence `corroboration-v1` (replaces coverage)

For the rank-1 passage p (by combined score), with **passage-level** idf and
M = the set of query terms present in p's bag:

`corroboration(q, p) = Σ_{t∈M} idf(t) − max_{t∈M} idf(t)`, and it is 0 when M
is empty. Sums run over sorted M.

The principle: a single shared word is what a coincidence looks like, whether it
is a hard negative (a keyword used in an unrelated sense), a random null, or
one rare word in an unrelated section. Evidence that a passage is *about* the
question is **several** of the question's words meeting in one passage,
weighted by how specific they are. Corroboration measures exactly the evidence
*beyond* the single strongest word.

Properties v1 lacked:

- **It does not saturate.** It has no denominator and no ceiling. More, and
  more specific, co-occurring words mean more evidence, so a percentile of null
  values cannot pin to a ceiling.
- **It is neutral to absent words.** A word that appears nowhere in the docs
  adds 0 and subtracts 0. The null queries contain only in-corpus words, so the
  signal and its calibration now measure the same thing. v1's mismatch is gone.
- **It still refuses a lone keyword.** A question whose only link to a passage
  is one word gets 0, which is below any positive τ.

### Calibration: `cross-file-null-v2`

The generator is **identical** to v1: seed 20260926, 2000 queries, lengths
{2, 3, 4, 5}, distinct files, one word drawn uniformly from each passage's
sorted distinct body tokens, and the **90th percentile**, nearest-rank. Only the
measured value changes: each null query's value is the corroboration of its
rank-1 passage under ranking-v2 (0.0 if nothing matches). τ is `round(p90, 6)`,
a non-negative number with no fixed upper bound. The quantile keeps v1's
rationale (half the owner's tolerated 20%). Changing it now would be turning a
knob after seeing the test.

- **Small corpus** (fewer than 5 eligible files): τ = `1000000.0`, which no
  question reaches. It still fails closed, and JSON has no `inf`.
- **Degenerate calibration**: if the p90 value is 0.0 (at least 90% of nulls
  have no corroboration at all), τ is the smallest positive null value, or
  1000000.0 if there is none. Otherwise every query with any corroboration
  would pass, and "confident" must mean strictly more than a lone keyword. The
  rule is fixed here and is generic to any corpus.

The rule is `confident ⇔ corroboration(q, rank-1) ≥ τ`. v1's ordered checks
still apply: no-searchable-words, then no-passage-matched, then below-threshold.
A result that is not confident still has **no hits** (INV-4 unchanged).

### Deltas to other sections (v2)

- **Index file format.** Bump `schema` to `"aveto-support/index@2"`, and change
  `params` to `{"tokenizer": "v2", "stopwords": "nltk-english-179", "stemmer":
  "porter-1980", "ranking": "ranking-v2", "file_lambda": 0.5, "k1": 1.2, "b":
  0.75, "heading_weight": 2, "path_weight": 1, "top_k": 5, "per_file_cap": 2,
  "confidence": "corroboration-v1"}` and `calibration.method` to
  `"cross-file-null-v2"`. `load_index` rejects v1 indexes (schema mismatch). All
  determinism rules are unchanged, and file bags are built over files sorted by
  path.
- **Data model.** Rename `RetrievalResult.coverage` to `confidence` (a
  non-negative float, the corroboration of the rank-1 candidate). `Hit.score` is
  the combined score s(p). `RetrievalParams` gains `ranking`, `file_lambda` and
  `confidence`.
- **Output.** Retrieve prints `Confidence: <corroboration, 2 dp> (threshold
  <τ, 2 dp>)`. The not-confident reason reads `Reason: below-threshold (best
  corroboration 1.73, threshold 2.41)`. The eval per-question lines say
  `corroboration` where v1 said `coverage`. The header line prints the threshold
  to 3 dp. The literal first line `no confident match`, the summary lines, the
  exit codes and the ingest report layout are unchanged. The ingest threshold
  line reads `(cross-file-null-v2, p90 of 2000 null queries, seed 20260926)`.
- **Service surface.** `Searcher.coverage` is replaced by
  `Searcher.corroboration(terms, passage) -> float`. `Searcher.rank` returns
  candidates ordered by the combined score. `search.calibrate` returns a value
  ≥ 0 (not bounded to [0, 1]). No new public functions.
- **Evidence.** The first v2 run is committed verbatim as
  `runs/docs-retrieval/eval-run-2.txt` before any further change (Overfitting
  protocol §3).

### General ideas considered and rejected for v2

| Idea | Why not |
|------|---------|
| Synonym, spelling or paraphrase tables | Forbidden (§5), and it cannot generalise: any table would be written from the only questions in the repo |
| Pseudo-relevance feedback (RM3/Rocchio query expansion) | It amplifies first-pass errors. With about 58% first-pass recall, expansion would often be built from the wrong files. It also adds three parameters (feedback depth, term count, weight) with no principled values for this corpus |
| Lowering the quantile or hand-setting τ | That turns a knob after seeing the test, and it cannot help, because ranking is the binding constraint |
| Per-file cap of 1 (five distinct files) | It would be chosen because the eval scores files, not because it serves a reader. Keeping v1's cap of 2 |
| Raising heading or path weights | There is no new principled value. Any choice would be a guess steered by run 1 |
| Merging small sections or a minimum passage size | It coarsens citations. File-level evidence addresses the same small-passage problem without changing provenance |
| Corpus-frequency stoplist (drop words in >X% of passages) | idf already down-weights them, and X would be a new knob |
| Proximity or phrase scoring | Little gain for short questions, and more parameters |
| Keeping coverage, fixing only the null generator | The diagnosis above shows the classes overlap on coverage, so a better τ on a non-separating signal does not help |
| Embeddings (local model or API) | Out of scope: a new dependency or a model call. That is the owner's decision if v2 misses (see "Finding") |

### Prediction, recorded before the run

- **Ungated recall@5 on the original 30: 17/24 expected, with an honest range of
  15–20/24.** The chance of it reaching ≥ 20 is about 25%. Both changes attack
  real, general causes (small passages, and morphology), but neither touches
  the dominant one: questions phrased in words the docs never use.
- **Gated result.** Answerable will be at or below the ungated number, perhaps
  1–4 lower, because corroboration withholds questions whose only link to the
  right passage is one word. Unanswerable is expected at 4–6 of 6. Losing the
  absent-word penalty removes v1's strongest guard, and some unanswerable
  questions will contain two common in-corpus words together.
- **Probability that v2 passes both bars on the original 30: about 15%.**

### Finding for the owner (stated before the run, as the escalation rule asks)

**Plain lexical retrieval is unlikely to reach 80% on questions phrased the way
this eval set phrases them.** The eval set was deliberately written in user
language, not the docs' language. That is the right test, and it is exactly the
vocabulary-mismatch case lexical methods are known to handle poorly. v2 fixes
two general weaknesses of v1 and a real calibration defect. It is still bounded
by words shared between question and doc.

If v2 misses, I recommend **not** spending retry 2 on a third lexical variant.
Each further lexical change is fitted more closely to these 30 questions and
tells the owner less. The decision the owner then faces is the one in
`ESCALATION-1.md` option B: record the lexical ceiling, and decide separately
whether to add embeddings (a new dependency or a model call, under rules 5
and 6).

### What a good result on the fresh held-out set looks like

The owner's fresh set is the only unbiased measurement of v2.

- **Generalises:** the fresh-set ungated recall@5 and both gated rates fall
  within about 10 percentage points of v2's score on the original 30, and the
  gated rates are ≥ 80% answerable and ≥ 80% unanswerable.
- **Overfitted, or does not generalise:** the fresh set scores more than 15
  points below the original 30. Either v2 was shaped by run 1 more than intended,
  or the method holds only for questions close to the docs' wording.
- **Sample-size caution:** with about 20 answerable questions, one question is 5
  points, and a 95% interval around 80% is roughly ±18 points. A pass on a
  20-question fresh set is weak evidence, and a single-question difference is
  noise. For a firmer read, the fresh set should use the same rules as
  `evals/retrieval.toml` (user phrasing, at least 5 unanswerable questions, and
  at least 2 hard negatives), and its TOML format, including `pinned_commit =
  "3a83b669a8b53dfdff869a1bbe361bdb156e3a13"`, which the eval pre-flight
  requires. QA runs it with the same `eval --eval-file <path>` command, which
  needs no code change.

## Retrieval — variant embed-v3 (SPEC ONLY: owner chose to pursue it in this slice; NO gated approval recorded; not implemented)

> **Update 2026-09-29: approvals granted.**
> - APPROVAL_RECORD-2, -3 and -4 (rules 5, 5 and 4) were each given separately
>   by the owner.
> - The INV-4 and INV-5 text from §3 has been applied byte for byte to
>   `.agentic/SAFETY_INVARIANTS.md` by the Orchestrator.
> - `docs/adr/0003-hybrid-embedding-retrieval.md` is written, with status
>   accepted and implementation pending.
> - The off-topic list `evals/calibration-offtopic.toml` is frozen at commit
>   `fa3673ad…`, with sha256
>   `9045189567b083c83c02336a4f70990c8a8e3ce3e49d5917642fbad6e293627c`.
>   `docs-source.toml` pins that value as `offtopic_sha256`.
>
> The "SPEC ONLY / no approval" wording below is historical.

> **Status (updated 2026-09-29).** The owner chose "Pursue embed-v3 in this
> slice". **That choice grants no gated approval.** Nothing in this section may
> be built, installed or downloaded, and `.agentic/SAFETY_INVARIANTS.md` may not
> change, until each request in §7 has its own recorded approval. Until then no
> dependency, weights file, config value or code exists for embed-v3. Variant v2
> stays in the spec unchanged as the fallback.
>
> Written 2026-09-29, after `eval-run-1.txt` (disclosed in v2) and before any
> run of v2 or embed-v3.
>
> **Freeze-first ordering, binding on whichever variant is built:**
> 1. Implementation builds the approved variant and runs every offline and
>    network-marked test, **then STOPS**. It runs no `eval`, on any set.
> 2. The frozen commit SHA of that implementation is recorded in STATE.md.
> 3. Only then does the owner commit the fresh held-out set.
> 4. QA scores it **once**, with
>    `uv run python -m aveto_support eval --eval-file <fresh set>`, against the
>    index built at the frozen SHA, with **no code change between** the freeze and
>    the score. The fresh set gates the ≥80% bar.
> 5. `evals/retrieval.toml` is a **dev-set diagnostic**, scored at the same
>    frozen SHA and reported but not gating.
>
> The Architect has not seen the fresh set and will not look for it.
>
> **How the facts below were established.** Every fact carries one of these
> labels:
>
> - **VERIFIED:** re-checked by the Orchestrator on 2026-09-29 against Hugging
>   Face's read-only metadata API and one HEAD request. No file was downloaded.
> - **REPORTED:** stated by the playbook session and **not independently
>   verified**.
> - **UNVERIFIED:** checked only at implementation, under approval, by a test
>   that fails loudly.
> - **ESTIMATE.**
>
> The benchmark figures are from the published model cards and the MTEB
> leaderboard, from memory, and are used only to rank candidates.

### 1. Design

**Recommended model: `BAAI/bge-small-en-v1.5`.** A 33.4M-parameter BERT-small
encoder: 12 layers, hidden size 384, 384-dimensional embeddings, 512-token input
limit, CLS pooling with L2 normalisation, and MIT licence. It was chosen on
general grounds:

- **Retrieval quality for its size.** Its published MTEB retrieval (BEIR)
  average nDCG@10 is about 51.7, among the best of the ~30M-parameter English
  encoders.
- **Size and speed.** Its size (~134 MB fp32) runs on CPU without a GPU.
- **Licence.** Permissive (MIT).
- **Plain architecture.** It is a standard BERT, so it needs no
  `trust_remote_code` and runs as a plain ONNX graph.
- **Revision pinning.** It is widely used, and the Hugging Face repo supports
  pinning a revision by full commit SHA.

No eval question was used to choose it.

**Alternative: `sentence-transformers/all-MiniLM-L6-v2`.** 22.7M parameters, 6
layers, 384 dimensions, Apache-2.0. It is smaller (~90 MB) and about twice as
fast on CPU, and it is the most widely deployed small encoder. It is clearly
weaker at retrieval (MTEB retrieval about 41.9) and was trained on inputs of 128
to 256 tokens, which is short for heading sections. Pick it only if the owner
weighs footprint and speed above quality.

Rejected candidates:

| Candidate | Why not |
|-----------|---------|
| `nomic-embed-text-v1.5` | Needs `trust_remote_code`, which runs repository Python at load. That is a supply-chain risk |
| `intfloat/e5-small-v2`, `thenlper/gte-small`, `Snowflake/snowflake-arctic-embed-s` | Comparable size. bge-small is as good or better on published retrieval, and choosing between near-ties is not worth an extra comparison |
| model2vec static embeddings | numpy only and very fast, but much weaker retrieval |
| Any embeddings **API** (Voyage, OpenAI, Cohere and others) | Question and doc text would leave the machine. That fires rule 6, needs a key, and contradicts "no API key in this slice" |

**Runtime: ONNX Runtime + numpy. Not PyTorch or sentence-transformers.**

- The model runs from the repo's own ONNX export, `onnx/model.onnx`, with
  `onnxruntime` on the CPU execution provider.
  - **VERIFIED:** the file exists at revision
    `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, is published by BAAI (not a
    third-party export), and is 133,093,490 bytes.
  - **UNVERIFIED until the approved download:** the graph's input names
    (`input_ids`, `attention_mask`, `token_type_ids`) and its output (`[1, seq,
    384]` hidden states, with `[CLS]` at position 0). The test
    `test_onnx_graph_signature` asserts the exact input-name set and the output
    shape on the cached model. It fails loudly on any mismatch, so Implementation
    stops and hands back rather than adapting silently.
- Tokenization is **plain-Python BERT WordPiece** in about 100 lines. It reads
  `vocab.txt` from the same pinned revision and uses the published BERT basic
  tokenizer: clean control characters, split CJK characters, lowercase, strip
  accents, split on punctuation, then greedy longest-match WordPiece with `##`
  continuations and `[UNK]`. So the `tokenizers` package (which pulls in
  `huggingface_hub` and its tree) is not a runtime dependency.
- The download uses stdlib `urllib` with a host allowlist, the same pattern as
  the GitHub fetch. There is no `huggingface_hub`.
- PyTorch lost because a CPU wheel is roughly 200 MB, and the default PyPI
  Linux wheel pulls in CUDA libraries of several GB.
- A pure-numpy forward pass over safetensors was also considered. It would
  shrink the dependency set to numpy alone. It lost because re-implementing
  BERT (GELU variant, LayerNorm epsilon, position ids) is a correctness risk,
  and the ONNX graph *is* the reference computation.
- No third-party ONNX export is needed, since the BAAI repo carries its own
  (VERIFIED above).
- **Downloaded files: exactly two.** `onnx/model.onnx` and `vocab.txt`.
  `config.json` and `tokenizer_config.json` are **not** downloaded. The
  tokenizer settings they carry (REPORTED: `BertTokenizer`,
  `do_lower_case: true`, `tokenize_chinese_chars: true`, `strip_accents: null`,
  `model_max_length: 512`) are pinned in code instead. With `strip_accents: null`
  and lowercasing on, BERT strips accents. The golden-token fixture (below)
  checks that behaviour against the reference, so the settings are verified by
  output, not by reading a config file. `model.safetensors` (VERIFIED 133,466,304
  bytes) is never downloaded.

**How text is embedded:**

- **Passage input:** `" > ".join(heading_path) + "\n" + body` (the verbatim
  passage text after the heading line), with no prefix. It is truncated to 512
  WordPiece tokens including `[CLS]` and `[SEP]`. The ingest report adds
  `passages truncated for embedding: n`, and the dropped tail stays searchable
  by BM25.
- **Query input:** bge v1.5's published retrieval instruction, `"Represent this
  sentence for searching relevant passages: "`, followed by the question.
- **Vector:** the output at `[CLS]` (the model's pooling), then L2-normalised,
  then **quantised to int8**: `q = clamp(round(x · 127), −127, 127)`. Similarity
  is the dot product of dequantised vectors (`q / 127`), a cosine up to
  quantisation error. int8 quantisation costs about 1% of retrieval quality in
  published results, and it makes the index smaller and more stable (see
  Determinism).
- **Batch size 1**, so padding never changes a result.

**Tokenizer correctness: a golden-token fixture instead of a dependency.**

A hand-written WordPiece that differs from the reference by even one rule (how
accents are stripped, how CJK is split, which characters count as control
characters) silently produces different vectors. So its output is checked
against ids produced by the reference tokenizer:

- **Fixture:** `tests/fixtures/wordpiece_golden.json`. This is a **new file**,
  flagged in §5.
- **Fixed strings, pre-registered here** (none taken from any eval set):
  1. `""`, the empty string, expected to give `[CLS] [SEP]`
  2. `"Hello, world!"`
  3. `"Café naïve résumé Ångström"`, for accent stripping
  4. `"日本語のテキストと中文"`, for CJK splitting
  5. `"don't stop-believing: e.g. 3.14 (v2) [x] {y} <z>"`, for punctuation and
     digits
  6. `"tab\there\nnewline\u0007bell​zero-width"`, for control and format
     characters
  7. `"unaffable electroencephalography antidisestablishmentarianism"`, for `##`
     continuations
  8. `"🙂 ☃ ∑ emoji and symbols"`, for `[UNK]` handling
  9. `"## Install `install.mjs` → run /agentic-slice --help"`, for markdown and
     the arrow
  10. `"word " * 600`, which must truncate to 512 ids including `[CLS]` and
      `[SEP]`
  11. The query prefix plus `"How do I resume a run?"`, the exact form queries
      take
- For each string the fixture records the full id list with `[CLS]`/`[SEP]` and
  truncation at 512.
- **Who produces it: QA (qa-evidence), not the engineer who writes the
  tokenizer,** so the builder never authors the answer key. QA does it once,
  after Requests A and B are approved, in a **throwaway environment outside the
  repo**, so no dependency enters `pyproject.toml` or `uv.lock`. It runs
  `uv run --no-project --with tokenizers==<exact version> python <snippet>`.
  The snippet builds `BertWordPieceTokenizer` from the pinned `vocab.txt` with
  `lowercase=True`, `strip_accents=None`, `handle_chinese_chars=True`,
  `clean_text=True`, and truncation to 512.
- **How it is recorded:** the fixture has a `generated_by` header holding the
  role and person, the UTC date, the `tokenizers` version, the sha256 of the
  `vocab.txt` it used (which must equal the pin), the exact command, and the
  full snippet text. QA commits it in its own commit **before** the engineer's
  tokenizer is tested against it. The engineer does not edit it.
- `tokenizers` is therefore **not a project dependency at all**, not even
  dev-only. v3's earlier optional Request D is **withdrawn**.
- Test: `test_wordpiece_matches_golden`. It needs no network, but it does need
  the cached, hash-verified `vocab.txt`.
  - It carries a new pytest marker, `model`, meaning "needs the cached model
    files; no network". `addopts` becomes `-m 'not network and not model'`.
  - QA and CI run it with `uv run pytest -m model` after `ingest`.
  - When selected, it **fails, never skips**, if the files are missing.
  - `test_onnx_graph_signature` uses the same marker.

**Ranking `hybrid-v3`:** a hybrid that keeps BM25.

- **Lexical list:** v2's `ranking-v2` combined score, unchanged, over its
  candidates (passages with P > 0).
- **Dense list:** every passage ordered by dense similarity, ties broken by
  `(path, line_start)`.
- **Fusion:** Reciprocal Rank Fusion (Cormack, Clarke and Büttcher, SIGIR 2009),
  `rrf(p) = Σ_lists 1 / (60 + rank_list(p))`, over the union of the **top 100**
  of each list. k = 60 is the published default. RRF needs no score
  normalisation and has one parameter.
- Order by `(−rrf, path, line_start)`, then per-file cap 2 and top_k 5, both
  unchanged.
- Why hybrid rather than dense-only: dense retrieval handles paraphrase, which
  is v1/v2's failure mode. BM25 handles exact terms (file names, commands like
  `install.mjs`, flags). Hybrids reliably beat either alone in published
  retrieval results. BM25 also stays as the fully deterministic fallback path.

**Confidence `dense-null-v3`, the "no confident match" rule:**

- The signal is the **dense similarity of the single best passage in the
  corpus** (dense rank 1), not the fused rank 1. The question it answers is
  "does anything in the docs mean roughly this?", which is closer to "the docs
  answer this" than word overlap is.
- **Calibration, part 1 (word salads):** reuses v1/v2's cross-file null
  generator unchanged: seed 20260926, 2000 queries, lengths {2, 3, 4, 5}, and
  one word from a passage in each of L distinct files. The words are joined with
  spaces and given the query prefix. τ_salad is the nearest-rank p90 of their
  dense-rank-1 similarity. The sentinels are unchanged (fewer than 5 files gives
  τ = 1000000.0).
- **Calibration, part 2 (fluent off-topic questions): the fix for the weak
  point below.** This uses no eval data.
  - **What:** a fixed list of **at least 50** fluent, natural-language questions
    that a user of a developer tool might plausibly ask, but that the configured
    docs do **not** answer. They should be on-domain in tone (platforms,
    pricing, accounts, integrations, IDEs, hosting, languages) and off-topic in
    substance.
  - **Where:** `evals/calibration-offtopic.toml`, a new file flagged in §5. It is
    TOML, with `pinned_commit` and `[[question]]` entries carrying `id` and
    `question`.
  - **Who writes it: QA or the owner.** Never the Architect and never the
    engineer. The author checks each question is unanswered at the pinned
    commit. Questions must not be copied from, or paraphrase,
    `evals/retrieval.toml` or the fresh held-out set. QA confirms that before
    freezing, and a question that shares its subject with a dev-set question is
    replaced.
  - **When:** written and committed **before embed-v3 Implementation starts**.
    Its sha256 is recorded in STATE.md at that commit (frozen).
    `docs-source.toml` pins the path and the sha256, and ingest refuses a
    mismatch with exit 2.
  - **Who may read it:** no role that builds retrieval (Architect,
    backend-architect) reads its contents before the freeze, or after it. The
    code loads it by path, and unit tests use a synthetic 5-question list in the
    test itself. This is a disclosure control, like the fresh set: git history
    shows who touched the file, and the Implementation note states that the file
    was not opened.
  - **Rule:** τ_offtopic is the nearest-rank p90 of the list's dense-rank-1
    similarity. It targets the same 10% leak rate as the word salads (half the
    owner's 20% tolerance), now measured on the right kind of negative.
  - **Adopters:** the file is per-source configuration. An adopter without one
    gets τ_salad alone, and ingest prints a warning that abstention is
    calibrated only on word salads and is likely too permissive.
- **τ_dense = max(τ_salad, τ_offtopic)**, rounded to 6 dp. Taking the stricter
  of the two means neither null can loosen the other. Both values and their
  sources are recorded in the index `calibration` block.
- Rule: `confident ⇔ dense_top1 ≥ τ_dense`. The v1/v2 ordered checks apply
  (no-searchable-words means no WordPiece tokens beyond the prefix), and a
  result that is not confident has **no hits** (INV-4).
- v2's lexical corroboration is **reported, not gated**. It is printed as a
  second number, so the owner can see where the two signals disagree.
- **This is the weakest part of the design, stated plainly.** Word-salad null
  queries are less fluent than real questions, and encoders give fluent,
  on-domain questions higher similarity to *something* in a docs corpus. So
  τ calibrated on word salads alone is probably **too low**, and fluent
  unanswerable questions about software may clear it. **Part 2 above is the
  mitigation.** It uses fluent negatives written by someone independent of the
  build, never by the builder. It remains a mitigation, not a guarantee: 50
  questions give a coarse p90, and the list's author shapes which kinds of
  off-topic question are covered.
- Calibrating τ on the dev set is also rejected. Now that the fresh set gates,
  `evals/retrieval.toml` (a dev set) could legitimately set τ. But it has only
  6 negatives, which is too few for a stable threshold, and an adopter pointing
  the template at their own docs has no dev set. The owner may overrule this;
  it would be a pre-registered rule such as "τ = midpoint of the dev set's
  lowest-answerable and highest-unanswerable similarity", fixed before the
  freeze.

**Index format `aveto-support/index@3`:**

- `params` gains an `embedding` block: `{"model": "BAAI/bge-small-en-v1.5",
  "revision": "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a", "onnx_sha256":
  "828e1496d7fabb79cfa4dcd84fa38625c0d3d21da474a00f08db0f559940cf35",
  "vocab_sha256": "07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3",
  "offtopic_sha256": "<recorded when QA/owner freeze the list>", "dim": 384, "pooling": "cls", "normalize": true,
  "max_tokens": 512, "query_prefix": "Represent this sentence for searching
  relevant passages: ", "quantization": "int8-127", "fusion": "rrf",
  "rrf_k": 60, "fusion_depth": 100, "confidence": "dense-null-v3"}`.
- `calibration` records `method: "cross-file-null-v3+offtopic-v1"`,
  `tau_salad`, `tau_offtopic` (or `null` when there is no list), and
  `threshold` (τ_dense).
- **The `vocab_sha256` value is REPORTED, not verified.** The first approved
  download computes the actual sha256. If it differs from the reported value,
  Implementation **stops and hands back**. It never "corrects" the pin itself.
- Each passage gains `"embedding": "<base64 of 384 int8 bytes>"`, which adds
  about 512 characters per passage (~0.5 MB for 910 passages).
- It is still **one generated JSON file** and not a database. `load_index`
  rejects index@2.
- The model pin (revision plus per-file sha256) lives in a new `[embedding]`
  table in the committed `docs-source.toml`, so it is configurable like the docs
  source and needs no new file.
- The weights cache is the repo-local `models/<model-id>/<revision>/`, which is
  gitignored.

**Adapter boundary (this is where the pack's pattern first becomes real).**
`Embedder` is a `Protocol` with `embed_passage` and `embed_query`, each returning
bytes of 384 int8 values:

- `OnnxEmbedder` is the real one. It loads only files whose sha256 matches the
  pin.
- `PlaceholderEmbedder` is the default everywhere a model has not been
  explicitly loaded. It raises `"embedding model is not configured in this
  build."`.
- `FakeEmbedder` exists in tests only. It gives deterministic hashed
  bag-of-words vectors, so every unit test runs with no model, no network and no
  key.
- `retrieve` and `eval` construct `OnnxEmbedder` from the local cache. If the
  cache is missing they exit 2 with "run ingest", and they **never download**.

### 2. Approval-ready facts

| Fact | Value | Status |
|------|-------|--------|
| **New runtime dependencies** | `onnxruntime` (MIT) and `numpy` (BSD-3-Clause). This is the first time the product has any runtime dependency. `onnxruntime` 1.2x is expected to declare `coloredlogs` (with `humanfriendly`), `flatbuffers`, `packaging`, `protobuf` and `sympy` (with `mpmath`). That is about 9 packages in total | **UNVERIFIED.** The declared deps vary by onnxruntime version. The first approved `uv lock` records the real tree (`uv tree`) in the Implementation note. More than about 12 packages, or any new top-level dependency, stops Implementation for the owner |
| **Transitive install size** | Roughly 150–250 MB installed: onnxruntime ~50–60 MB, numpy ~35–40 MB, sympy + mpmath ~70 MB, protobuf ~5 MB, the rest small. Wheels download at about 45–60 MB | **ESTIMATE.** Measured and reported at implementation |
| **Dev-only dependency** | **None added.** The tokenizer is checked by QA's golden fixture (§1), generated once outside the repo | Request D withdrawn |
| **Weights source host** | `https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/<revision>/<file>` answers **302** to a signed, expiring Xet CDN URL on **`us.aws.cdn.hf.co`**. That host can differ by region and over time, so it cannot be pinned exactly. Allowlist: `huggingface.co` for the request, plus any host under **`.hf.co`** for the redirect, HTTPS only. Integrity does not rest on the host (see Revision verification and the amended INV-5) | **VERIFIED** (Orchestrator, one HEAD request, 2026-09-29) for the 302 and the `us.aws.cdn.hf.co` host. The variability is reported by the Orchestrator |
| **Pinned revision** | `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` (lastModified 2024-02-22) | **VERIFIED** (HF metadata API, 2026-09-29) |
| **Files and hashes (downloaded)** | `onnx/model.onnx`: 133,093,490 bytes, sha256 `828e1496d7fabb79cfa4dcd84fa38625c0d3d21da474a00f08db0f559940cf35`. `vocab.txt`: 231,508 bytes, sha256 `07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3`. Both pinned in `docs-source.toml` | onnx existence, publisher, size and sha256 **VERIFIED**. vocab size **VERIFIED**. **The vocab sha256 is REPORTED, not verified.** The first approved download checks it, and a mismatch stops Implementation for the owner |
| **Files not downloaded** | `config.json` (743 bytes, VERIFIED size; sha256 `094f8e891b932f2000c92cfc663bac4c62069f5d8af5b5278c4306aef3084750` REPORTED). `tokenizer_config.json` (366 bytes, VERIFIED size; content REPORTED: BertTokenizer, do_lower_case true, tokenize_chinese_chars true, strip_accents null, model_max_length 512). `model.safetensors` (133,466,304 bytes, sha256 `3c9f3166…21ad`, VERIFIED, not used). The tokenizer settings are pinned in code and checked by the golden fixture | As labelled |
| **ONNX graph signature** | Inputs `input_ids`, `attention_mask`, `token_type_ids`; output hidden states `[1, seq, 384]` | **UNVERIFIED** (it needs the 133 MB download). Checked at implementation, under approval, by `test_onnx_graph_signature`, which fails loudly on a mismatch |
| **Download size, cache** | 133,093,490 + 231,508 bytes ≈ **133.3 MB** once per machine, cached in the repo-local `models/BAAI--bge-small-en-v1.5/5c38ec7c…/` (gitignored). Ingest skips the download when every cached file matches its pinned sha256 | Sizes VERIFIED. Cache design |
| **Code licence** | onnxruntime MIT, numpy BSD-3-Clause, sympy BSD-3-Clause, protobuf BSD-3-Clause, and our own code | **UNVERIFIED** per package. Security reads the locked metadata at implementation |
| **Weights licence** | **MIT.** Note for the owner: the model was trained on public datasets, some with research-only terms (for example MS MARCO). The MIT licence on the weights is the publisher's grant, and whether training-data terms matter is a legal judgement for the owner, not an engineering one | MIT **VERIFIED** (HF metadata API). The training-data note is general knowledge, not checked
| **Offline after download?** | **Yes.** After ingest has verified the cached files, `retrieve`, `eval` and tests never open a connection. The autouse network block stays in force for every test that is not network-marked. An `ingest` whose cache is complete and verified makes only the GitHub fetch | Design property, tested |
| **Does question or user text leave the machine?** | **No, never.** Questions are embedded locally. The only outbound requests are two GETs: the GitHub archive URL (repo + commit) and the HF resolve URLs (repo + revision + file name). Neither contains a question, a passage or any user data. HF sees ordinary download metadata (IP, User-Agent), as GitHub already does | Design property. Security verifies |
| **Supply-chain format** | `model.onnx` is a protobuf graph and `vocab.txt` is plain text. **No pickle, and no `trust_remote_code`**: nothing executes code from the model repo. The `.bin` / PyTorch pickle files are never downloaded | Design property |
| **Revision verification** | The integrity control is the **committed sha256 per file, checked before the file is used**. The download streams into a temporary file in the cache directory while hashing. On a mismatch the temporary file is **deleted** and ingest fails with `FetchError` (exit 3). Only a matching file is atomically renamed into place. At every load (ingest, retrieve, eval) the cached file is re-hashed *before* an ONNX session is created or the vocab is read. A mismatch deletes the cached file and exits 2. The host allowlist is the egress control, not the integrity control. The revision SHA pins what we asked for, and the sha256 proves what we got | Design property. Tested by `test_model_hash_mismatch_rejected_and_deleted` and `test_cached_file_rehashed_before_use` |
| **CI cost** | The model download is 133.3 MB per run unless cached. With `actions/cache` keyed on the revision plus the file hashes, a restore is about 5–15 s, and the cached files are still re-hashed before use. Embedding ~910 passages single-threaded on a GitHub-hosted runner is roughly 1–4 min, 2000 short null queries plus about 50 off-topic questions roughly 0.5–1 min, and 30 eval questions a few seconds. CI also runs `uv run pytest -m model` after `ingest`. Installing the new deps adds about 20–40 s with the uv cache. **Total: about +2–6 min per CI run** against a v2 run of well under a minute | Estimates. The `docs-retrieval-ci` slice measures them |
| **Ongoing cost** | No tokens and no API bill. The model runs locally | — |

### 3. What it changes in the safety and intent record

**`.agentic/SAFETY_INVARIANTS.md` is NOT edited here.** A changed safety
control needs the owner's explicit approval (rule 4). These are drafts for that
approval.

**INV-5.** Current text (committed): "The product's only network egress is the
HTTPS archive fetch of the configured GitHub repo at a full 40-hex commit.
Redirects go only to `github.com` / `codeload.github.com`, and no credentials are
sent." The words that change are "**only network egress is the HTTPS archive
fetch of the configured GitHub repo**" and "**Redirects go only to `github.com` /
`codeload.github.com`**". "No credentials are sent" is kept verbatim.

Why the host rule must widen:

- An allowlist of `huggingface.co` alone would refuse the download, because the
  resolve URL answers 302 to `us.aws.cdn.hf.co` (VERIFIED).
- Pinning that exact CDN host would break when HF serves another region or
  changes hosts.
- So the host rule names the `*.hf.co` CDN domain, and **integrity moves to the
  pinned sha256**.

Draft amended text, **in this spec only; `.agentic/SAFETY_INVARIANTS.md` is not
edited** (Request C, rule 4):

> **INV-5** — The product's network egress is limited to two read-only HTTPS
> GET downloads, both made only by `ingest`:
> (a) the archive of the configured GitHub repo at a full 40-hex commit, with
> redirects only to `github.com` / `codeload.github.com`; and
> (b) the pinned files of the configured embedding model, requested from
> `huggingface.co` at a full 40-hex revision, with redirects only to hosts under
> `hf.co` (for example `us.aws.cdn.hf.co`).
> Every model file is checked against its committed sha256 **before it is
> used**. On a mismatch the file is deleted and ingest fails. Trust rests on the
> hash, never on the host. No credentials are sent. **No question, passage or
> user text ever leaves the machine.** `retrieve`, `eval` and the default test
> suite make no network calls.
> *(Enforced by `test_redirect_to_other_host_refused`,
> `test_hf_redirect_outside_hf_co_refused`, `test_short_sha_rejected`,
> `test_model_revision_must_be_40_hex`,
> `test_model_hash_mismatch_rejected_and_deleted`,
> `test_cached_file_rehashed_before_use`,
> `test_retrieve_is_offline_with_cached_model`, and the autouse network block.)*

Host matching is exact: the host is `huggingface.co`, or it ends with `.hf.co`
after IDNA normalisation. A look-alike such as `hf.co.evil.example` or
`evilhf.co` is refused, and `test_hf_redirect_outside_hf_co_refused` covers
both. If HF ever redirects outside `*.hf.co`, ingest fails closed (exit 3), and
widening the rule again is a new rule-4 request.

**INV-4.** None of its existing words has to change. Retrieval still returns
only verbatim passages or "no confident match" with none, and the model only
*ranks* and *gates*. Draft of the full amended text, **in this spec only**. The
last sentence is the only addition, and it strengthens the invariant:

> **INV-4** — Retrieval returns only verbatim passages from the configured
> source at its pinned commit, each with path, heading and line range, or "no
> confident match" with no passages. It never returns generated or reworded
> text. **A model may be used only to rank passages and to decide confidence. It
> never produces, selects fragments of, or alters the text returned.**
> *(Enforced by `test_not_confident_returns_no_hits`,
> `test_result_invariant_enforced`,
> `test_retrieved_text_is_verbatim_slice_of_file`, and a new
> `test_hybrid_hits_are_verbatim_passages`.)*

**The `ai-agent-product` floor's `generationMode`.** No text is generated, so
`generation_mode` stays `"deterministic"`. Proposed: add
`ranking_mode: "lexical" | "hybrid:<model>@<revision>"` to `RetrievalResult`
and to the output, so the model's role is always visible and nobody mistakes
"deterministic generation" for "no model involved". The owner may prefer to set
`generation_mode` itself to a non-deterministic value. That is the owner's call,
and it changes no behaviour.

**Intent lines it contradicts** (`runs/docs-retrieval/intent.md`, owner-confirmed).
The owner would amend each deliberately:

| Intent line (verbatim) | Contradiction |
|------------------------|---------------|
| What I want: "**No model is involved** — this is the retrieval step (step 2 of the design in the README) on its own" | An embedding model is involved in ranking and confidence |
| Done means: "**No model is called anywhere, and the only network access is fetching the pinned docs.**" | Both halves: a local model is called, and a second download (the weights) is added |
| Constraints: "This slice uses no model, so only the language, structure and test setup are exercised." | Same |
| Out of scope: "**Any model call** — classification by model, drafting, checking." | Its examples do not name embeddings, but "Any model call" covers a local encoder |
| Done means: "Running ingest twice on the same commit produces **byte-identical output**." | It holds on the same machine by design (see Determinism). It is at risk only if the fallback relaxation is needed |

The same stance appears in two more places the owner may want to align:

- `.agentic/PROJECT_CONTEXT.md`, "2. **Retrieve** the relevant passages —
  plain code."
- `README.md`, "Retrieve the relevant docs — plain code."

**Release tier: I expect Tier 3.** This is a recommendation; the Release
Manager decides. Four independent reasons, any one of which the Release Manager
could treat as sufficient:

1. `project-packs/ai-agent-product.md` makes "wiring a real LLM client behind a
   placeholder for the first time" Tier 3, plus rule 5. A local, non-generative
   encoder is not an LLM, but it is the first model in a path that was
   deterministic, and the placeholder-to-real transition is exactly what that
   rule targets.
2. It **changes a safety control** (INV-5, rule 4).
3. It adds a **third-party supply-chain input**: a 133 MB binary graph from a
   host we do not control, parsed at runtime. Integrity is hash-pinned, but it is
   still a new external dependency of the product's behaviour.
4. It adds **two runtime dependencies**, where there were none.

What keeps it from being higher-stakes: no deploy, no user data, no posting, no
spend. Tier 3 means the Release Gate walks the Tier 3 rows of
`RELEASE_GATES.md`. The owner should budget for that; the current tier is 2.

**ADR.** If approved, embed-v3 gets `docs/adr/0003-hybrid-embedding-retrieval.md`,
which supersedes the ranking and confidence parts of 0002. ADR 0001 is
unaffected, because its "Anthropic SDK direct" decision concerns generative
calls.

### 4. Determinism

**Target: byte-identical index on same-machine re-runs, as in Done-means 3,
unchanged.** How:

1. **Fixed execution.** ONNX Runtime CPU provider,
   `intra_op_num_threads = 1`, `inter_op_num_threads = 1`,
   `execution_mode = ORT_SEQUENTIAL`, and a fixed
   `graph_optimization_level = ORT_ENABLE_BASIC`. numpy BLAS is pinned to one
   thread (`OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS` and `MKL_NUM_THREADS` set
   to 1 by the CLI before numpy is imported). Single-threaded inference with the
   same library version, same model file and same CPU is bitwise repeatable in
   practice, because the reduction order is fixed.
2. **Batch size 1.** There is no padding, so tensor shapes depend only on the
   input.
3. **int8 quantisation of stored vectors.** It absorbs last-bit float noise. A
   stored value can differ only if a float lands within about 1e-7 of a rounding
   boundary (`x·127` exactly at *.5*), which is vanishingly rare, and even then
   the similarity moves by at most 1/127 in one dimension.
4. **Calibration.** Same seed and sorted iteration as v2. τ is computed from
   dequantised int8 similarities and rounded to 6 dp.
5. **Pinned versions.** The lockfile pins onnxruntime and numpy, and
   `docs-source.toml` pins the model by revision and sha256. `params.embedding`
   records them, and `load_index` rejects a mismatch.

**Not guaranteed across machines.** MLAS kernels pick AVX2, AVX-512 or NEON code
paths by CPU, so a Mac and a Linux CI runner may produce slightly different
floats. With int8, most vectors will still match exactly, but not all. The CI
slice compares within one runner, as it already does for v2.

**If same-machine byte identity fails anyway** (QA's two-run sha256 check is
the test):

- **First fallback:** store embeddings at lower precision (int8 with a coarser
  scale, for example round(x·63)). This needs no owner decision if the check
  passes afterwards.
- **Second fallback, needing the owner to amend Done-means 3:** "byte-identical
  for `source`, `params`, `counts`, `skipped` and `passages[*]` except
  `embedding`; each embedding equal within ±1 int8 step; τ equal within 1e-4."
  Ingest would print both a full sha256 and a sha256 of the embedding-free
  canonical form.
- I would **not** move embeddings into a second file to dodge the check. That
  hides the drift rather than bounding it.

### 5. Files and test plan

**Final file list for embed-v3 (for the EM re-scope): 19 files written by
Implementation, plus 2 files written by QA or the owner. That makes 21 slice
files in total, against the 18 accepted.**

Written by **Implementation** (backend-architect):

| # | File | Change for embed-v3 |
|---|------|---------------------|
| 1 | `pyproject.toml` | + `onnxruntime`, `numpy`. + the `model` pytest marker. `addopts` becomes `-m 'not network and not model'` |
| 2 | `uv.lock` | regenerated (generated file) |
| 3 | `docs-source.toml` | + an `[embedding]` table: model, revision, per-file sha256, and the off-topic list path and sha256 |
| 4 | `.gitignore` | + `models/` |
| 5 | `aveto_support/__init__.py` | unchanged |
| 6 | `aveto_support/__main__.py` | single-thread env vars before the numpy import. Output shows `ranking_mode` and the dense confidence |
| 7 | `aveto_support/ingest.py` | HF download: allowlist, stream-hash, delete on mismatch, atomic rename. Still the only network code |
| 8 | `aveto_support/index.py` | `index@3` schema, embedding params, base64 int8 vectors |
| 9 | `aveto_support/search.py` | RRF fusion, dense calibration (salad + off-topic), confidence rule |
| 10 | `aveto_support/evaluate.py` | prints the dense confidence and `ranking_mode`. Scoring unchanged |
| 11 | **`aveto_support/embed.py`** | **NEW, the 19th file.** `Embedder` protocol, `OnnxEmbedder`, `PlaceholderEmbedder`, WordPiece, int8 quantisation |
| 12 | `tests/conftest.py` | + `FakeEmbedder`, a fake model cache |
| 13 | `tests/test_ingest.py` | + download, allowlist and hash tests |
| 14 | `tests/test_index.py` | + index@3 tests |
| 15 | `tests/test_search.py` | + fusion, calibration, WordPiece, golden-fixture and graph-signature tests. The `embed.py` tests live here, so **no new test file** |
| 16 | `tests/test_evaluate.py` | output-string updates |
| 17 | `README.md` | model note: download, cache, offline after ingest, and "configure your own model pin" |
| 18 | `.agentic/LOCAL_COMMANDS.md` | + `uv run pytest -m model` |
| 19 | `.agentic/CURRENT_MVP_STATUS.md` | the hybrid retrieval note |

Written by **QA or the owner**, never by Implementation. These are the files
added by fixtures, flagged:

| # | File | Author | When |
|---|------|--------|------|
| 20 | `tests/fixtures/wordpiece_golden.json` | QA | after Requests A and B, before the tokenizer is tested |
| 21 | `evals/calibration-offtopic.toml` | QA or owner | before embed-v3 Implementation starts; frozen with its sha256 in STATE.md |

Not counted, as for v2, because they are Architect-owned records:
`docs/adr/0003-hybrid-embedding-retrieval.md`, `docs/ARCHITECTURE.md`, and, only
after Request C is approved, `.agentic/SAFETY_INVARIANTS.md` (applied by the
Architect).

**Why 19 rather than holding at 18.** `embed.py` gives the model adapter
boundary its own module, as the pack's pattern intends. Security can review
the model-loading code in isolation, and `search.py` stays lexical plus fusion
(about 300 lines rather than about 500). If the EM refuses the 19th file, the
same code goes in `search.py`. That works, but it is worse.

**Test plan changes** (in addition to v2's, all offline unless marked):

- `test_search.py`:
  - `test_placeholder_embedder_raises`
  - `test_fake_embedder_deterministic`
  - `test_rrf_fusion_math` (hand-computed ranks, k = 60)
  - `test_hybrid_candidates_union_of_lists`
  - `test_per_file_cap_applies_after_fusion`
  - `test_int8_quantise_roundtrip`
  - `test_dense_calibration_deterministic` (FakeEmbedder)
  - `test_not_confident_returns_no_hits` (unchanged; INV-4)
  - `test_wordpiece_basic_rules` (lowercase, accent strip, punctuation split,
    `##` continuation, `[UNK]`, and 512 truncation with `[CLS]`/`[SEP]`, all on
    a tiny synthetic vocab)
  - `test_hybrid_hits_are_verbatim_passages` (INV-4)
  - `test_tau_is_max_of_salad_and_offtopic`
  - `test_no_offtopic_list_warns_and_uses_salad`, both on a synthetic
    5-question list defined in the test
- `test_ingest.py`:
  - `test_model_hash_mismatch_rejected_and_deleted`
  - `test_cached_file_rehashed_before_use`
  - `test_hf_redirect_outside_hf_co_refused` (covers `evilhf.co` and
    `hf.co.evil.example`)
  - `test_hf_redirect_to_cdn_allowed` (a fake 302 to `us.aws.cdn.hf.co`)
  - `test_model_revision_must_be_40_hex`
  - `test_cached_model_skips_download`
  - `test_offtopic_list_hash_mismatch_exit_2`
  - `test_retrieve_is_offline_with_cached_model` (network blocked, fake cache
    with FakeEmbedder)
- `test_index.py`:
  - `test_load_rejects_index_v2`
  - `test_embedding_params_mismatch_rejected`
- **`model`-marked** (cached files, no network; fail, never skip):
  - `test_wordpiece_matches_golden`
  - `test_onnx_graph_signature`
  - `test_onnx_embedding_is_repeatable`: two runs give bitwise-equal int8
    vectors, which directly tests Determinism point 1
- **Network-marked:**
  - `test_live_model_download_verifies_hashes` (it also turns the REPORTED
    vocab sha256 into a verified one, or fails)
  - `test_live_ingest_byte_identical` (unchanged, now including embeddings)
- **QA stage additions:**
  - `uv tree` output (the actual dependency list)
  - the cached files' sha256 against the pins
  - a packet capture or `lsof`-level check, or at minimum the network-blocked
    test run, showing `retrieve` and `eval` make no connection
  - the two-run sha256 check
  - both eval sets' scores (fresh set gating, dev set diagnostic)

### 6. Honest comparison: v2 versus embed-v3

These predictions are recorded before either variant is built or run. They are
judgement, not measurement. "Fresh" means the owner's held-out set, assumed to be
phrased like `evals/retrieval.toml`.

| | **v2 (lexical)** | **embed-v3 (hybrid)** |
|---|---|---|
| Ungated recall@5 | about 17/24 (range 15–20). On a fresh ~20-question set, about 70% (range 55–85%) | about 20/24 (range 17–23). Fresh, about 80% (range 65–92%) |
| Unanswerable abstention | 4–6 of 6 | 3–6 of 6 on word salads alone. With the QA/owner off-topic list (τ = max of the two), about 4–6 of 6, at some cost to answerable questions |
| **Chance of passing both ≥80% bars on the fresh set** | **about 15%** (10–25%) | **about 30%** (20–45%), perhaps **about 35%** with the off-topic list. Ranking probably clears; abstention is still the likely failure |
| New runtime dependencies | none | 2 direct (onnxruntime, numpy), about 9 in total (UNVERIFIED), about 150–250 MB (ESTIMATE) |
| Downloads | GitHub archive | + 133.3 MB (VERIFIED sizes) from Hugging Face, via `*.hf.co` CDN redirects |
| Approvals needed | none new | 3 rule requests (A and B under rule 5, C under rule 4), plus the owner's intent amendment and the Release Manager's tier decision. Request D is withdrawn |
| Files | 18 | 19 by Implementation + 2 by QA/owner = 21 (EM re-scope) |
| Release tier | 2 | probably 3 (Release Manager) |
| CI time | under 1 min | +2–6 min, with cache |
| Determinism | exact, float math only | same-machine exact by design, with a fallback that needs an owner amendment |
| Security surface | one egress, no parsing of untrusted binaries | two egresses, and parsing a 134 MB ONNX graph (protobuf, no code execution, hash-pinned) |
| Build effort | one more Implementation pass | a larger pass: WordPiece, ONNX runner, download and verify, RRF, dense calibration, and about 15 new tests. Probably one build-stage estimate plus about half again. The Orchestrator prices it |

> **Owner decision, 2026-09-29: "Pursue embed-v3 in this slice."** The
> Architect's recommendation below is kept as written, for the record. The
> owner's choice supersedes it. This spec now proceeds on the "When I would
> recommend the opposite" path. **No gated approval follows from the choice
> itself.** Requests A–C must each be approved.

**Recommendation, stated plainly: do not add embeddings to *this* slice.**
Freeze v2, run the fresh set once, and record the result. If v2 misses, which
is likely, open a **new slice** for hybrid retrieval with this embed-v3 section
as its starting design and its own intent, approvals and tier.

My reasons:

1. **The slice's premise.** Its intent is to find out whether plain code is good
   enough before a model is involved. Adding a model rewrites four intent lines
   and a safety invariant mid-slice, which turns it into a different slice under
   the old one's name.
2. **Low pass chance.** embed-v3 roughly doubles the pass chance, but only to
   about 30%, because abstention, not ranking, becomes the binding problem. A
   sense-aware "the docs don't answer this" judgement is the job of the later
   classifier and checker models, which this design can already feed.
3. **Separate evidence.** A clean v2 result on the fresh set is valuable
   evidence on its own. It is the measured lexical ceiling, and the embeddings
   slice needs it as its baseline.
4. **Tier change.** A Tier 3 change deserves its own Release Gate, not a tier
   change halfway through this one.

**When I would recommend the opposite:** if the owner's priority is shipping
≥80% *ranking* soon, and they accept abstention as the known weak point, then
embed-v3 in this slice is the faster route. In that case approve all of §7,
accept the 19th file (`embed.py`), and move this slice to Tier 3 before
Implementation.

### 7. Draft approval requests (for the Orchestrator to file; drafts only)

Each is a separate, smallest-possible request per `HUMAN_APPROVAL_RULES.md`
"How to ask". None is approved by this text. The facts are filled in from §2,
each carrying its VERIFIED, REPORTED or UNVERIFIED label. The owner decides
knowing which is which.

**Request A: rule 5, "Inviting a model into a previously deterministic path".**

> **What:** Add a local embedding model, `BAAI/bge-small-en-v1.5` at revision
> `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` (VERIFIED; MIT, VERIFIED), run
> from BAAI's own `onnx/model.onnx` on CPU with `onnxruntime` + `numpy`. These
> are new runtime dependencies: about 9 packages in total (UNVERIFIED until
> `uv lock`) and about 150–250 MB installed (ESTIMATE). The model ranks passages
> and decides "no confident match" in `retrieve`, as specified in
> 02-tech-spec.md "variant embed-v3". This includes adding
> `aveto_support/embed.py` as the 19th file, which is the EM's re-scope and not
> part of this rule.
> **Why this rule:** retrieval is plain code today, and this puts a neural model
> in that path. There is no API, no key and no token spend. The model runs
> locally, and no question text leaves the machine.
> **If denied:** nothing changes. Variant v2 (lexical, no model) is built and
> frozen as specified.
> **Scope:** this model, this revision, CPU-local inference only. A different
> model, revision or any hosted API is a new request.

**Request B: rule 5, "Adding a network call to the build / test / commit path".**

> **What:** Let `ingest` (locally and in CI) download **two files** from
> `https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/5c38ec7c405ec4b44b94cc5a9bb96e735b38267a/`:
> - `onnx/model.onnx`: 133,093,490 bytes, sha256
>   `828e1496d7fabb79cfa4dcd84fa38625c0d3d21da474a00f08db0f559940cf35`, both
>   VERIFIED
> - `vocab.txt`: 231,508 bytes, VERIFIED; sha256
>   `07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3`, which
>   is **REPORTED, not verified**. A mismatch at the first download stops the
>   work for the owner.
>
> The resolve URL redirects (302, VERIFIED) to a signed, expiring CDN URL on
> `us.aws.cdn.hf.co`, and the host can vary by region and over time. So redirects
> are allowed to any host under `.hf.co`, HTTPS only. Each file is hashed
> **before use** and deleted on mismatch. The files are cached in the gitignored
> `models/`. No question or user text is sent, and no credentials.
> **Why this rule:** it is a second network call in the build/test path.
> APPROVAL_RECORD-1 covers only the GitHub archive. QA also downloads
> `vocab.txt` once more, into a throwaway environment, to generate the golden
> fixture. That is the same file and host, so it is covered here.
> **If denied:** Request A cannot be used, and v2 is built.
> **Scope:** this host and the `*.hf.co` redirect domain, this repo and
> revision, these two files, read-only GET, no credentials.

**Request C: rule 4, "Changes to safety controls".**

> **What:** Replace INV-5 in `.agentic/SAFETY_INVARIANTS.md` with the amended
> text in 02-tech-spec.md "embed-v3 §3". That text:
> - permits a second egress: the pinned Hugging Face download, with redirects
>   to `*.hf.co`
> - puts trust on the committed sha256, checked before use, with the file
>   deleted on mismatch
> - keeps "no credentials" and adds "no question, passage or user text ever
>   leaves the machine"
> - states that `retrieve` and `eval` make no network calls
>
> Also replace INV-4 with its drafted text, which adds one strengthening
> sentence: "A model may be used only to rank passages and to decide
> confidence. It never produces, selects fragments of, or alters the text
> returned."
> **Why this rule:** INV-5 is a safety control, and widening its egress allowance
> is a change to it, even though it stays tightly bounded.
> **If denied:** INV-5 stays as it is, which rules out Request B, and so
> embed-v3.
> **Scope:** exactly the drafted text.

**Owner decision (not a numbered rule): amend the intent.** Amend the five
intent lines listed in §3 ("No model is involved…", "No model is called
anywhere…", "This slice uses no model…", "Out of scope: Any model call…", and,
only if the determinism fallback is ever needed, Done-means 3). This is not a
gate rule, but the intent is owner-confirmed and QA verifies Done-means
verbatim. Without the amendment, QA would correctly fail embed-v3 on
Done-means 10. The Release Manager also confirms the tier change (2 to 3).

**~~Optional request D: dev-only dependency `tokenizers`~~ is withdrawn.** QA
generates the golden-token fixture once, outside the repo (§1), so `tokenizers`
never enters `pyproject.toml` or `uv.lock`.

**Not an approval, but needed before Implementation.**

- **The EM re-scopes** from 18 to 21 files (§5).
- **QA or the owner writes and freezes** `evals/calibration-offtopic.toml`, with
  its sha256 recorded in STATE.md.
- **The Release Manager confirms the tier** (Tier 3 is expected, see §3).

**Order of events if Requests A–C are approved:**

1. The owner amends the intent.
2. The Architect applies INV-4 and INV-5 and writes ADR 0003.
3. QA or the owner freezes the off-topic list.
4. Implementation builds.
5. QA generates and commits the golden fixture.
6. The `model`- and `network`-marked tests pass.
7. **STOP.** No eval runs. The frozen SHA is recorded in STATE.md.
8. The owner commits the fresh held-out set.
9. QA scores it once with `eval --eval-file`, with no code change between, and
   scores the dev set at the same SHA as a diagnostic.

**Rule 6 does not apply, and here is why.** Rule 6 covers routing user or
customer data to a new processor. Under embed-v3 **no user, customer, question
or passage data goes to Hugging Face**. The only thing HF receives is a file
download request, just as GitHub already does. Hugging Face is an artefact
supplier, handled by Requests A and B and the Security review, not a data
processor. **It would apply** if embeddings were ever computed by a hosted API.
That would need a `VENDOR_RISK_TEMPLATE` assessment and a DPA check first.

## Overfitting protocol — how the 30 questions stay a test, not a training set

Thirty questions are easy to overfit. Anyone can reach 30/30 with a synonym table
or a special case per question, and the score then says nothing about the 31st
question. This protocol keeps the eval set as held-out evidence.

1. **Everything that decides a result is pre-registered in this spec.** That
   covers the tokenizer, the stopword list, the stemmer, k1, b, the field weights,
   top_k, per_file_cap, the coverage formula, and the calibration method, seed,
   count, lengths and quantile. `load_index` rejects an index whose `params`
   differ from the code, so a silent parameter change cannot be scored.
2. **Disclosure.** The Architect read `evals/retrieval.toml`, as the stage brief
   asked, to learn its format and scoring rule. No design choice above was
   checked against how a specific eval question would score, and no corpus
   search was run to simulate one. The only threshold with a free value is τ,
   and it is calibrated from the corpus.
3. **The eval runs once the build is finished, not during it.** Implementation
   runs `eval` only after every unit test passes and the code matches this spec.
   The full output of that first run is committed verbatim as
   `runs/docs-retrieval/eval-run-1.txt` **before any further code change**.
   Every later run is committed as `eval-run-<n>.txt`, so the number of looks at
   the test set shows in git history, and QA and the Release Manager report it.
4. **What may change after seeing eval output.** Only **bug fixes**. A bug fix
   makes the code do what this spec says. It is shown by a new unit test built on
   synthetic text, never on an eval question, and it cites the spec sentence it
   restores.
5. **What may not change after seeing eval output.** Adding or removing
   stopwords, synonyms or spelling maps. Any `RetrievalParams` value. Any
   calibration constant. The Aveto `exclude` list. Any rule keyed to a
   particular word, file or question. `evals/retrieval.toml` itself, which is
   read-only to everyone except the owner.
6. **A miss is a failed gate, not a tuning session.** If run 1 misses either
   threshold, Implementation stops and hands back per `FAILURE_LOOP.md`, with
   `eval-run-1.txt` and the ungated diagnostic (below). The Architect revises the
   **method** on general grounds as a new, versioned variant in this spec (for
   example `cross-file-null-v2`), and records what changed and why before it is
   run. That uses a retry. The cap is 2 (STATE.md failure budget). After that,
   the slice escalates to the owner with every run's numbers. The honest outcome
   might be that plain lexical retrieval cannot reach 80% on these questions,
   and that is a finding for the owner. Embeddings would mean a new dependency
   or a model call, which is the owner's decision.
7. **After any revision, the 30 questions are no longer unseen.** If the method
   changes even once, the Release Gate artefact should say so. The spec
   recommends, but this slice does not require, that the owner write a small
   fresh set of questions later to confirm the result generalises.
   **Triggered 2026-09-29.** Run 1 missed and v2 was written after it was seen.
   The owner is writing the fresh set (`ESCALATION-1.md`).

## Eval command

`evaluate.score(searcher, eval_set) -> EvalReport`, printed by `evaluate.format_report`.

**Eval-set parsing** (`load_eval_set`, `tomllib`), read-only:

- `pinned_commit` (string) and `question` (an array of tables).
- **Answerable**: `answerable` is absent or `true`. It needs `id`, `question` and
  a non-empty `sources` (list of repo-relative paths). `where` is ignored by
  scoring; it is documentation for humans.
- **Unanswerable**: `answerable = false`. It needs `id` and `question`.
  `hard_negative` is ignored by scoring and echoed in the per-question line.
- A malformed file is an `EvalFormatError`, which maps to exit 2.

**Pre-flight check.** `index.commit` must equal `eval_set.pinned_commit`.
Otherwise the command exits 2 with "index is for commit X, eval set is pinned to
Y; re-run ingest". Scoring against the wrong docs is never allowed.

**Scoring rule** (matches the eval file's header and Done-means 8):

- An answerable question is a **hit** when `result.confident` is true **and**
  the path of any returned hit (at most 5) equals any entry in `sources`. A "no
  confident match" on an answerable question is a miss.
- An unanswerable question is a **hit** when `result.confident` is false.
- The bar uses **integer arithmetic**, with no floating-point edge:
  `hits * 5 >= total * 4` (≥ 80%) for each group separately. With 24 answerable
  questions the bar is ≥ 20. With 6 unanswerable it is ≥ 5.
- **Diagnostic, not a gate.** "Ungated recall@5" is the number of answerable
  questions whose correct source is in the capped top 5 *before* the confidence
  rule is applied. It separates "ranking missed the source" from "the threshold
  withheld a correct result" without anyone reading individual questions to find
  out. It is printed, and it never affects the exit code.

**Output (stdout).** The per-question lines come first, then the summary block.
The summary lines are stable, so CI can grep for them, although CI relies on the
exit code.

```
eval: evals/retrieval.toml  index: gpatwa/agentic-sdlc-playbook @ 3a83b669…  threshold: 0.583
a01  HIT   docs/GETTING_STARTED.md (rank 1)
a02  MISS  expected README.md; got no confident match (below-threshold, coverage 0.41)
a03  MISS  expected docs/GETTING_STARTED.md | execution/pack/commands/agentic-slice.md; got agents/…, …
u01  HIT   no confident match (below-threshold, coverage 0.33)
u02  MISS  returned 5 passages; top docs/… (coverage 0.71)
…
answerable:   21/24 (87.5%)  required >= 80%  PASS
unanswerable: 5/6 (83.3%)  required >= 80%  PASS
diagnostic:   ungated recall@5 22/24 (not a gate)
eval: PASS
```

The last line is always exactly `eval: PASS` or `eval: FAIL`. Percentages are
display-only, with one decimal place. **Exit code 0 when both groups pass, 1 when
either misses**, and 2 for any input error (see the CLI contract).

## CLI contract

All commands run from the repo root. Implementation must record these verbatim in
`.agentic/LOCAL_COMMANDS.md` (the Architect cannot write that file), replacing the
stub.

| Purpose | Command | Network |
|---------|---------|---------|
| Install (clean checkout) | `uv sync --locked` | PyPI (toolchain) |
| Type-check | `uv run mypy` | none |
| Lint | `uv run ruff check` | none |
| Test (default, offline) | `uv run pytest` | **blocked** by the autouse fixture |
| Test (live fetch) | `uv run pytest -m network` | the pinned fetch only |
| Ingest | `uv run python -m aveto_support ingest [--config docs-source.toml] [--out index/docs-index.json]` | the pinned fetch only |
| Retrieve | `uv run python -m aveto_support retrieve [--index index/docs-index.json] <question words…>` | none |
| Eval score | `uv run python -m aveto_support eval [--index index/docs-index.json] [--eval-file evals/retrieval.toml]` | none |

Configuration in `pyproject.toml`:

- `[tool.mypy]`: `strict = true`, `python_version = "3.12"`,
  `files = ["aveto_support", "tests"]`.
- `[tool.pytest.ini_options]`: `testpaths = ["tests"]`, `addopts = "-m 'not network'"`,
  `markers = ["network: hits the pinned GitHub archive (approved rule-5 fetch)"]`.
  With this default, `uv run pytest` deselects network tests, and
  `uv run pytest -m network` overrides it, because the last `-m` wins.
- `[tool.ruff]`: `target-version = "py312"`, default rule set. There are no
  per-file ignores.

`retrieve` takes the question as its remaining positional words (`nargs="+"`,
joined with single spaces), so both `retrieve Does Aveto run on Windows` and
`retrieve "Does Aveto run on Windows?"` work.

**Exit codes**, the same for every subcommand:

| Code | Meaning | Raised by |
|------|---------|-----------|
| 0 | Success. For `retrieve`, **both** a confident result and `no confident match` are successes, because abstaining is a correct answer | all |
| 1 | Eval score below either threshold | `eval` only |
| 2 | Input or usage error: bad arguments (argparse's own 2), `ConfigError`, `IndexFormatError` (including a missing index or params mismatch), `EvalFormatError`, commit mismatch between the index and the eval set | all |
| 3 | Fetch error: network failure, non-200, redirect to a disallowed host, size cap, archive/commit mismatch | `ingest` only |

Errors print one line to **stderr** (`error: <message>`) and no traceback.
Normal output goes to **stdout**.

**Ingest report (stdout):**

```
ingested gpatwa/agentic-sdlc-playbook @ 3a83b669a8b53dfdff869a1bbe361bdb156e3a13
files indexed: 87   passages: 1204   skipped files: 0   empty sections dropped: 31
confidence threshold: 0.583333 (cross-file-null-v1, p90 of 2000 null queries, seed 20260926)
wrote index/docs-index.json  sha256 3f9a…(64 hex)
```

(The numbers are illustrative.) The `sha256` line lets anyone confirm Done-means 3
by eye: two runs, same hash.

### How `docs-retrieval-ci` will invoke this (its workflow is not built here)

The CI slice wires these unchanged commands into GitHub Actions, one step each, in
this order. Any non-zero exit fails the job:

```sh
uv sync --locked                                  # fails if uv.lock is stale
uv run mypy
uv run ruff check
uv run pytest                                     # offline suite
uv run python -m aveto_support ingest             # the approved live fetch; exit 3 on fetch failure
uv run python -m aveto_support eval               # exit 1 below either threshold → red build
```

- **Where the score is printed:** stdout of the `eval` step. The two lines
  starting with `answerable:` and `unanswerable:` are the thresholds, and the
  last line is `eval: PASS|FAIL`. To show the score on the run page, the CI slice
  may add `set -o pipefail` and pipe to `tee -a "$GITHUB_STEP_SUMMARY"`. With
  `pipefail`, the exit code of `eval` still decides the step. CI does **not**
  parse numbers to decide pass or fail. The exit code is the gate, so the
  threshold lives in one place (`evaluate.py`).
- `uv run pytest -m network` is optional in CI. The `ingest` step exercises the
  same fetch against the real archive.
- Setting up uv on the runner (for example `astral-sh/setup-uv`, pinned by SHA)
  and making the check required are the CI slice's decisions.
- A red `eval` must block merging the same way a red test does. That is the
  "eval-gated merge" pattern in `RELEASE_GATES.md` and the whole point of
  `docs-retrieval-ci`.

## Service surface

The whole surface is new; nothing existing is extended, because the repo has no
code yet. The five modules are justified in "Stack and structure". Each maps to
one concern and one test file.

| Function | Signature | Invariant |
|----------|-----------|-----------|
| `ingest.load_source_config` | `(path: Path) -> SourceConfig` | Raises `ConfigError` unless repo, a 40-hex commit and exclude are valid; unknown keys rejected |
| `ingest.fetch_archive` | `(source: SourceConfig, *, opener: OpenerDirector \| None = None, max_bytes: int = 50_000_000, timeout: float = 60) -> bytes` | The **only** network call in `aveto_support/`. HTTPS GitHub archive URL only; redirects only to `github.com` / `codeload.github.com`; raises `FetchError` on any failure; sends no credentials |
| `ingest.read_markdown` | `(archive: bytes, source: SourceConfig) -> tuple[list[DocFile], list[tuple[str, str]]]` | Never writes to disk. Raises `FetchError` if the archive is not for `source.commit`. Output sorted by path. `.md` regular files only, `exclude` honoured |
| `ingest.run_ingest` | `(config_path: Path, out_path: Path, *, opener: OpenerDirector \| None = None) -> IngestReport` | State-changing (writes the index). Atomic: on any failure the previous index is unchanged. Same inputs give the same bytes |
| `index.split_passages` | `(path: str, text: str) -> list[Passage]` | Pure. Every passage has `1 ≤ line_start ≤ line_end ≤ line count`. `text` equals those lines verbatim. Headings in fences or front matter are ignored |
| `index.serialize_index` | `(index: Index) -> bytes` | Pure and canonical, per "Index file format" |
| `index.write_index` | `(index: Index, path: Path) -> str` | Atomic replace. Returns the sha256 hex of the bytes written |
| `index.load_index` | `(path: Path) -> Index` | Raises `IndexFormatError` on a missing file, bad JSON, wrong schema, or `params` ≠ the code's `RetrievalParams` |
| `search.tokenize` | `(text: str) -> list[str]` | Pure. Casefold, split, NLTK stopwords, S-stemmer |
| `search.Searcher` | `(index: Index)`, with `.rank(terms: Sequence[str]) -> list[tuple[Passage, float]]` and `.coverage(terms, passage) -> float` | Read-only over the index. Deterministic order `(−score, path, line_start)` |
| `search.calibrate` | `(passages: Sequence[Passage], params: RetrievalParams) -> float` | Pure and deterministic (fixed seed). Returns a value in [0, 1], or 1.0 when there are fewer than 5 eligible files |
| `search.retrieve` | `(searcher: Searcher, question: str) -> RetrievalResult` | Read-only. At most 5 hits and at most 2 per file. `hits` is empty whenever `confident` is false. Never generates text |
| `evaluate.load_eval_set` | `(path: Path) -> EvalSet` | Read-only. Raises `EvalFormatError` |
| `evaluate.score` | `(searcher: Searcher, eval_set: EvalSet) -> EvalReport` | Read-only. Integer threshold check. `passed` is true only if both groups pass |
| `__main__.main` | `(argv: Sequence[str] \| None = None) -> int` | Returns an exit code per the table and never raises to the caller. `if __name__ == "__main__": sys.exit(main())` |

`main` returning an int, rather than calling `sys.exit` inside, lets the tests
check exit codes directly.

## Adapter boundaries

**No model adapter exists in this slice, and none is stubbed.** Retrieval is plain
code from end to end. There is no LLM boundary for a placeholder to guard, so the
Security gate "adapter boundary placeholder still throws" is **n/a, because no
model adapter exists yet** (as `01-scope.md` anticipated).

Deterministic logic covers everything in `aveto_support/`. The one external
integration is the GitHub archive fetch:

| Boundary | Default | Behaviour under test |
|----------|---------|----------------------|
| GitHub archive fetch (`ingest.fetch_archive`) | Real `urllib` opener with the host-restricted redirect handler | **Blocked by default.** `tests/conftest.py` has an autouse fixture that monkeypatches `socket.socket.connect` and `socket.create_connection` to raise `RuntimeError("network disabled in tests; mark with @pytest.mark.network")`, except for tests marked `network`. Offline tests inject a fake `opener` that serves an **in-memory tar.gz built by a fixture** from synthetic markdown (a recorded-fixture double, per `01-scope.md`). No archive bytes from the real repo are committed |

This keeps the pack's rule that tests run without keys or network, and a test
that forgets to inject an opener fails loudly instead of silently fetching.

**Where the future model steps plug in (not built, and not stubbed now):**

```
question ──► [classify] ──► search.retrieve() ──► RetrievalResult ──► [draft] ──► [check] ──► [person approves] ──► post
              step 1          step 2 (THIS SLICE)                     step 3        step 4        step 5
```

- **Classifier (step 1)** sits *before* `retrieve` and takes the raw question.
  The pattern will be a `Classifier` protocol with a `RulesClassifier` (the
  deterministic default) and a `PlaceholderLlmClassifier` that raises
  `"classify LLM adapter is not configured in this build."`. It may route or
  refuse, but it does not change `retrieve`'s contract.
- **Drafter (step 3)** consumes a `RetrievalResult` exactly as defined here. If
  `confident` is false, there is nothing to draft from, and the reply is an
  escalation, not a draft. The drafter's bounded tool loop ("may search the docs
  again") calls `search.retrieve()` as its search tool, so abstention and
  provenance come with it. It gets `PlaceholderLlmDrafter` raising
  `"draft LLM adapter is not configured in this build."`.
- **Checker (step 4)** compares a draft against the `Passage.text` values of the
  hits it cites. It is a separate adapter and model (INV-3).
- **FastAPI**, when a slice needs HTTP, adds a thin route that builds a
  `Searcher` once at startup and calls `retrieve()`. The route layer has no
  retrieval logic of its own.

None of these files is created in this slice. Creating empty adapter scaffolding
now would be the "future-proofing" the role brief warns against.

### Network surface (for Security)

- **One** call site in `aveto_support/` opens a connection: `urllib` inside
  `ingest.fetch_archive`. Implementation must keep it that way, and QA checks it
  with a grep: `urllib`, `http.client`, `socket` and `ssl` appear only in
  `ingest.py`. `aveto_support/` does not import `subprocess`, so it cannot shell
  out to `git` or `curl`.
- Hosts: `github.com` (the request) and `codeload.github.com` (the redirect).
  Both are GitHub, and both fall within APPROVAL_RECORD-1's "read-only fetch of
  `gpatwa/agentic-sdlc-playbook` … from GitHub".
- **Configurability versus the approval scope.** `docs-source.toml` makes the repo
  configurable, as the intent requires. The code can therefore fetch *any*
  public GitHub repo if the file is edited. The rule-5 approval covers **this
  repo's committed config value** only. Pointing this repo's `docs-source.toml`
  at a different repo, or using a non-GitHub host, is a new rule-5 action that
  needs its own approval. An adopter running the template on their own fork is
  outside this repo's approvals. The README says so.

## Audit / feedback / usage events

The `ai-agent-product` floor says every automated action that produces a
user-visible artefact emits an audit event carrying `generationMode`. This slice
has **no event store**: no database (intent: "The real database arrives with the
slice that needs it"), no service process and no users. Adding an append-only log
file now would be a second persisted artefact with no reader. So the events below
are **structured records on the artefacts themselves** rather than rows in an
audit log, and each one is complete enough to be moved into the audit table
unchanged when the database slice lands.

| Event | Type | Emitted from | Where it is recorded | Fields |
|-------|------|--------------|----------------------|--------|
| `ingest.completed` | audit (the only state change: writes the index) | `ingest.run_ingest` | The ingest report on stdout, plus the index file's own `source`, `counts`, `skipped` and `calibration` blocks | repo, commit, files_indexed, passages, skipped, empty_sections_dropped, threshold, calibration method/seed, index sha256, `generationMode: "deterministic"` (implied by the method) |
| `ingest.failed` | audit | `__main__.main` (ingest branch) | stderr `error: …`, plus exit code 2 or 3. The previous index is untouched | error class and message |
| `retrieve.result` | usage (read-only; nothing is persisted) | `search.retrieve` | The `RetrievalResult` returned, and the retrieve output | question, confident, reason, coverage, threshold, hit paths/headings/line ranges, `generation_mode = "deterministic"` |
| `eval.scored` | usage (read-only) | `evaluate.score` | The eval stdout. **Implementation's and QA's runs are committed** as `runs/docs-retrieval/eval-run-<n>.txt` | per-question outcome, both group scores, diagnostic, PASS/FAIL, index commit, threshold |

No timestamp goes into the index, because that would break byte-identity.
Timestamps come from the git commits that record the eval runs. No user data
exists: questions come from the owner at the CLI or from the eval file, and no
question is logged anywhere in this slice.

## Integration points

- **No existing services.** The repo is greenfield, so there is nothing to
  extend or wrap.
- **GitHub (external, read-only)**: the source archive of the configured repo at
  its pinned commit. It is unauthenticated and needs no credential. Approved under
  rule 5 (APPROVAL_RECORD-1).
- **`evals/retrieval.toml` (repo, read-only)**: read by `eval` and by one sanity
  test. **No stage edits it.**
- **PyPI** (toolchain only), through `uv sync`.

## Safety

- **INV-1** (nothing posted without approval): upheld trivially. No code path
  writes to GitHub, and there is no credential and no write API client.
- **INV-2** (answers from Aveto's docs, passages named): this slice returns only
  verbatim passages from the configured docs, each with its path, heading, line
  range and permalink. It never returns a paraphrase. "No confident match"
  withholds everything, so the future drafter cannot be handed ungrounded
  material.
- **INV-3** (a different model checks each draft): n/a, since no drafting
  exists. Nothing here closes off a checker.

**Added to `.agentic/SAFETY_INVARIANTS.md`** under "## Retrieval and network".
The Architect added them after the Orchestrator corrected this stage's write
scope. INV-1..3 are unchanged:

- **INV-4:** Retrieval returns only verbatim passages from the configured source
  at its pinned commit, each with path, heading and line range, or "no confident
  match" with **no** passages. It never returns generated or reworded text.
  *(Test: `test_search.py::test_not_confident_returns_no_hits`,
  `test_retrieved_text_is_verbatim_slice_of_file`.)*
- **INV-5:** The product's only network egress is the HTTPS archive fetch of the
  configured GitHub repo at a full 40-hex commit. Redirects go only to GitHub
  hosts, and no credentials are sent. *(Test: `test_ingest.py::test_redirect_to_other_host_refused`,
  `test_short_sha_rejected`, plus the autouse network block.)*

## Test plan

Every unit test uses **synthetic markdown written in the test itself**. No test
contains an eval question or asserts how an eval question ranks. The eval set is
used only by the `eval` command and by one structural sanity test.

### `tests/conftest.py`
- An autouse network block (see "Adapter boundaries"). It is lifted only for
  `@pytest.mark.network`.
- `make_archive(files: dict[str, bytes], *, repo_name, commit, extra_members=…) -> bytes`
  builds a GitHub-shaped tar.gz in memory, with the top dir `{repo_name}-{commit}/`
  and an optional pax `comment`. `FakeOpener` serves those bytes, or a chosen
  status or redirect.

### `tests/test_ingest.py`
- `test_load_config_valid`, `test_short_sha_rejected`, `test_branch_name_rejected`,
  `test_bad_repo_rejected`, `test_unknown_key_rejected`, `test_exclude_dotdot_rejected`
- `test_read_markdown_keeps_only_md_regular_files` (skips `.txt`, symlinks,
  directories and `../` members)
- `test_read_markdown_strips_top_dir_and_sorts`
- `test_exclude_prefix_honoured`
- `test_archive_for_other_commit_rejected` (both the top-dir name and the pax
  comment)
- `test_non_utf8_file_skipped_with_reason`
- `test_crlf_normalised_line_count_preserved`
- `test_redirect_to_other_host_refused`, `test_non_200_raises_fetch_error`,
  `test_size_cap_enforced`
- `test_default_network_is_blocked` (calling `fetch_archive` with no opener
  raises under the autouse block)
- `test_ingest_is_byte_identical` (run `run_ingest` twice on the same fake
  archive into two paths; the bytes and sha256 are equal)
- `test_ingest_is_byte_identical_under_member_reordering` (same files, shuffled
  tar order; the bytes are identical)
- `test_failed_ingest_leaves_previous_index` (the fake opener fails and the old
  file is unchanged)
- `@pytest.mark.network test_live_fetch_pinned_commit`: runs the real
  `run_ingest` on the committed `docs-source.toml` **twice** and checks that the
  two sha256 values are equal and the file and passage counts are > 0. It also
  checks that **every path named in `evals/retrieval.toml` `sources` is present**
  among the indexed paths. That proves the labels and the corpus agree on paths
  (it catches a top-dir-stripping bug), and it says nothing about ranking.

### `tests/test_index.py`
- `test_split_atx_levels_and_trail` (H1 > H2 > H3, then back to H2 pops
  correctly)
- `test_heading_in_backtick_fence_ignored`, `test_heading_in_tilde_fence_ignored`,
  `test_unclosed_fence_runs_to_eof`
- `test_front_matter_not_headings`
- `test_hashtag_without_space_not_heading`, `test_closing_hashes_stripped`,
  `test_up_to_three_leading_spaces`
- `test_setext_heading_not_recognised` (documents the accepted limitation)
- `test_preamble_passage`, `test_empty_sections_dropped`,
  `test_line_end_trims_trailing_blanks`
- `test_retrieved_text_is_verbatim_slice_of_file` (for every passage,
  `text == "\n".join(lines[line_start-1:line_end])`)
- `test_serialize_canonical` (sorted keys, trailing newline, no NaN) and
  `test_load_round_trip`
- `test_load_rejects_wrong_schema`, `test_load_rejects_params_mismatch`,
  `test_load_missing_file`

### `tests/test_search.py`
- `test_tokenize_casefold_split_stopwords`
- ~~`test_s_stemmer_rules`~~ (v1, superseded). **v2:** `test_porter_end_to_end`,
  checking the pairs from Porter's paper and plain inflections:
  `caresses→caress`, `ponies→poni`, `cats→cat`, `feed→feed`,
  `plastered→plaster`, `motoring→motor`, `hopping→hop`, `falling→fall`,
  `failing→fail`, `filing→file`, `happy→happi`, `sky→sky`, `stopped→stop`,
  `running→run`, `tokens→token`, `windows→window`
- **v2:** `test_porter_step_examples`, checking one published example per step
  (1a, 1b, 1c, 2, 3, 4, 5a, 5b) against the per-step helpers, with the values
  taken from the paper's own tables
- **v2:** `test_short_tokens_not_stemmed` (length ≤ 2)
- `test_stopwords_removed_before_stemming` (`does` never reaches the stemmer)
- `test_bm25_prefers_passage_with_rarer_term`, `test_heading_and_path_count`
- **v2:** `test_file_evidence_lifts_passage_in_on_topic_file`. On a synthetic
  corpus, two passages have equal passage scores, and the one whose file matches
  more of the question ranks first
- **v2:** `test_passage_without_query_terms_never_returned` (its file matches,
  but P = 0)
- **v2:** `test_combined_score_normalised` (the top candidate's two normalised
  parts are each ≤ 1, and λ = 0.5 comes from `RetrievalParams`)
- `test_rank_tie_break_is_path_then_line`
- `test_per_file_cap_two`, `test_at_most_five_hits`
- `test_no_searchable_words` (empty, and only stopwords)
- `test_no_passage_matched` (every term is out of vocabulary)
- `test_not_confident_returns_no_hits` (below τ, so `hits == ()`)
- `test_confident_returns_hits_with_provenance` (path, heading, line range,
  permalink format with `?plain=1#Lx-Ly`)
- `test_result_invariant_enforced` (constructing `confident=False` with hits
  raises)
- ~~`test_oov_term_lowers_coverage`~~ (v1, superseded). **v2:**
  `test_single_shared_word_has_zero_corroboration`,
  `test_corroboration_sums_beyond_strongest_term`,
  `test_absent_word_is_neutral_to_corroboration` and
  `test_lone_keyword_question_is_not_confident` (the hard-negative property, on
  a synthetic corpus)
- `test_calibrate_deterministic` (the same passages give the same τ, twice).
  ~~`test_calibrate_in_unit_interval`~~ becomes **v2**
  `test_calibrate_non_negative`. ~~`test_calibrate_small_corpus_returns_one`~~
  becomes **v2** `test_calibrate_small_corpus_returns_sentinel` (1000000.0).
  **v2:** `test_calibrate_zero_p90_uses_smallest_positive`
- `tests/test_index.py`: `test_load_rejects_wrong_schema` now also covers
  "a v1 (`index@1`) file is rejected"

### `tests/test_evaluate.py`
- `test_load_eval_set_parses_both_kinds`, `test_malformed_eval_file`
- `test_answerable_hit_any_listed_source`, `test_answerable_no_match_is_miss`,
  `test_unanswerable_hit_on_no_match`
- `test_threshold_integer_boundaries`: 20/24 passes, 19/24 fails, 5/6 passes,
  4/6 fails
- `test_ungated_diagnostic_does_not_affect_exit`
- `test_commit_mismatch_exit_2`, `test_missing_index_exit_2`
- `test_cli_eval_exit_0_on_pass`, `test_cli_eval_exit_1_on_miss` (a synthetic
  eval file and index through `main([...])`), `test_cli_retrieve_no_match_exit_0`,
  `test_cli_retrieve_prints_no_confident_match_first_line`,
  `test_cli_ingest_fetch_error_exit_3`
- `test_committed_eval_set_is_well_formed`: `evals/retrieval.toml` parses and has
  ≥20 answerable and ≥5 unanswerable questions, and its `pinned_commit` equals
  `docs-source.toml`'s `commit`. This is structure only; it does not score.

### Eval score (Done-means 8)
- Suite: `evals/retrieval.toml` (owner-authored, `a4e5275`, read-only), all 30
  cases, `a01`–`a24` and `u01`–`u06`, including the hard negatives `u01` and `u02`.
- Command: `ingest`, then `eval` (see the CLI contract). Evidence is the
  committed `eval-run-<n>.txt`.

### What QA runs at stage 3 (QA Evidence)
1. Clean checkout (fresh clone of the branch): `uv sync --locked`, `uv run mypy`,
   `uv run ruff check`, `uv run pytest`, then `uv run pytest -m network`.
2. `ingest` twice, checking that the two printed sha256 values are equal and also
   `shasum -a 256 index/docs-index.json` after each run (Done-means 3). Record
   the file and passage counts (Done-means 2).
3. `retrieve` on one question the QA agent phrases itself (not from the eval set),
   checking path, heading, line range and permalink against the file at the commit
   on GitHub (Done-means 4). Also one clearly off-topic question, which must give
   `no confident match` (Done-means 5).
4. `eval`: record the full output and the exit code. Pass requires ≥20/24 and
   ≥5/6 (Done-means 8). **v2:** QA runs the eval on the committed
   `evals/retrieval.toml` **and** on the owner's fresh held-out set
   (`eval --eval-file <fresh path>`, supplied only to QA). QA verifies the fresh
   file's sha256 against the one the owner recorded before the revision
   (`ESCALATION-1.md`), and reports both scores side by side against the "good
   result" criteria in "Retrieval — variant v2". The fresh set is evidence and is
   not added to the Release Gate threshold unless the owner says so. Report how
   many `eval-run-*.txt` files exist; that is the
   number of looks at the test set.
5. `git log --follow -- evals/retrieval.toml` and
   `git diff a4e5275 -- evals/retrieval.toml`: the only changes are the owner's
   (`17a6ae6`, comment only) (Done-means 6 and 7).
6. Done-means 10: `uv.lock` contains no `anthropic`, `openai` or other model SDK,
   and no runtime dependency at all. `urllib` appears only in
   `aveto_support/ingest.py`. `subprocess` appears nowhere in `aveto_support/`.
7. The README's own-docs instructions work as written (Done-means 11).
8. The safety checklist: INV-1, INV-2, INV-4 and INV-5 (INV-3 is n/a, since no
   drafting exists). Each is checked against the test named beside it in
   `.agentic/SAFETY_INVARIANTS.md`.

No manual UI checks, because there is no UI.

## Rollback plan

The slice is purely additive. It has no deploy, no database, no migration and no
remote writes. The only generated state is the gitignored `index/` directory on
whichever machine ran `ingest`. Another engineer can roll it back without the
author:

1. If `docs-retrieval-ci` has landed, roll it back first, because its workflow
   calls these commands. Revert its commits, or at minimum delete
   `.github/workflows/<its file>` in a commit, so CI does not go red on missing
   commands.
2. Find this slice's implementation commits:
   `git log --oneline --reverse <base>..HEAD -- aveto_support tests pyproject.toml uv.lock docs-source.toml .gitignore README.md .agentic/LOCAL_COMMANDS.md .agentic/CURRENT_MVP_STATUS.md`,
   where `<base>` is `73d0208` (the last commit before Architecture).
3. On a branch, run `git revert --no-edit <oldest>^..<newest>`. Git reverts
   newest first. Pushing or merging the branch is the owner's action.
4. Leave `runs/docs-retrieval/`, `docs/adr/` and `docs/ARCHITECTURE.md` in place.
   They are the history of the decision. If the stack itself is being reversed,
   add an ADR that supersedes 0001; never edit or delete 0001.
5. On any machine that ran `ingest`: `rm -rf index/`, which is the generated,
   gitignored index.
6. Verify: `git status` is clean, `aveto_support/` and `tests/` do not exist, and
   `.agentic/LOCAL_COMMANDS.md` is back to its stub.

Nothing outside the repo needs undoing. The fetch was read-only, and there is no
credential to rotate.

**Partial rollback** (keep the code, pull the bar): not applicable. The ≥80% bar
is a Release Gate in this slice, not a flag, so if the bar cannot be met the slice
does not ship.

## Files the Implementation stage will touch

| # | File | New/modified | Kind |
|---|------|--------------|------|
| 1 | `pyproject.toml` | new | project config (deps, mypy, pytest, ruff, `package = false`) |
| 2 | `uv.lock` | new | **generated** by `uv lock` |
| 3 | `docs-source.toml` | new | configured source |
| 4 | `.gitignore` | modified | adds `index/`, `.venv/`, `__pycache__/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/` |
| 5 | `aveto_support/__init__.py` | new | code (docstring only) |
| 6 | `aveto_support/__main__.py` | new | code |
| 7 | `aveto_support/ingest.py` | new | code |
| 8 | `aveto_support/index.py` | new | code |
| 9 | `aveto_support/search.py` | new | code |
| 10 | `aveto_support/evaluate.py` | new | code |
| 11 | `tests/conftest.py` | new | tests |
| 12 | `tests/test_ingest.py` | new | tests |
| 13 | `tests/test_index.py` | new | tests |
| 14 | `tests/test_search.py` | new | tests |
| 15 | `tests/test_evaluate.py` | new | tests |
| 16 | `README.md` | modified | docs: a "Run it" section (install, ingest, retrieve, eval) and "Point it at your own docs" (edit `docs-source.toml`; full SHA only; a public GitHub repo; this repo's rule-5 approval covers only the committed value). Also update "Status: Not built yet" |
| 17 | `.agentic/LOCAL_COMMANDS.md` | modified | the CLI contract table, verbatim |
| 18 | `.agentic/CURRENT_MVP_STATUS.md` | modified | what exists (ingest/retrieve/eval, CLI only), what is out (model, HTTP, DB, CI until `docs-retrieval-ci`) |

Also committed under `runs/docs-retrieval/` (artefacts, not product):
`eval-run-1.txt` and any later runs.

**This is 18 files against the EM's "≤10 files for a non-refactor change" rule.
The overrun is flagged here and justified, not split.**

- Only **5 files carry logic** (items 6–10, with 5 a one-line marker). Each has a
  single concern and a matching test file.
- One file is **generated** (`uv.lock`). Three are greenfield scaffolding that
  any first Python slice needs (1, 3, 4). Three are docs that Done-means 1 and 11
  explicitly require (16–18).
- The rule exists to keep one implementation pass verifiable in one head. The
  logic here is about 600–800 lines in total, which is within that. Splitting
  again would separate code from its tests, or ingest from the retrieve/eval it
  exists to feed, and neither half would be independently checkable against
  Done-means 8.
- Consolidating to fewer modules was considered. Merging `index.py` into
  `ingest.py` gives a 17-file slice with a module mixing network, parsing and
  serialisation, a worse boundary to save one file. **If the EM disagrees, this
  is the place to push back before Implementation starts.**

## Risks / open questions

- **Lexical retrieval may not reach 20/24 on paraphrased questions.** The eval
  set phrases questions "the way a user would ask, NOT copied from headings".
  Plain BM25 with no synonyms is weakest there. *Mitigation:* the heading-trail
  and file-path fields, the per-file cap, and a threshold calibrated from the
  corpus rather than a hand guess. *If it still misses:* the overfitting protocol
  turns the miss into a bounded Architect retry and then an owner decision. It is
  never quietly tuned. Accepted, because the intent's whole premise is to find
  out whether plain code is good enough before a model is involved.
  **Realised in eval run 1** (14/24 ungated, 2/24 gated). v2 is retry 1, and
  the finding and prediction are in "Retrieval — variant v2".
- **v2 drops the absent-word penalty** (a deliberate trade, see "Diagnosis").
  Unanswerable questions made of two common in-corpus words can now pass as
  confident. Expected unanswerable result: 4–6 of 6. *Accepted,* because v1's
  penalty withheld answerable and unanswerable questions alike and so protected
  nothing.
- **The 30 questions are no longer unseen.** Any v2 score on them is
  post-hoc. *Mitigated* by the owner's fresh held-out set, which only QA reads.
- **Hard negatives are lexically indistinguishable in the limit.** "Windows" as
  an OS and "window" as a time window are the same token after stemming. Coverage
  can reject such a question only when its *other* specific words fail to
  co-occur with it. The ≥5/6 bar allows one miss. *Accepted.* A sense-aware check
  is a model's job (the classifier or checker in later slices).
- **Threshold trade-off.** A stricter τ (grounded or silent) costs answerable
  recall, and a looser one lets hard negatives through. The p90 null quantile is
  pre-registered from the owner's stated tolerance, so the trade-off is decided
  in advance instead of by searching for a passing number. *Accepted.*
- **Cross-platform float identity** (see "Index file format"). Same-machine
  identity is required and tested. *Accepted residual.*
- **GitHub archive endpoint behaviour could change** (top-dir naming, redirect
  host). The commit check fails closed with exit 3, which is the correct failure
  mode for a pinned source. *Accepted.*
- **The configurable repo can widen network scope when edited.** This is
  addressed in "Network surface": the approval covers the committed value only,
  and the README states it. *Mitigated by documentation. Security confirms.*
- **INV-4 and INV-5 are now in `.agentic/SAFETY_INVARIANTS.md`** (section
  "Retrieval and network"), each naming the test that enforces it. They are no
  longer pending. Implementation must create those tests under the names given.
- **Open question for the owner:** none that blocks Implementation. One
  judgement call is recorded here for visibility: **FastAPI is decided but not
  installed in this slice** (no HTTP surface is needed yet). If the owner wants
  the FastAPI skeleton present from slice 1, that adds one dependency tree and a
  route file, and should be said before Implementation starts.

## Hand off

Next agent: **Backend Architect** (backend-architect) owns everything in this
slice: all 18 files in "Files touched". No AI Engineer, because there is no model,
prompt or adapter. No Frontend, because there is no UI.

Artefacts to produce:
- The code and tests exactly as specified, with no new dependency beyond pytest,
  mypy and ruff.
- One focused commit per task (for example scaffold, then ingest, then
  index, then search, then evaluate and CLI, then docs). The eval set stays
  untouched.
- `.agentic/LOCAL_COMMANDS.md` and `.agentic/CURRENT_MVP_STATUS.md` filled in, and
  the README "Run it" and "Point it at your own docs" sections written.
- `runs/docs-retrieval/eval-run-1.txt`, committed **before** any post-eval change
  (the overfitting protocol, step 3).
- An implementation note in `runs/docs-retrieval/03-implementation.md` giving the
  gate evidence (the typecheck, lint and test output), the ingest sha256 values
  from two runs, eval run 1's summary block, and any deviation from this spec
  with its reason. Any change to a pre-registered value is a deviation that
  requires the Architect; it is never absorbed.

### Hand off for retry 1 (variant v2)

Next agent: **Backend Architect**. Re-implement "Retrieval — variant v2" and its
"Deltas to other sections". Nothing else changes.

- **The file list is unchanged: the same 18 files, and no 19th.** Porter goes
  inside `aveto_support/search.py`. The code changes touch `search.py`,
  `index.py` (params, schema, calibration constants), `evaluate.py` and
  `__main__.py` (the output label `coverage` becomes `confidence`/`corroboration`),
  `tests/test_search.py`, `tests/test_index.py` and `tests/test_evaluate.py`
  (output strings). Update `.agentic/CURRENT_MVP_STATUS.md` only if it names the
  v1 method. README, LOCAL_COMMANDS and the CLI commands are unchanged.
- Order of work: implement, make every unit test pass (none of which uses an
  eval question), ingest twice with the sha256 values equal, then run `eval`
  **once**. Commit its output verbatim as `runs/docs-retrieval/eval-run-2.txt`
  before any further change.
- If run 2 misses either bar, stop and hand back. Do not adjust anything. The
  Architect's recommendation is in "Finding for the owner".
- `evals/retrieval.toml` and the owner's fresh set: do not edit either. Do not
  look for the fresh set.
