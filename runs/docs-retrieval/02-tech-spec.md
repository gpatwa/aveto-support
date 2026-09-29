# Tech Spec — docs-retrieval-core

> Owner: Software Architect Agent
> Status: ready for implementation
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
- `test_s_stemmer_rules`: `queries→query`, `windows→window`, `aliases→aliase`,
  and `glass`, `status` and `bus` unchanged (`bus` is too short to stem)
- `test_stopwords_removed_before_stemming` (`does` never reaches the stemmer)
- `test_bm25_prefers_passage_with_rarer_term`, `test_heading_and_path_count`
- `test_rank_tie_break_is_path_then_line`
- `test_per_file_cap_two`, `test_at_most_five_hits`
- `test_no_searchable_words` (empty, and only stopwords)
- `test_no_passage_matched` (every term is out of vocabulary)
- `test_not_confident_returns_no_hits` (below τ, so `hits == ()`)
- `test_confident_returns_hits_with_provenance` (path, heading, line range,
  permalink format with `?plain=1#Lx-Ly`)
- `test_result_invariant_enforced` (constructing `confident=False` with hits
  raises)
- `test_oov_term_lowers_coverage` (the grounded-or-silent property, shown on a
  synthetic corpus)
- `test_calibrate_deterministic` (the same passages give the same τ, twice),
  `test_calibrate_in_unit_interval`, `test_calibrate_small_corpus_returns_one`

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
   ≥5/6 (Done-means 8). Report how many `eval-run-*.txt` files exist; that is the
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
