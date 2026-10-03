# Security & Privacy Review: docs-retrieval-4

Security & Privacy Agent. Diff reviewed: `git diff 6591bf3 HEAD -- aveto_support tests .agentic docs README.md` (6591bf3 = slice 3 merged; HEAD = b6842d8, code at 4419650). Depth: **adversarial** for the model download path, INV-4 and INV-5; **standard** elsewhere. Inputs read: `intent.md`, `01-scope.md`, `01-scope-addendum.md`, `02-tech-spec.md`, `02-approval-request.md`, `APPROVAL_RECORD-1.md`, `03-implementation.md`, `.agentic/SAFETY_INVARIANTS.md`, `aveto_support/ingest.py` and `rerank.py` in full, plus the diff of `__main__.py`, `embed.py`, the three test files, `tests/conftest.py` (autouse block) and the wording files. No network call was made. No eval set was run.

**Verdict: FAIL. There is one required-fix (R1: ADR 0006 claims a crash outcome the evidence does not support), it is doc-only, and there is no blocker.** The code passes: the download path, INV-4 and INV-5 hold under adversarial checks. See section 10.

## 1. Scope checks (standard)

| Check | Evidence | Result |
|-------|----------|--------|
| Files the spec put off-limits are untouched | `git diff --stat 6591bf3 HEAD -- aveto_support/search.py aveto_support/evaluate.py evals docs-source.toml pyproject.toml uv.lock tests/conftest.py .gitignore` is empty | holds |
| Download functions are unchanged (`download_model_file`, `ensure_model_files`, `ensure_reranker_files`, `_HostRestrictedRedirect`, `_hf_host_allowed`, `fetch_archive`) | `git diff -U0 6591bf3 HEAD -- aveto_support/ingest.py` has hunks only at lines 427-514 (`run_ingest`) | holds |
| `RerankParams` pins (model, 40-hex revision, both sha256s) are unchanged | `rerank.py` diff touches only `load`, `close`, `_live`, `signature`, `score` | holds |
| No secrets or credential files added | Grepped the added lines for api key / secret / password / bearer / authorization / `hf_` / `ghp_` / `sk-` / JWT / AKIA patterns: no hit. No `.env`, `.pem`, `.key`, `netrc` or credential file in `git diff --name-only` | holds |
| Copied `models/` and `index/` (Implementation used local copies from the slice 3 worktree) are not committed | `git check-ignore` matches `.gitignore:16 models/` and `.gitignore:10 index/`; `git status` clean | holds |
| No new dependency | `pyproject.toml` and `uv.lock` unchanged | holds |

## 2. Model download path (adversarial)

The download code is byte-for-byte unchanged since slice 3 (section 1). What changed is **who calls it**: `run_ingest` now calls `ensure_reranker_files` only when `with_reranker` is true. The call graph is the only place the claim could break, so I attacked it there and re-confirmed the existing controls.

| Claim | How I tried to break it | Evidence | Result |
|-------|------------------------|----------|--------|
| Only `ingest` can download | Grepped the package for network modules and download entry points | `urllib` / `http.client` are imported only in `ingest.py`. `fetch_archive`, `download_model_file`, `ensure_model_files` and `ensure_reranker_files` are called only from `ingest.py` (lines 348, 369, 432, 452, 458). `rerank.py` and `embed.py` import no fetch code. `retrieve`/`eval` import `run_ingest` (import only) and never call it | holds |
| Default `ingest` never requests the reranker | Read `run_ingest`: the only `ensure_reranker_files` call sits under `if with_reranker:` (line 457). `with_reranker` defaults to `False` in `run_ingest` and is `store_true` in argparse. No env var or config key feeds it (the only `os.environ` use is the thread limits) | `test_default_ingest_makes_no_reranker_request` runs the **real** `ensure_model_files` with a recording opener and asserts that no URL contains the reranker model id. Mutation M1 (force the branch on) fails it, along with 8 other tests | holds |
| `--with-reranker` only widens `ingest`, and only when explicit | `retrieve --with-reranker q` and `eval --with-reranker` | Both exit 2 (argparse rejects them). The flag exists only on the `ingest` subparser. argparse prefix abbreviation (`ingest --with`) still needs the user to type it, so it is still explicit | holds |
| Host allowlist and redirects | Unchanged code. `_hf_host_allowed` = exactly `huggingface.co` or a suffix `.hf.co`. Redirects must be `https`. Hosts are IDNA-normalised and lowercased. `evilhf.co`, `hf.co.evil.example`, `http://…hf.co` and a trailing-dot host are all refused | `test_reranker_redirect_outside_hf_co_refused`, `test_hf_redirect_outside_hf_co_refused`, `test_redirect_to_other_host_refused` pass | holds |
| 40-hex revision | `RerankParams.__post_init__` rejects anything but `^[0-9a-f]{40}$`. The embedding revision is validated in `_load_embedding` | `test_reranker_revision_must_be_40_hex`, `test_model_revision_must_be_40_hex`, `test_short_sha_rejected` pass | holds |
| sha256 before use; delete on mismatch | Download: hashed while streaming into a `mkstemp` `.part` file; `os.replace` only on a match; the `.part` is unlinked on any exception, including `BaseException`. Cache at ingest: re-hash, `unlink` on a mismatch, then re-download. Cache at load: `verify_file` re-hashes both files and deletes on a mismatch before any session or vocab read | `test_reranker_hash_mismatch_rejected_and_deleted`, `test_reranker_cached_file_rehashed_before_use` (real code, not mocked) pass. Mutation M4 (skip the ONNX re-hash in `OnnxReranker.load`) fails the second | holds |
| A tampered cached reranker file cannot be used | **Runtime check D** (real ONNX, scratch copy of `models/`, one byte appended to the reranker `vocab.txt`): `retrieve --ranking file-rerank-v1` exits 2 with `model file vocab.txt does not match its pinned sha256; deleted, run ingest (reranker: run ingest --with-reranker)`. The tampered file was deleted and no session was built. **D2**, run again: exit 2 with the "not cached … ingest --with-reranker" message, and still no download | holds |
| `--ranking file-rerank-v1` without files downloads nothing | **Runtime check C** (embedder-only models dir, sockets blocked, audit hook on `socket.*` / `urllib.*` / `http.*` / `subprocess.*` / `os.system` events): exit 2, zero network events, no file created, stderr names `ingest --with-reranker`. `OnnxReranker.load` checks `is_file()` on both files before `verify_file` and has no fetch import | `test_reranker_absent_fails_closed_without_download` (asserts exit 2, the message, and an empty `models/`). Mutation M3 (make `load` call `ensure_reranker_files` when files are absent) fails it | holds |
| No credentials sent | Requests carry only `User-Agent: aveto-support-ingest`. No `Authorization`, cookie jar or token handling. No `HF_TOKEN` read | grep of the package and of the added lines | holds |
| Cached-file path handling | Cache paths are `models_dir / model.replace("/", "--") / revision / {onnx/model.onnx, vocab.txt}`. The model id is regex-limited to `[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+`, so `/` is gone after the replace and no component can be `..` on its own. The revision is 40-hex. File names are constants. `.part` files are created inside the target dir | `test_reranker_dir_layout` | holds |
| Opt-in fetch and load-check | With the flag, `ensure_reranker_files` (unchanged controls) runs, then `OnnxReranker.load(models_dir).close()` re-hashes both files and builds and releases the session at once. `RerankParams()` in ingest equals `DEFAULT_PARAMS` used by `load` | `test_ingest_with_reranker_fetches_and_rehashes` (call order and close; see advisory A2) | holds |

**What `--with-reranker` changes, in full:** it adds one call to the same, unchanged, pinned and hash-checked reranker fetch that slice 3 made unconditionally, followed by a load-check. It adds no host, model, revision, header or code path. The default is strictly narrower than slice 3's `ingest`.

## 3. INV-5: egress (adversarial)

| Clause | Evidence | Result |
|--------|----------|--------|
| Egress only by `ingest`, only two kinds of read-only GET | Section 2, row 1. `urllib.request.Request` is built only with a URL and a `User-Agent` header and no `data`, so every request is a GET. There are two URL shapes: `https://github.com/{repo}/archive/{commit}.tar.gz` and `https://huggingface.co/{model}/resolve/{revision}/{name}` | holds |
| Default `ingest` fetches only the embedding model | Section 2, row 2 | holds |
| `retrieve` (default) is offline and never touches reranker files | **Runtime check A** (the real `models/` with both models cached, real ONNX embedder, sockets blocked, audit hook): exit 0, `Ranking: file-rrf-v1…`, **zero network events and zero opens of any path under the reranker's cache dir**. **B** (embedder-only models dir): the same result, exit 0. So the default path does not need the reranker's files and does not read them | holds |
| `eval` (default) is offline and loads no reranker | `eval` shares `_dispatch` with `retrieve` up to `Searcher`. After that it adds only `load_eval_set` (a local file) and `score` (`evaluate.py`, unchanged, no network import). `test_default_run_loads_no_reranker` patches `OnnxReranker.load` to raise and runs default `retrieve` **and** `eval`: both exit 0. Mutations M2 (default back to `file-rerank-v1`) and M6 (load the reranker on every run) fail it. I did not run `eval` against any `evals/*.toml` (not needed) | holds |
| `retrieve --ranking file-rerank-v1` with valid files is still offline | **Runtime check E** (valid copies): exit 0, `Ranking: file-rerank-v1:…+ce:…@233902d…:n20`, zero network events | holds |
| No question, passage or user text leaves the machine | No outbound path exists outside `ingest`, and `ingest` sends only pinned identifiers (repo, commit, model, revision, file name) in URLs. The question goes only into `Searcher`, then to local stdout. New error messages contain local paths and file names, never the question. The changed `print`s in `__main__` are the existing stdout prints, re-indented into the `try` | holds |
| The default test suite makes no network calls | `tests/conftest.py` (autouse block on `socket.connect`, `create_connection`, `getaddrinfo`) is unchanged. A blocked call raises `RuntimeError`, which neither `urllib` nor `main` catches (both catch `OSError`-family and named errors only), so an accidental fetch fails the test rather than being swallowed. The full suite: **168 passed, 10 deselected**, offline | holds |
| The four new enforced-by tests really enforce the sentence | `test_default_ingest_fetches_no_reranker` (fetch and load patched to raise on the default path; also asserts the embedder is closed). `test_default_ingest_makes_no_reranker_request` (real `ensure_model_files` with a recording opener; no reranker URL). `test_ingest_with_reranker_fetches_and_rehashes` (opt-in calls fetch, then load, then close). `test_reranker_absent_fails_closed_without_download` (exit 2, message, nothing written, under the socket block). Mutations M1, M3 and M6 each fail at least one of them | holds (see A2) |
| Every name in INV-4's and INV-5's enforced-by lists exists and passes | All 22 names exist exactly once under `tests/`. Running them by name: **27 passed** (some are parametrised) | holds |

### 3.1 The owner's INV-5 sentence and the scope of the edit

- **Approved words (APPROVAL_RECORD-1, verbatim):** "Of the two models, the default path fetches only the embedding model's files: ingest fetches the reranker's files only when run with --with-reranker."
- **Text in `.agentic/SAFETY_INVARIANTS.md` (lines 52-53):** `Of the two models, the default path fetches only the embedding model's files:` / `` **`ingest`** fetches the reranker's files only when run with **`--with-reranker`**. ``
- The words are identical. The only additions are bold and backticks on `ingest` and `--with-reranker`, which the record explicitly allows ("Typography (bold, backticks around `ingest` and `--with-reranker`) follows the file's existing style"). The position is after clause (b) and before "Every model file is checked", as approved.
- **`git diff 6591bf3 HEAD -- .agentic/SAFETY_INVARIANTS.md` has exactly two hunks:** (1) the two-line sentence; (2) the enforced-by list, where `test_retrieve_is_offline_with_cached_reranker`, `and the autouse network` is split so that the four approved names are inserted in the approved order, and the closing `and the autouse network block.)*` is kept. Nothing else in the file changed: the INV-1 to INV-4 text, both pins and clauses (a) and (b) are untouched. **The approval was not exceeded.**

### 3.2 MS MARCO licence

**Not applicable to the default path:** default `ingest` never fetches the reranker, and default `retrieve`/`eval` never open its files (runtime checks A and B). **Still open for anyone who opts in** with `ingest --with-reranker` / `--ranking file-rerank-v1`: this slice does not resolve the reranker's MS MARCO licence question (ADR 0005 records the weights as Apache-2.0 and the model as trained on MS MARCO). Anyone who opts in has to settle it first. ADR 0006 records the first half ("does not apply to it"). It does not say the question stays open for the opt-in, so this artefact is the record of that half (see advisory A4).

## 4. INV-4: a model only ranks; retrieved text is verbatim (adversarial)

| Claim | Evidence | Result |
|-------|----------|--------|
| No ranking, scoring or passage code changed | `search.py`, `index.py` and `evaluate.py` have no diff. The `rerank.py` diff is `load` (an existence check and a re-raise), `close`, `_live` and the `session` local in `signature`/`score`. `score` still returns `float(logits[0][0])` | holds |
| `close()` adds no text path | Both `close()` methods are `-> None` and only set `self._session = None`. `_live()` returns the session object or raises `ModelError("… is closed")`. Neither produces, selects or alters passage text. A closed adapter fails closed (`ModelError`, exit 2), so it never falls back to some other text source | holds |
| Closing cannot change what is returned | In `__main__`, the `finally` runs after `format_result` has already been printed, or `return 0 if passed else 1` has already been computed. The reranker is closed only after all scoring. In `ingest`, the opt-in reranker is closed before embedding starts, and it never contributed to the index (`test_reranker_opt_in_does_not_change_index`: index bytes and sha256 identical, flag on vs off; `test_ingest_is_byte_identical` unchanged) | holds |
| INV-4's named tests | `test_result_invariant_enforced`, `test_retrieved_text_is_verbatim_slice_of_file`, `test_hybrid_hits_are_verbatim_passages`, `test_reranked_hits_are_verbatim_passages`, `test_reranked_result_invariant_enforced` and `test_reranker_returns_only_scores` all pass, unchanged (none appears in the test diff) | holds |
| Runtime output | Runtime checks A and E print `no text generated` in the `Ranking:` line, in both modes | holds |

## 5. Standard-depth checks

| Area | Evidence | Result |
|------|----------|--------|
| CLI argument handling | `--ranking` is restricted by `choices` (an unknown value exits 2). `--with-reranker` exists only on `ingest` (`retrieve`/`eval` reject it, exit 2). The defaults come from one constant, `DEFAULT_RANKING = "file-rrf-v1"`. The question is joined into a string and given only to `retrieve()` | holds |
| Fail-closed absent reranker | `OnnxReranker.load` raises `ModelError` when either file is missing. `main` maps `ModelError` to `error: …` on stderr and exit 2, with stdout empty (asserted in the test). The hash-mismatch path still deletes the file and exits 2. It never downloads (runtime checks C, D and D2) | holds |
| `close()`/`finally` ordering | `_dispatch` closes only the adapters it loaded, the reranker before the embedder, in a `finally` that also covers exit 1, exit 2 and a raised reranker load (by reading: `loaded_embedder` is already set when `OnnxReranker.load` raises). Injected adapters are never closed. `close()` cannot raise, so the second close always runs. `run_ingest` closes the embedder it loaded in a `finally` that wraps the opt-in fetch, embedding and `write_index`. The opt-in reranker is load-checked and closed before the embedder, so the order is reversed. `test_main_closes_loaded_adapters_in_reverse_order` (exit 0, 1 and 2; default mode closes only the embedder; injected never closed) and `test_ingest_closes_embedder_it_loaded` pass. Mutation M5 (drop the reranker close) fails the first. One edge, by reading: if `OnnxReranker.__init__` raises after building its session (wrong graph inputs or shape), that partial object is not closed. It is garbage at once, holds no text and is not a security issue | holds |
| Cache files copied into `models/` and `index/` | Gitignored and uncommitted (section 1). The copies are hash-checked at load like any cached file (runtime check A used them and passed `verify_file`). `index/docs-index.json` is `-rw-------` | holds |
| Autouse network block | `tests/conftest.py` has no diff. The new tests rely on it, and the one that names it (`test_reranker_absent_fails_closed_without_download`) asserts an outcome that a swallowed download could not produce (an empty `models/`) | holds |
| Audit events | The product has no audit, feedback or usage event store. The state-changing command is `ingest`, and its record is the CLI report. Every line is kept. The reranker line now reads `not fetched (optional; …)` on the default path, or the hash-verified status on opt-in. The removed `"injected"` reranker status has no consumer left (grep: `reranker_status` is used only in `ingest.py`, `__main__.py` and two tests, all updated). `model files: …` and `wrote … sha256 …` are unchanged. Nothing was weakened | holds |
| Adapter boundary integrity | `PlaceholderReranker.score` still raises `RuntimeError`, and `PlaceholderEmbedder` is unchanged. No new model, client or dependency was added, and the reranker pin is unchanged. No placeholder became a real client. The two real ONNX adapters were approved in earlier slices (rule 5) and only gain `close()` | holds |
| Approval bypass | Nothing is sent, posted, submitted or deployed. The only safety-control edit (INV-5) carries a recorded rule 4 approval in the Orchestrator's session (APPROVAL_RECORD-1, 2026-10-03T06:42:53Z), and the text applied matches it (section 3.1). Addenda 1-3 are owner scope decisions, correctly marked as not rule 4. The "Aveto AI SDLC" session's suggestions are recorded as advice, not approval | holds |
| Agentic / CAPTCHA surfaces | None in this slice: no agent, no tool, no memory, no browser automation | n/a |
| Crash-evidence artefacts | `crash-evidence/*.sh` run only `retrieve`, or `eval --eval-file evals/retrieval.toml`. No network tool and no other eval set (`grep -i heldout`: no hit). Output files hold `N exitcode` lines only. The scripts hard-code absolute local paths (home dir, session scratchpad): no secret, but they cannot be reused elsewhere (advisory A5) | holds |

## 6. Wording and claims

| Check | Evidence | Result |
|-------|----------|--------|
| README makes no release claim | `README.md` line 3: "**Status: retrieval only; Security Review and Release Gate pending; not announced.** … Nothing here is released." The 14/16, 11/16 and 12/17 figures are stated as recorded scores, not as a bar met. A grep of README, `.agentic/`, `docs/ARCHITECTURE.md` and ADRs 0005/0006 for `releasable` / `released` / `announce` finds only negations | holds |
| `.agentic/CURRENT_MVP_STATUS.md` | "Retrieval has not passed its held-out gate as a released feature; nothing is released or announced, and no answers are generated." No crash wording | holds |
| `docs/ARCHITECTURE.md` | Describes the close discipline as a code property ("so no inference session is left to interpreter teardown"). It makes no claim about the abort | holds |
| **No document claims the crash is fixed or explained; the wording says NOT REPRODUCED** | `03-implementation.md` says "NOT REPRODUCED", with no fixed or explained claim, and gives the counts (unfixed 220, fixed 440, zero 134). **`docs/adr/0006-default-rrf-reranker-opt-in.md` does not.** Written before Implementation, it says in Consequences, line 31: "**Exit codes are no longer at the mercy of teardown order.**" That is an outcome claim the evidence does not support: the spec's premise (a session alive at finalisation) was **observed false** on the unfixed code, and the abort was never reproduced, so nothing shows that exit codes depended on our sessions' teardown order. Line 33: "Slice 4 then reports it as explained, not fixed." But slice 4 reports NOT REPRODUCED, not "explained". Line 26 ("it hides the lifetime defect") asserts a defect that was not observed. Nothing in the ADR says "not reproduced". The ADR is `proposed` and becomes accepted, and **frozen**, when the Release Gate passes, so after the gate this wording could no longer be corrected in place | **fails: R1** |

## 7. Findings

### Required-fix

- **R1. ADR 0006 claims a crash outcome the evidence does not support, and never says "not reproduced".** In `docs/adr/0006-default-rrf-reranker-opt-in.md`:
  - line 31: "Exit codes are no longer at the mercy of teardown order."
  - line 33: "Slice 4 then reports it as explained, not fixed."
  - line 26: "it hides the lifetime defect"

  The recorded status is **NOT REPRODUCED**: zero 134s in 220 unfixed and 440 fixed runs, and the spec's premise was observed false (`03-implementation.md`). This is a claim leak in a decision record that freezes when the Release Gate accepts it. It is **doc-only**: the code at 4419650 passes this review. Remedy, for the engineer and not done here:
  1. Restate line 31 as a property of the code: our sessions are released before interpreter shutdown.
  2. Add that the exit-134 abort was not reproduced (unfixed 220, fixed 440, 0 × 134), so the change is neither a demonstrated fix nor an explanation.
  3. Make lines 26 and 33 consistent with that (for example, "would hide any lifetime defect", and "Slice 4's status: not reproduced; neither fixed nor explained").

  **Re-check scope after the fix:** the ADR 0006 diff and a grep of README, `.agentic/` and `docs/` for fixed / explained / teardown wording. No code or test re-review is needed unless other files change.

No blocker-severity finding.

### Advisory (for the EM to fold into a later slice; none blocks)

- **A1. INV-5's named offline tests cover only the opt-in ranking, with injected adapters.** `test_retrieve_is_offline_with_cached_model` and `…_with_cached_reranker` now pass `--ranking file-rerank-v1`. The default path's offline behaviour is enforced in practice by `test_retrieve_default_ranking_is_rrf`, `test_eval_default_ranking_is_rrf` and `test_default_run_loads_no_reranker` under the autouse block, but INV-5 does not name them. Real-adapter offline behaviour is exercised only by `-m model` and by this review's runtime checks. Name a default-path offline test at the next rule 4 touch of INV-5 (that needs approval, so not now).
- **A2. `test_ingest_with_reranker_fetches_and_rehashes` overstates what it proves.** It patches both `ensure_reranker_files` and `OnnxReranker.load`, so it proves call order and close, not re-hashing. Re-hashing on the opt-in path is proven by `test_reranker_cached_file_rehashed_before_use` and `test_reranker_hash_mismatch_rejected_and_deleted` (real code). The coverage taken together holds. Strengthen the test, for example with real cached fixture files. Do not rename it, because the name is in INV-5.
- **A3. Mixed guidance on a reranker hash mismatch.** The message now reads `… deleted, run ingest (reranker: run ingest --with-reranker)`. Plain `run ingest` no longer refetches the reranker, so the first half is wrong advice. It fails closed either way, so this is cosmetic. Changing it means editing the shared `verify_file` message (spec: not touched) or replacing rather than appending in `load`.
- **A4. The MS MARCO record is half-written in the docs.** ADR 0006 says the licence question "does not apply" to the default path. It does not say it **stays open for the opt-in**. Fold that sentence into the R1 edit if convenient. Section 3.2 above is the record meanwhile.
- **A5. The crash-evidence scripts hard-code absolute local paths** (home dir and this session's scratchpad). No secret leaks, but the scripts cannot be rerun elsewhere. Parameterise them if they are ever reused.

## 8. Tested with what

- **Offline suite:** `uv run pytest -q` gave **168 passed, 10 deselected**. The INV-4 and INV-5 named tests by name gave **27 passed**. Targeted INV and download tests (`-k`) gave 43 passed.
- **Mutation checks** on a scratch copy of HEAD (`git archive` into the session scratchpad, run with the repo's venv; repo untouched, scratch deleted afterwards). Every mutant was caught:
  - M1, default ingest always fetches the reranker: 9+ failures, including the four new INV-5 tests.
  - M2, default back to `file-rerank-v1`: 4 failures.
  - M3, `load` downloads when files are absent: `test_reranker_absent_fails_closed_without_download` fails.
  - M4, `load` skips the ONNX re-hash: `test_reranker_cached_file_rehashed_before_use` fails.
  - M5, reranker never closed: the close-order test fails.
  - M6, default run loads the reranker: 7 failures, including `test_default_run_loads_no_reranker`.
- **Runtime audit**, with the real ONNX models and the real index:
  - **Setup:** sockets monkeypatched to raise, plus a `sys.addaudithook` recording `socket.*`, `urllib.*`, `http.*`, `subprocess.*`, `os.system` and opens of any path under the reranker cache. The question was "how do I install the package". Runs A-E above. Tampering was done only on scratch clones of `models/`, and the real `models/` was not modified.
  - **Results:** zero network events in every run. Zero reranker-file opens on the default path. Exit codes: A 0, B 0, C 2, D 2 (tampered file deleted), D2 2, E 0.
- **argparse:**
  - `retrieve --with-reranker`: exit 2.
  - `eval --with-reranker`: exit 2.
  - an unknown `--ranking`: exit 2.
- **Not done:** no network call. No eval set run (in particular not `evals/retrieval-heldout-4.toml`). No real `ingest`, because it needs the network. Default `eval` with real adapters was not run, since no eval set was needed; it shares the audited `_dispatch` path, and the fake-adapter test covers it.

## 9. Residual risks (accepted or out of this slice's scope)

1. **The exit-134 abort is open.** It was never reproduced (0 in 660 runs across both modes). The close discipline is hygiene with no demonstrated effect. The intent's "fixed or explained" is not met: that is the Release Manager's and the owner's call, not a security finding. It cannot leak data, since it happens after all output has been written.
2. **Verify-then-use gap (pre-existing since slice 1):** `verify_file` hashes a cached file, then ONNX Runtime or `read_text` re-opens it by path. A local process that can write to `models/` could swap the file in between. That attacker already has the user's write access, so this is low.
3. **Proxy environment (pre-existing):** `urllib`'s default handlers honour `HTTPS_PROXY`. A configured proxy would see the pinned public URLs, which carry no question or user text. TLS is end to end over CONNECT, and integrity rests on the sha256.
4. **Native code is outside the socket block:** the autouse fixture and this review's audit hook see only Python-level sockets. ONNX Runtime has no network feature in use, and no new native dependency was added. Low.
5. **The MS MARCO licence question is open for anyone who opts in** (`ingest --with-reranker` / `--ranking file-rerank-v1`). It is not applicable to the default path.

## 10. Verdict

**FAIL: one required-fix (R1, doc-only, ADR 0006 crash wording). No blocker.** The code is sound:
- The default path fetches, loads and opens nothing of the reranker.
- `retrieve` and `eval` are offline.
- `file-rerank-v1` without files fails closed and never downloads.
- A tampered cached file is deleted and never used.
- INV-4 holds.
- The INV-5 edit is exactly the owner's approved wording plus the four approved names.
- No audit line was weakened, and no placeholder became a real client.

The slice goes back for the ADR 0006 wording only. After the fix, a re-check limited to the section 7 R1 scope can turn this into **PASS with advisories** (A1-A5) without re-running the code review. No-go to the Release Gate until then.
