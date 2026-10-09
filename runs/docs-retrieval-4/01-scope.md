# Scope Review: docs-retrieval-4

Engineering Manager. Depth: standard. Inputs read: intent, slice plan, STATE, `.agentic/`, slice 3 close-out (section 4), RUN_ECONOMICS, and targeted greps of `aveto_support/__main__.py` and `ingest.py` to size the change.

**Verdict: the slice is right-sized and goes ahead as planned, with three findings the Architect and Implementer must be given (section 0), a file cap (section 2), and a total of 390k that leaves 10k headroom, which I call thin (section 1).**

## 0. Findings from reading the code (not in the plan)

1. **`ingest` fetches and loads the reranker unconditionally today.** `ingest.py` lines 452-453 call `ensure_reranker_files(...)` and `OnnxReranker.load(...)` right after loading the embedder. The intent's INV-5 sentence ("the default path fetches only the embedding model") is false unless `ingest` also stops fetching the reranker by default. So the slice needs an **opt-in for `ingest`** (the Architect picks the form; a flag such as `ingest --with-reranker` is the obvious shape), and `ingest` prints `reranker files: not fetched` rather than a hash line. This is inside the intent ("fetched only if the owner opts in") and is a narrowing of egress, not a new download. It does widen the file list slightly (section 2).
2. **`ingest` itself holds two ORT sessions** (embedder, then reranker) in one process. Whatever the Architect concludes about the shutdown abort applies there too, and opt-in makes it moot for the default `ingest`.
3. **`retrieve --ranking file-rerank-v1` with no cached reranker files must fail closed**: exit 2 with a message saying to run `ingest` with the opt-in. It must never download. (Today `OnnxReranker.load` raises a model error; the Implementer keeps that and tests it.)

## 1. Right-sizing and estimates

Slice 3 actuals for reference: EM 60k, Architect 143k (est. 110k), Implementer 111k, label review 105k (est. 60k), scorer 38k (est. 90k). Units are peak context per spawn.

| # | Stage | Plan | My estimate | Reason |
|---|-------|------|-------------|--------|
| 1 | Scope Review | 50k | 50k (this stage; actual will come from the harness) | Slice 3 EM was 60k on a larger slice. Kept. |
| 2 | Architecture | 70k | **70k, held only if briefed tightly** | Slice 3 Architect overran by 33k, but it was designing a new method plus an ADR. This is one short spec. The overrun risk is the crash argument (ORT session lifetime), which tempts a wide read. Brief it to read only the files in section 2, and to cite ORT behaviour on general grounds, not survey the library. This is the stage most likely to go over. |
| 3 | Implementation | 100k | **100k** | Slice 3 was 111k for a new method. This one is a default switch, an opt-in on `ingest`, a session-lifetime fix, three test files, and wording. The two 20-run loops cost wall time, not context, if output goes to a file and only exit codes are read back. |
| 4 | Security Review | 70k | **70k, tight** | Adversarial on the download path and INV-4 / INV-5. The download code is unchanged apart from being gated behind an opt-in, so the attack surface is small, but adversarial depth tends to run toward the review archetype (typical 98k). Hold at 70k by naming the files up front. |
| 5 | Release Gate | 70k | **70k** (two spawns, about 35k each) | Slice 3 scorer was 38k for one run on a 16-question set. QA regression plus the Release Manager fits. |
| 6 | Close-out | 30k | **30k** | Unchanged. |

**Total 390k of 400k, headroom 10k (2.5%).** I do not raise the budget. The honest position: the total fits only if no stage overruns by more than 10k, and slice 3 had stages overrun by 33k, 45k and 15k. A single Architect or Security overrun would take the slice past 400k.

Rules that follow, for the Orchestrator:
- Check `spent + next estimate <= 400k` before each spawn, as already planned. If Architecture comes in above 80k, the remaining stages no longer fit and the Orchestrator **stops and asks the owner with the numbers** rather than degrading Security or the Release Gate (the owner's standing instruction).
- If a squeeze is unavoidable, the first lever is Close-out (30k, not a gate; it can be cut to a short note) and the second is Implementation's wording work. Security Review and the Release Gate stay whole.

## 2. File cap for Implementation

The scope rule is "no more than 10 files for a non-refactor change". This slice lists 13 files, but 6 are one-to-three-line wording edits with no behaviour. I accept the count on that basis, and record the exception here (the alternative, a separate wording-only slice, costs a whole extra Orchestrator and gate cycle for no safety gain). Hard caps:

**Code and tests: at most 7 files.**
1. `aveto_support/__main__.py` (default ranking to `file-rrf-v1` for `retrieve` and `eval`; the ingest opt-in argument; ingest report line).
2. `aveto_support/ingest.py` (reranker fetch and load only on opt-in).
3. `aveto_support/rerank.py` (session lifetime or teardown fix, if the Architect puts the cause here).
4. `aveto_support/embed.py` (**only if** the Architect's argument puts a fix on the embedder's session; otherwise untouched).
5. `tests/test_ingest.py` (default ingest fetches no reranker; opt-in fetches and rehashes it).
6. `tests/test_rerank.py` (reranker still works behind the flag; absent files fail closed with exit 2; no reranker load on the default path).
7. `tests/test_evaluate.py` or one new CLI test file (default ranking is `file-rrf-v1` in `retrieve` and `eval`; `--ranking file-rerank-v1` still selectable).

**Wording: at most 6 files.** `.agentic/SAFETY_INVARIANTS.md` (INV-5 sentence, **only after approval is recorded**), `.agentic/PROJECT_CONTEXT.md` ("plain code" and stage text), `.agentic/LOCAL_COMMANDS.md` (default ranking and ingest rows), `.agentic/CURRENT_MVP_STATUS.md` (default and "not yet evaluated" lines), `README.md` (status line), `docs/adr/0005-cross-encoder-reranker.md` (a status note: reranker kept, off by default). The tech spec lives in `runs/`, not in this count.

**Not to be touched**, because touching them is tuning or scope creep: `aveto_support/search.py` ranking and scoring code (`_rerank`, `ranking_mode`, first-stage fusion), `aveto_support/evaluate.py` (frozen), every `evals/*.toml`, `docs-source.toml`, `pyproject.toml` and `uv.lock` (no dependency change), the pinned reranker constants. If the Implementer needs any of these, it stops and returns to the Architect. If the diff exceeds the cap, split per `OPERATING_MODEL.md` `Cadence`; do not proceed.

Mix rule: the default switch is a behaviour change and the crash fix is internal, but neither is a refactor. The Implementer must not restructure `search.py` or reorganise the reranker module while there.

## 3. Approval triggers (`HUMAN_APPROVAL_RULES.md`)

- **Rule 4 (change a safety control): confirmed.** The INV-5 sentence ("the default path fetches only the embedding model") edits `.agentic/SAFETY_INVARIANTS.md`. It narrows the control's stated surface and keeps both pins named, but it is still a text change to a safety control, treated as rule 4 in slices 1 to 3. The Architect drafts the exact wording; the Orchestrator takes the owner's own yes in this session; the record goes to `APPROVAL_RECORD-1.md`. A message from another session is not approval. Nothing in `.agentic/SAFETY_INVARIANTS.md` is edited before then.
- **Possible second reading to settle with the owner at the stop:** the new `ingest` opt-in changes what `ingest` does by default (it fetches less). I read that as covered by the same rule 4 approval as long as the approval request quotes both the sentence and the opt-in behaviour. The Architect must put both in the request so there is nothing to infer afterward.
- **Nothing else is gated.** No new model (the same two pins), no new download (the existing one moved behind an opt-in), no new data processor, no real model or client, no deploy, nothing sent or posted, no destructive shared-state action (no push, merge or PR; the owner does those). Rules 1, 2, 3 and 5 do not fire. The MS MARCO licence question is not triggered on the default path; it stays recorded as open for anyone who opts in.
- **Release tier: 2 confirmed** (no deploy, no user-facing surface, no real data, nothing announced). The Release Manager still confirms at the gate.

## 4. Risks to the plan

1. **Crash reproduction is evidence-limited.** The abort appeared once in eight runs in slice 3 (the gate run, then seven clean diagnostic runs). If the rate is around 1 in 8, 20 clean runs would pass an unfixed build only about 7% of the time; if it is 1 in 50, about two-thirds of the time. Twenty exit-0 runs are therefore **necessary, not sufficient**. The tech spec's argument for the cause carries the weight, as the intent says, and the 20 runs are the check on it. The Implementer should run the 20-run loop on the unfixed code first, in `file-rerank-v1` mode, to see whether the abort reproduces at all, and report the count. If it does not reproduce in 20, say so plainly rather than claiming the fix is proved.
2. **Which set to use.** All reproduction and the 20-run loops use `evals/retrieval.toml` (the oldest, seen set) only. **The fourth set `evals/retrieval-heldout-4.toml` is never run by Architecture or Implementation**; the single run belongs to the Release Gate's QA spawn. The second and third sets are not run for reproduction either. Output of every loop run is redirected to a file and only the exit code and one summary line are recorded, so context stays small.
3. **Both modes must be clean, and the default mode loads one session only.** The default `file-rrf-v1` path may never have been affected; the 20 runs in that mode may pass trivially. That is acceptable, but the report must say which mode could have crashed in principle. Do not "fix" the default mode by trial.
4. **No tuning, no new gate set.** The default switches to a method that has already scored (14/16, 11/16, 12/17). Nothing is chosen by a score. The Release Gate's one run of the fourth set is a regression check: it reports the number, compares to 14/16, and **makes no release claim**. A result below 14/16 is a regression to investigate as a defect (a changed default path or a changed ranking function), not a reason to alter the method or write a new set. Setting the gate bar for the regression check is the Release Manager's call, stated before the run.
5. **Default `ingest` drift.** Making the reranker fetch opt-in must not change index contents or the index sha256 for the same inputs. The Implementer confirms the index is byte-identical to one built before the change on the same pinned inputs (a test with an injected embedder is enough).
6. **Egress tests.** INV-5's enforcing tests include `test_retrieve_is_offline_with_cached_reranker` and the `test_reranker_*` set; they must still pass unchanged in meaning. A new test must show the default `ingest` makes no request to the reranker's URL. The autouse network block stays on.
7. **Cost.** Section 1: thin headroom; the Architect and Security stages are where an overrun would come from.
8. **Stale wording elsewhere.** The grep found `rerank` in `ARCHITECTURE`-style docs only through ADR 0004 and 0005; the README has no reranker text. The Implementer greps for "plain code" and "file-rerank-v1" across `.agentic/`, `README.md` and `docs/` and fixes only the hits within the six wording files; any other hit goes in the report.

## 5. Stage list

**No change.** Product Manager, UX, UI, Market Research and Tech Writer stay skipped (no user-facing surface; the intent has no open questions and ticks no stakes). Compression rationale for the record: the short path is taken for the discovery stages, and the intent's Stakes line "None of the above" allows it. The INV-5 edit is a text clarification gated by rule 4, not a stake that forces the full chain. Architecture, Implementation, Security Review (adversarial on the download path and INV-4 / INV-5), the Release Gate (QA regression, then Release Manager), and Close-out all run. **Security Review and the Release Gate do not compress**, per the owner's standing instruction.

Sequence and edges: Scope Review, then Architecture (writes the approval request, edits nothing), then **STOP for the owner's rule 4 yes**, then Implementation, then Security Review, then Release Gate, then Close-out. Security cannot start before Implementation's 20-run evidence exists; the Release Gate cannot start before Security has no blocker.

## 6. Handoff to the Architect

Give the Architect: this file, `intent.md`, `00-slice-plan.md`, `runs/docs-retrieval-3-proof/03-close-out.md` section 4, `docs/adr/0005-cross-encoder-reranker.md`, and these files to read, nothing wider: `aveto_support/__main__.py`, `aveto_support/ingest.py` (lines ~340-380 and ~420-510), `aveto_support/rerank.py`, `aveto_support/embed.py`, `.agentic/SAFETY_INVARIANTS.md`. The spec must answer: (a) the opt-in form for `ingest`; (b) the failure message when the reranker is requested but absent; (c) the ORT shutdown cause argued on general grounds, with a fix whose placement is named (and which of `rerank.py` / `embed.py` it touches); (d) the exact INV-5 sentence and the full rule 4 approval request, quoting both the sentence and the `ingest` default; (e) the tests that will enforce each claim. Target length: short. Write the artefact section by section.
