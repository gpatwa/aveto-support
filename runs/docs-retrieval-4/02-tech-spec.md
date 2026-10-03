# Tech Spec: docs-retrieval-4 (make `file-rrf-v1` the default, reranker opt-in, fix the teardown abort)

Software Architect. Depth: standard. Short path: `intent.md` is the requirements source; section 9 traces each "Done means" line. Inputs read: `01-scope.md`, `intent.md`, `00-slice-plan.md`, `STATE.md`, slice 3 close-out section 4, ADR 0005 (status lines), `aveto_support/__main__.py`, `ingest.py` (340-380, 420-505), `rerank.py`, `embed.py`, `.agentic/SAFETY_INVARIANTS.md`. Nothing wider. No eval set was run.

**Nothing in this slice changes a method.** `search.py` ranking and scoring, `evaluate.py`, every `evals/*.toml`, `docs-source.toml`, `pyproject.toml`, `uv.lock` and the pinned constants in `RerankParams` stay as they are. There is no new dependency, model or download. The one existing download (the reranker's two pinned files) moves behind an opt-in.

## 1. (a) Opt-in form for `ingest`

**Decision: a flag, `ingest --with-reranker`, off by default.** The flag is explicit, shows up in shell history and in `--help`, and needs no new config key. A config key would put an egress choice in `docs-source.toml`, which this slice must not touch.

`__main__.py`:
- `ing.add_argument("--with-reranker", action="store_true", help="also fetch and hash-check the optional reranker (file-rerank-v1); off by default")`.
- Pass `with_reranker=args.with_reranker` to `run_ingest`.
- Print the reranker line according to the status:
  - `not fetched`: `reranker files: not fetched (optional; ingest --with-reranker fetches them for --ranking file-rerank-v1)`
  - `cached` / `downloaded`: `reranker files: <status> (sha256 verified before use)`, as today.

`ingest.py`, `run_ingest(..., with_reranker: bool = False)`:
- The embedder branch stays as it is, minus lines 452-453. The default path calls `ensure_model_files` and `OnnxEmbedder.load` and nothing else.
- Only when the flag is set, after the embedder branch:
  ```
  if with_reranker:
      reranker_status = ensure_reranker_files(RerankParams(), models_dir, opener=model_opener)
      OnnxReranker.load(models_dir).close()   # load-check only; released at once (section 3)
  else:
      reranker_status = "not fetched"
  ```
  This decouples reranker fetching from embedder injection. Today an injected embedder silently skips the reranker (`"injected"`). After the change the flag alone decides, so tests can exercise the opt-in path by monkeypatching `ensure_reranker_files` / `OnnxReranker.load` without real model files. The `"injected"` reranker status goes away. `model_status` keeps `"injected"`.
- `IngestReport.reranker_status` takes `"not fetched" | "cached" | "downloaded"`.

**The index is unchanged by construction.** The reranker never contributed to the index. The loaded object was discarded at line 453, and `Index(...)` / `RetrievalParams(embedding=...)` take no reranker field. For the same pinned inputs, the index bytes and sha256 are identical with and without the flag, and identical to the pre-change build. Section 6 has the test.

## 2. Default ranking, and (b) fail-closed when the reranker is requested but absent

**Default switch (`__main__.py` only):** `DEFAULT_RANKING = "file-rrf-v1"`, `RANKINGS = ("file-rrf-v1", "file-rerank-v1")`, and `default=DEFAULT_RANKING` on both the `retrieve` and `eval` `--ranking` arguments. `_dispatch` keeps its existing guard: `OnnxReranker.load` is reached only when `args.ranking == "file-rerank-v1"`. On a default run, no reranker file is opened or hashed, no reranker session is built, and nothing is downloaded (`load` never downloads, and `retrieve`/`eval` import nothing from the fetch code). The `text.replace("ranking: file-rrf-v1", ...)` header fix in `eval` becomes a no-op on the default path and stays correct for the opt-in path.

**Absent reranker files (`rerank.py`, `OnnxReranker.load`):** before `verify_file`, check that both files exist. If either is missing:
```
raise ModelError(
    f"reranker files are not cached in {base}; --ranking file-rerank-v1 needs them. "
    "Fetch them with: ingest --with-reranker (the default ranking, file-rrf-v1, does not need them)"
)
```
`__main__.main` already maps `ModelError` to `error: <message>` on stderr and **exit 2**. Nothing is downloaded: `load` imports no fetch code, and a test runs it under the autouse network block and asserts that no file appeared under `models/`. If the hash does not match, the behaviour is unchanged (`verify_file` deletes the file and raises `ModelError`, exit 2). The one difference is that `load` re-raises with ` (reranker: run ingest --with-reranker)` appended, because plain `run ingest` no longer refetches the reranker. `verify_file` in `embed.py` is shared and is **not** edited for this.

## 3. (c) The exit-134 teardown abort: cause, fix, and what the 20-run check shows

### 3.1 What the evidence says, read literally

- Exit 134 is `128 + SIGABRT`. `libc++abi: terminating due to uncaught exception of type std::system_error: recursive_mutex lock failed: Invalid argument` is the C++ runtime calling `std::terminate`. An exception escaped where none may: a destructor (implicitly `noexcept`) or a function running during `exit()`.
- libc++'s `recursive_mutex::lock` throws `system_error` only when `pthread_mutex_lock` returns an error. On Darwin, `EINVAL` from that call means the mutex is no longer a valid, initialised mutex. In practice, it has already been destroyed (`pthread_mutex_destroy` invalidates the mutex's signature).
- It happened **after** the full report printed and `eval: PASS`, so after all of our code ran, during process teardown. It happened once in eight runs, in `file-rerank-v1` mode, with **two ONNX Runtime sessions** alive in the process (embedder and reranker).

So the defect is a **use-after-destroy at teardown**: some ONNX Runtime code took a lock on a mutex that teardown had already destroyed. This is a lifetime-ordering bug, not a numerical or scoring one.

### 3.2 Why teardown order is undefined here, on general grounds

- ONNX Runtime keeps **process-wide state**: one shared environment (logging manager, allocators, and the locks guarding them) that every `InferenceSession` refers to and locks when it is created and destroyed. That state belongs to the native library. It is destroyed by the library's own static/`atexit` teardown inside `exit()`, **after** Python finalisation.
- A session's native destructor runs when the last Python reference to its `InferenceSession` wrapper goes away. Our code never ends that lifetime explicitly. Each adapter holds its session in `self._session`, and nothing ever releases it. The session is freed whenever the adapter happens to become garbage: on frame exit if nothing else refers to it; or, if it is held by a reference cycle, a cache or a module global, during Python's finalisation, or **never before `exit()`**. CPython guarantees neither an order nor completeness for objects still alive at finalisation, and that order can change from run to run (per-process hash randomisation changes dict and set iteration order; GC timing follows allocation counts).
- Put together: any session whose Python wrapper survives into finalisation is destroyed at an undefined point relative to the ORT environment it locks. If the session goes first, the exit is clean. If the environment's locks are already destroyed, the session's destructor locks a dead mutex, and libc++ throws inside a `noexcept` destructor, which aborts. **That matches all three observed facts:** after-the-work timing, the specific `EINVAL` mutex error, and intermittency.
- **Why two sessions make it worse:** each live session is an independent draw on the same ordering race, and a reranker session additionally lives inside `Searcher` alongside the embedder, so more objects reach finalisation still holding a session. In the default `file-rrf-v1` mode **only one session (the embedder's) is ever built**. The hazard is the same in kind, but there are fewer draws, and it has never been observed in that mode.

This is an argument from how the runtime and the interpreter tear down, not a measurement. Without instrumenting the run, it cannot show which object outlived what. Section 3.4 gives the cheap, eval-free observation that tests the argument's premise.

### 3.3 The fix: explicit, owned session lifetime, released before the interpreter shuts down

**Rule:** whoever loads an ONNX adapter closes it, in reverse order of creation, in a `finally`, before returning to the interpreter. After `main` returns, no ORT session is left alive, so teardown order can no longer matter for our sessions.

| File | Change | Why here |
|------|--------|----------|
| `aveto_support/rerank.py` | `OnnxReranker.close()`: idempotent, sets `self._session = None`. `score()` / `signature()` on a closed reranker raise `ModelError("reranker is closed")`. Plus the section 2 message. | The adapter owns its session, so only it can release it. Dropping the one strong reference frees the native session deterministically, wherever else the adapter object is still referenced (e.g. inside a `Searcher` caught in a cycle). |
| `aveto_support/embed.py` | `OnnxEmbedder.close()`, same contract (`_embed` / `signature` raise `ModelError("embedder is closed")`). | **Needed, not optional.** The embedder's session is one of the two in the failing run, and it is the only session on the default path. Closing only the reranker would leave the embedder's session to the same undefined teardown in both modes. Scope item 4's condition ("only if the argument puts a fix on the embedder's session") is met. About 6 lines. `verify_file` and the tokenizer are untouched. |
| `aveto_support/__main__.py` | `_dispatch` records the adapters **it loaded** (not those injected by the caller; the caller owns those) and closes them in a `finally`: reranker first, then embedder. | `__main__` is the only place that knows the process is about to end and owns both loads on the `retrieve`/`eval` path. The `finally` also covers the error exits (2, 3) and an `eval` below 80% (1). |
| `aveto_support/ingest.py` | The opt-in load-check closes the reranker at once (section 1). `run_ingest` closes the embedder **it loaded** (embedder `None` on entry) in a `finally` after `write_index`. | `ingest` holds two sessions on the opt-in path (scope finding 2). Each is released before `ingest` returns. The default `ingest` holds one. |

`Embedder` / `Reranker` protocols are **not** widened: the placeholders and test fakes need no `close`. `__main__` and `ingest` call `close()` only on the concrete `OnnxEmbedder` / `OnnxReranker` they built themselves.

**Rejected:**
- `os._exit(code)` after flushing. It skips teardown entirely, which hides the defect rather than fixing ownership, and it silently drops `atexit` handlers and unflushed stderr.
- `del` plus `gc.collect()` in `main`. It frees cyclic garbage but depends on who else holds references. Explicit `close()` does not.
- Changing ORT thread or session options, or the ORT version. The threads are already 1/1/sequential, and a version change is a dependency change, which is out of scope.
- Anything found by running eval sets until the abort stops.

**If the argument is wrong:** suppose section 3.4 shows that no adapter outlives `main` on the unfixed code, or the abort still reproduces after the fix. Then the dead lock sits inside ORT's own static teardown (environment versus its Python module). That cannot be fixed here without a dependency change. Implementation then reports **"explained, not fixed"** with the evidence and stops for the owner. The intent allows "fixed or explained". It does **not** try options by trial.

### 3.4 Evidence the Implementer collects, and what it can and cannot show

1. **Premise check (deterministic, no eval set):** a unit test that monkeypatches `OnnxEmbedder.load` / `OnnxReranker.load` to return instrumented fakes. It asserts that `main` closes each loaded adapter exactly once, reranker before embedder, on success and on the exit-1 and exit-2 paths. On the unfixed code, the Implementer also records once (in the report, not as a test) whether a `weakref` to each loaded adapter is still alive after `main` returns. "Alive" confirms the premise of section 3.2 by observation.
2. **Reproduction first, on the unfixed code:** 20 consecutive runs of `eval --ranking file-rerank-v1 --eval-file evals/retrieval.toml`. Output goes to a file; only the exit codes and the 134 count are recorded.
3. **After the fix:** 20 consecutive runs **in each mode** (`file-rrf-v1` default, then `file-rerank-v1`), same set, same recording.

**Sets:** reproduction and every loop use **`evals/retrieval.toml` only**. `evals/retrieval-heldout-4.toml` is **never** run by Architecture or Implementation (its one run belongs to the Release Gate). The second and third sets are not used either.

**What 20 consecutive exit-0 runs can and cannot show (scope risk 1):** they are **necessary, not sufficient**. If the true abort rate is about 1 in 8 (the slice 3 observation), an unfixed build passes 20 straight runs about 7% of the time ((7/8)^20). At 1 in 50, it passes about 67% of the time. So 20 clean runs after the fix are consistent with the fix and do not prove it. The weight rests on sections 3.2-3.3 and on the deterministic close-order test. If step 2 does not reproduce the abort in 20 runs, the report says so plainly: the post-fix runs then show no regression but no before/after difference. In the default `file-rrf-v1` mode, one session is loaded. Its 20 runs may pass trivially, and the report must say that only `file-rerank-v1` was ever observed to crash.

## 4. (d) INV-5 text change (rule 4; applied by Implementation only after `APPROVAL_RECORD-1.md` records the owner's yes)

Two edits, both inside INV-5:
1. **One sentence added**, after the (b) clause and before "Every model file is checked".
2. The **enforced-by list** gains the four new test names from section 6.

Both models' pins stay named, and (a) and (b) are otherwise unchanged. Nothing else in the file changes.

**Full new INV-5 paragraph:**

```
- **INV-5** — The product's network egress is limited to two kinds of
  read-only HTTPS GET download, both made only by `ingest`:
  (a) the archive of the configured GitHub repo at a full 40-hex commit, with
  redirects only to `github.com` / `codeload.github.com`; and
  (b) the pinned files of exactly two local models — the configured embedding
  model (`docs-source.toml`) and the reranker model pinned in
  `aveto_support/rerank.py` — each requested from `huggingface.co` at its own
  full 40-hex revision, with redirects only to hosts under `hf.co` (for example
  `us.aws.cdn.hf.co`).
  **The default path fetches only the embedding model: `ingest` fetches the
  reranker's files only when run with `--with-reranker`.**
  Every model file is checked against its committed sha256 **before it is
  used**. On a mismatch the file is deleted and ingest fails. Trust rests on the
  hash, never on the host. No credentials are sent. **No question, passage or
  user text ever leaves the machine.** `retrieve`, `eval` and the default test
  suite make no network calls.
  *(Enforced by `test_redirect_to_other_host_refused`,
  `test_hf_redirect_outside_hf_co_refused`, `test_short_sha_rejected`,
  `test_model_revision_must_be_40_hex`,
  `test_model_hash_mismatch_rejected_and_deleted`,
  `test_cached_file_rehashed_before_use`,
  `test_retrieve_is_offline_with_cached_model`,
  `test_reranker_revision_must_be_40_hex`,
  `test_reranker_hash_mismatch_rejected_and_deleted`,
  `test_reranker_cached_file_rehashed_before_use`,
  `test_reranker_redirect_outside_hf_co_refused`,
  `test_retrieve_is_offline_with_cached_reranker`,
  `test_default_ingest_fetches_no_reranker`,
  `test_default_ingest_makes_no_reranker_request`,
  `test_ingest_with_reranker_fetches_and_rehashes`,
  `test_reranker_absent_fails_closed_without_download`, and the autouse network
  block.)*
```

**Diff against the current text:**

```diff
   full 40-hex revision, with redirects only to hosts under `hf.co` (for example
   `us.aws.cdn.hf.co`).
+  **The default path fetches only the embedding model: `ingest` fetches the
+  reranker's files only when run with `--with-reranker`.**
   Every model file is checked against its committed sha256 **before it is
@@
   `test_reranker_redirect_outside_hf_co_refused`,
-  `test_retrieve_is_offline_with_cached_reranker`, and the autouse network
-  block.)*
+  `test_retrieve_is_offline_with_cached_reranker`,
+  `test_default_ingest_fetches_no_reranker`,
+  `test_default_ingest_makes_no_reranker_request`,
+  `test_ingest_with_reranker_fetches_and_rehashes`,
+  `test_reranker_absent_fails_closed_without_download`, and the autouse network
+  block.)*
```

**INV-4 is preserved and its text is not touched.** No ranking, scoring or passage code changes (`search.py` is not edited). `OnnxReranker.score` still returns one float. `close()` returns nothing and produces no text. The INV-4 tests (`test_reranked_hits_are_verbatim_passages`, `test_reranked_result_invariant_enforced`, `test_reranker_returns_only_scores`, and the `file-rrf-v1` ones) must pass unchanged in meaning.

## 5. Audit, feedback and usage events; adapter boundaries

- **State-changing functions:** only `run_ingest` (it writes the index and the model cache). Its audit record stays the CLI report it already prints, with one changed line: `reranker files: not fetched (...)` on the default path, and the hash-verified status on opt-in. `retrieve` and `eval` change no state. `close()` changes only in-process state. The CLI has no feedback or usage event store, and none is added.
- **Adapter boundaries:** unchanged in place. `embed.py` and `rerank.py` stay the model boundaries, and `PlaceholderEmbedder` / `PlaceholderReranker` still throw by default, so tests run without model files. The new `close()` sits on the concrete ONNX adapters only.

## 6. (e) Tests that enforce each claim

All run in the default suite under the autouse network block, with injected or monkeypatched adapters and tiny fixture indexes and eval files in `tmp_path`. None reads `evals/*.toml`.

| Claim | Test (new unless marked) | File |
|-------|--------------------------|------|
| Default ranking is `file-rrf-v1` in `retrieve` | `test_retrieve_default_ranking_is_rrf`: `main(["retrieve", ...], embedder=fake)` prints `Ranking: file-rrf-v1` | CLI file (see section 7, item 7) |
| Default ranking is `file-rrf-v1` in `eval` | `test_eval_default_ranking_is_rrf`: header and `Ranking:` line say `file-rrf-v1` | CLI file |
| Default run loads no reranker files | `test_default_run_loads_no_reranker`: `OnnxReranker.load` patched to fail the test. Default `retrieve` and `eval` both exit 0 | CLI file |
| Opt-in still works | `test_rerank_ranking_still_selectable`: `--ranking file-rerank-v1` with an injected fake reranker prints `file-rerank-v1` and calls `score` | CLI file |
| Default `ingest` does not fetch or load the reranker | `test_default_ingest_fetches_no_reranker`: embedder `None` path with `ensure_model_files` / `OnnxEmbedder.load` patched to fakes, and `ensure_reranker_files` / `OnnxReranker.load` patched to fail the test. Report status is `"not fetched"`. Also via `main(["ingest", ...])` the stdout line reads `reranker files: not fetched` | `tests/test_ingest.py` |
| Default `ingest` makes no reranker request | `test_default_ingest_makes_no_reranker_request`: a recording `model_opener`; no request URL contains `cross-encoder/ms-marco-MiniLM-L6-v2` | `tests/test_ingest.py` |
| Opt-in fetches and rehashes | `test_ingest_with_reranker_fetches_and_rehashes`: `with_reranker=True` calls `ensure_reranker_files` once and the load-check once, and closes the reranker. Status is passed through | `tests/test_ingest.py` |
| Index unchanged | `test_reranker_opt_in_does_not_change_index`: same inputs, flag off vs. on (reranker fetch and load patched). Index bytes and sha256 are identical. The existing ingest determinism test passes unchanged, which shows the index matches the pre-change build | `tests/test_ingest.py` |
| Absent files fail closed, exit 2, no download | `test_reranker_absent_fails_closed_without_download`: empty `models_dir`; `main(["retrieve", "--ranking", "file-rerank-v1", ...], embedder=fake)` returns 2, stderr contains `ingest --with-reranker`, and no file was created under `models_dir` | `tests/test_rerank.py` |
| Crash fix: ownership and order | `test_main_closes_loaded_adapters_in_reverse_order`: loads patched to instrumented fakes. After `main` returns, the reranker is closed, then the embedder, each once, on exit 0, 1 and 2. Injected adapters are never closed | CLI file |
| Crash fix: `close()` contract | `test_onnx_adapters_close_releases_session`: built with `object.__new__` and a sentinel `_session`. `close()` sets it to `None`, is idempotent, and later use raises `ModelError` (embedder and reranker) | `tests/test_rerank.py` |
| Ingest releases its sessions | `test_ingest_closes_embedder_it_loaded` (embedder `None` path, patched `OnnxEmbedder.load` returning a fake with `close`) | `tests/test_ingest.py` |
| INV-5 / INV-4 regressions | All existing `test_reranker_*`, `test_retrieve_is_offline_with_cached_reranker`, and the INV-4 tests in section 4, **unchanged in meaning**. Existing tests that asserted `reranker_status == "injected"` or the old default ranking are updated to the new contract, and the report lists them | as they are |

Outside the suite: the 20-run loops in section 3.4, on `evals/retrieval.toml` only, plus the full regression (`mypy`, `ruff`, the default `pytest`).

## 7. Implementation file list (within the scope cap) and what must not be touched

**Code and tests: 7 files (cap 7).**
1. `aveto_support/__main__.py`: `DEFAULT_RANKING`, the reordered `RANKINGS`, `--with-reranker`, the reranker report line, and closing in a `finally` in `_dispatch`.
2. `aveto_support/ingest.py`: the `with_reranker` parameter, removal of lines 452-453 from the default path, the opt-in block, and closing the embedder it loaded.
3. `aveto_support/rerank.py`: `close()`, closed-use guard, and the absent-files message in `load`.
4. `aveto_support/embed.py`: `close()` and the closed-use guard on `OnnxEmbedder` only (section 3.3 gives the reason).
5. `tests/test_ingest.py`
6. `tests/test_rerank.py`
7. **CLI file:** `tests/test_evaluate.py` if it already drives `main(...)`; otherwise one new `tests/test_cli.py`. Use one or the other, never both.

**Wording: 6 files (cap 6).** Each is a one-to-three-line edit with no behaviour:
- `.agentic/SAFETY_INVARIANTS.md`: exactly the section 4 diff, **only after `APPROVAL_RECORD-1.md` records the owner's yes**.
- `.agentic/PROJECT_CONTEXT.md`: replace the stale "plain code" wording with what shipped. Retrieval ranks with a local embedding model (`file-rrf-v1`, default), plus an optional local cross-encoder reranker that is off by default. No generative model.
- `.agentic/LOCAL_COMMANDS.md`: the default ranking is `file-rrf-v1`. `--ranking file-rerank-v1` needs `ingest --with-reranker` first. Add an `ingest --with-reranker` row.
- `.agentic/CURRENT_MVP_STATUS.md`: the default-ranking line, and the "not yet evaluated" line brought in line with the recorded scores (no new claim; Decision 1).
- `README.md`: the status line, kept honest (retrieval only, internally releasable, not announced, no answers generated).
- `docs/adr/0005-cross-encoder-reranker.md`: a status note only ("kept, off by default, opt-in via `ingest --with-reranker`; see ADR 0006"). The decision text is not edited.

The Implementer greps `.agentic/`, `README.md` and `docs/` for "plain code" and "file-rerank-v1", fixes only hits inside these six files, and lists any other hit in its report.

**Must not be touched:**
- `aveto_support/search.py` (`_rerank`, `ranking_mode`, first-stage fusion, all scoring)
- `aveto_support/evaluate.py` (frozen)
- every `evals/*.toml`
- `docs-source.toml`
- `pyproject.toml`
- `uv.lock`
- the pinned values in `RerankParams` (model, revision, sha256s, candidates, token caps, scoring)
- `verify_file`
- the download functions (`download_model_file`, `ensure_model_files`, `ensure_reranker_files`) apart from where they are called
- the INV-4 text

There is **no new dependency, no new model and no new download**. If the Implementer needs any of these, it stops and returns to the Architect. If the diff goes over the cap, the slice splits per `OPERATING_MODEL.md` and does not proceed.

**Living architecture record (Architect-owned):**
- `docs/adr/0006-default-rrf-reranker-opt-in.md` is written by this stage with **Status: proposed**. It becomes accepted when the owner approves (rule 4) and the Release Gate passes.
- **Finding:** `docs/ARCHITECTURE.md` does not mention the reranker at all; it has been stale since slice 3. It needs a row for `rerank.py`, the ranking modes with `file-rrf-v1` as default, the `--with-reranker` egress note, and session ownership/close. That is outside both caps above and outside this stage's write scope as briefed, so the Orchestrator should decide where it goes: a scope-cap exception for Implementation, or a follow-up Architect touch after approval. It is not silently dropped.

## 8. Rollback

The whole slice is a single revert, with no data migration:
1. `git revert` the Implementation commit(s) on `claude/docs-retrieval-4`. Nothing has been pushed or merged; the owner does that.
2. Existing indexes need **no** rebuild, because the index bytes do not change (section 1). Cached reranker files under `models/` are left in place either way. They are hash-checked before every use, and the old code would simply find them cached.
3. After a revert, the reverted code's `ingest` fetches the reranker unconditionally again (old behaviour). INV-5's added sentence would then be false, so the **INV-5 edit must be reverted along with the code**. That restores the previously approved text. Because it is still an edit to a safety control, the reverting session asks the owner for a rule 4 yes first. Check: `pytest` green, `retrieve` prints `Ranking: file-rerank-v1` by default again.
4. Partial rollback is possible without code: run any command with an explicit `--ranking file-rerank-v1` (after `ingest --with-reranker`) to get the old ranking under the new code.

## 9. Trace: intent "Done means" to design

| Done means | Satisfied by |
|------------|--------------|
| Starts from main with slice 3 merged | Done at intake (merge 6591bf3); no design needed |
| `file-rrf-v1` default in `retrieve` and `eval`; rerank still selectable; no reranker files loaded or downloaded by default; fetched only on opt-in | Sections 1 and 2; tests in section 6 rows 1-6 |
| Shutdown crash fixed or explained; 20 exit-0 runs per mode; argued on general grounds | Section 3 (cause 3.2, fix 3.3, evidence and limits 3.4); tests in section 6 rows "Crash fix" |
| No new gate set, no tuning; one regression run of the fourth set at the Release Gate | Section 7, "must not be touched"; section 3.4 limits loops to `evals/retrieval.toml` |
| Security Review and Release Gate once, tier 2; MS MARCO "not applicable to the default path" | Default path never fetches or loads the reranker (sections 1 and 2), which is the factual basis for that record. Stages are downstream |
| INV-5 names both pins, plus the default-path sentence | Section 4 (exact text and diff; rule 4 request in `02-approval-request.md`) |
| "plain code" and the README status line updated | Section 7, wording files |
| Earlier guarantees hold | Section 4 (INV-4 untouched), section 6 last row, section 1 (index unchanged, deterministic) |

## 10. Handoff

- **One owner: backend-architect** (Implementation) holds all of it. The slice touches no UI and no prompt, and the model adapters change only in lifetime.
- **Order:**
  1. Reproduce on the unfixed code (section 3.4 step 2) and run the premise check.
  2. Make the code and test changes.
  3. Run the full regression, then the 20-run loops in each mode.
  4. Apply the wording edits.
  5. Apply the INV-5 edit last, and only if `APPROVAL_RECORD-1.md` holds the owner's yes.
- **Stop conditions:**
  - Section 3.3 "if the argument is wrong".
  - Any need to touch a file listed in section 7 under "must not be touched".
  - A diff over the cap.
