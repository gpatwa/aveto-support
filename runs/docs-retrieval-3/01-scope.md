# Agent Handoff — engineering-manager -> software-architect

> Slice: docs-retrieval-3 (slice A: through the freeze)
> From: engineering-manager (Scope Review, depth standard)
> To: software-architect (Architecture, depth standard)
> Date: 2026-09-30
> Playbook: `/Users/gopalpatwa/opt/agentic-sdlc-playbook` (the relative path does not resolve from this worktree)
> Sources: `runs/docs-retrieval-3/intent.md` (source of truth), `00-slice-plan.md`, `.agentic/*`, `runs/docs-retrieval-2-proof/02-close-out.md`, `runs/docs-retrieval-2/01-scope.md` (format only), playbook `project-packs/ai-agent-product.md` "Held-out gates", `docs/HUMAN_APPROVAL_RULES.md`, `execution/pack/protocols/RUN_ECONOMICS.md`.

## 1. Scope decision: ACCEPT the plan, as one slice A plus the planned slice B. No further split.

**Rule check.**
- RUN_ECONOMICS section 2 ("more than 6 stages or ~600k is a signal the slice is too big"): the intent's 600k is already split at the freeze (Decision 1). Slice A is 4 working stages and 330k; slice B is 3 stages and 270k. Each half is under both thresholds. The split is the one I made for slice 2 and it sits on the same seam (the freeze), so I do not re-open it.
- My 10-file rule for a non-refactor change: slice A's expected footprint is **12 to 13 files** (section 4). That is over 10. **Recorded exception, same reasoning as slice 2's scope:** the product code (reranker, its fetch/pin, the combination with the first stage), its tests and the INV-5 and doc deltas have no observable gate alone; the intent gates only the combined method on the held-out set, and forbids choosing any part by score. A further split would cost another Architect + Implementation chain (~240k) to save about 3 files. In place of a split, a **hard cap of 13 files** (section 4). If the Architect needs more, stop and hand back to me; do not widen.
- Mixes behaviour change with refactor: no. One change (a reranker); corpus, first stage, embedding model unchanged.
- New dependency: none allowed. ONNX Runtime and numpy are already runtime dependencies. If the chosen model needs a tokenizer or any library not already present, the Architect must solve it in the existing code (see risk R2) or stop and ask; a new package is its own approval, not a design detail.
- Two unrelated test suites: no. One suite plus `-m model`.
- Observable criteria: yes (intent "Done means").

## 2. Lifecycle: short path confirmed

Rationale: `intent.md` has checkable "Done means", no open questions (Decisions 1 to 3 settled), and its Stakes line has only the "None of the above" box ticked, with a note that the new download touches INV-5 and is covered by the rule 4 and 5 approval of the specific model. Per `docs/AGENTIC_SDLC.md` short path, Market Research, Discovery, UX Research and UI Design are skipped; PM, UX, UI and Tech Writer are skipped (no user-facing surface; README/ARCHITECTURE prose refresh stays deferred, as in slice 2). **Stakes do not override here**: no real user data, money, irreversible action, or auth control is ticked; the INV-5 extension is a safety-control wording change and is handled by a hard approval stop (section 5), not by running the full chain. **QA, Security and the Release Gate never compress.** The plan's stage list stands unchanged.

I disagree with nothing in `00-slice-plan.md`. Adjustments are limited to the estimates and headroom notes below.

**Release tier: 2 confirmed as the working tier** (behavioural change with no external effect; nothing is sent, posted, pushed or deployed). The Release Manager makes the go/no-go. The new model download is gated separately by the owner's rule 4 and 5 approval, not by moving to Tier 3. Slice A is not releasable by itself: no push, no PR.

## 3. Budget: stage list, depth, estimates against 330k (slice A)

Units are peak context per spawn (RUN_ECONOMICS section 1). Check before every spawn: `spent + estimate <= budget`.

| # | Stage | Role | Depth | Est. | Cumulative |
|---|-------|------|-------|------|-----------|
| 1 | Scope Review (this) | engineering-manager | standard | 40k | 40k |
| 2 | Architecture + approval request | software-architect, one fresh spawn | standard | 110k | 150k |
| - | **STOP: owner approvals (rules 4 and 5)** | human | - | 0 | 150k |
| 3 | Implementation | backend-architect, one fresh spawn | standard | 130k | 280k |
| 4 | Freeze | Orchestrator | - | ~0 | 280k |
| | **Headroom in slice A** | | | **50k** | 330k |

- Sum of estimates 280k; **headroom 50k**. Estimates follow RUN_ECONOMICS section 1 (review ~100k, build ~130k); Architecture is set a little above "review" because it also writes the approval request, and Scope Review at 40k is below the 98k typical because it reads only about 10 small files and writes one artefact. If Scope Review comes in far under 40k, that is not spare to spend elsewhere; the budget is not re-split.
- **Depth is standard on every stage.** Adversarial is not earned (no auth, no user data, no irreversible action). Nothing here is to be degraded to smoke either: the Architect's argued-on-general-grounds spec and the Implementer's non-vacuous tests are the load-bearing work.
- **What does not fit in 50k:** a second Architecture spawn (about 110k) or an Implementation retry (about 130k). If the owner **declines** the proposed model, or Implementation fails its regression gate once, the headroom is not enough: **stop and ask the owner with the numbers** (spent, estimate, budget), never raise 330k. The same applies if the pre-spawn hook says over budget.
- **Slice B (270k, `docs-retrieval-3-proof`) opens only at the freeze** with its own STATE Budget block, set by the Orchestrator: B1 label review ~60k, B2 scoring ~90k, B3 Security, Release Gate, Post-Launch ~120k = 270k exactly, **no headroom**. Any overrun in B is a stop-and-ask. If the gate fails, B3's Security and Release Gate do not run (about 80k saved), which is the only slack. Note for the Orchestrator: slice A's unspent headroom does **not** carry to B. The two budgets are the owner's Decision 1; I am not moving money between them.
- RUN_ECONOMICS section 4: every stage writes its artefact section by section as it goes. State this in each brief.

## 4. Files slice A is expected to touch (an inference; I have not read the code, the Architect confirms or corrects)

| Group | Files | Count |
|-------|-------|-------|
| Product and config | a new reranker module (ONNX inference and its tokenisation, reading text and returning an order, never text); `aveto_support/search.py` (re-order the first stage's top candidates and combine scores); `aveto_support/ingest.py` (fetch the reranker's pinned files, hash-check, in `ingest` only); `docs-source.toml` (the pin: source, 40-hex revision, file list, sha256s) | 4 |
| Needed to make the baseline comparison possible | one of `aveto_support/__main__.py` / `aveto_support/evaluate.py`: a way for slice B's QA to score `file-rrf-v1` and the reranked method on the same sets from the same code (a method switch). The Implementer **builds it and tests it on synthetic fixtures only; does not run it on any `evals/` file.** | 1 to 2 |
| Tests | new reranker test file; `tests/test_ingest.py` (pin, hash, redirect, mismatch-delete for the new files); `tests/test_search.py`; `tests/conftest.py` only if a shared fixture changes | 2 to 4 |
| Context and docs | `.agentic/SAFETY_INVARIANTS.md` (INV-5 wording; **only after the owner's rule 4 approval of the exact words**), `.agentic/LOCAL_COMMANDS.md`, `.agentic/CURRENT_MVP_STATUS.md`, new `docs/adr/0005-*.md` (Architect) | 4 |

Baseline **11 to 14**. **Hard cap 13.** The Architect designs to the cap and lists the exact files in the tech spec, justifying each optional one; if it cannot get under 13, hand back for a re-split. `aveto_support/embed.py`, `index.py` and the corpus/first-stage logic must not change (intent: corpus, first stage, embedding model unchanged); if the Architect finds `embed.py` must change (for example to share WordPiece code with the reranker's tokenizer), that is a flagged exception in the spec, with a test proving first-stage output is byte-identical. `pyproject.toml` and `uv.lock` are expected **not** to change; a change there means a new dependency and fires section 5. `runs/` artefacts do not count. Stale-wording fixes (`PROJECT_CONTEXT.md` lines 47 and 55 "plain code", README) are out of this slice (close-out carry-forward (d); separate docs slice).

## 5. Approval triggers and exactly where the run stops

Source: `docs/HUMAN_APPROVAL_RULES.md`, "What explicit approval means": a direct yes to the specific request; not inferred; not carried over; not batchable. The record is the owner's own words in the Orchestrator's session, attributed to a named person (Gopal Patwa), with a UTC time, in `runs/docs-retrieval-3/APPROVAL_RECORD-<n>.md` and the STATE Approvals table. An agent's relayed message is never approval.

| # | Action | Rule | Why it fires | Needed before |
|---|--------|------|--------------|---------------|
| A1 | Approve the **specific reranker model**: source, exact 40-hex revision, file list, each file's sha256, size, licence | **5** (a new real model into the deterministic retrieval path; a new network download in `ingest`) | The intent itself says it needs this "before anything is installed or downloaded"; it is also new ongoing network egress and a new model whose output changes retrieval | Any install, download, or `ingest` run that fetches the model; the Implementation stage |
| A2 | Approve the **exact INV-5 wording extension** for the reranker's files | **4** (change to a safety control: INV-5 is the egress and hash-check invariant) | INV-5 today names exactly two downloads and the embedding model; a third set of files cannot be fetched without changing it | Writing any change to `.agentic/SAFETY_INVARIANTS.md`; the Implementation stage |
| A3 | Push, open a PR, merge | Owner-only, after slice B's Release Gate | The Release Manager records identity and time | Not in slice A at all |
| A4 | Anything the Architect proposes beyond the above: a new host, a new Python dependency, a model that needs `trust_remote_code`, any generative model | 5 and/or 6 | Not approved; **not planned** | Stop; raise as its own request; do not design around it |

**Rule 6 check (stated so the Architect confirms it, not assumes it):** no new subprocessor if the files come from `huggingface.co` (already INV-5's host for the embedding model), only the pinned files are fetched, and no question, passage or user text is sent. If the Architect proposes any other source, rule 6 and `VENDOR_RISK_TEMPLATE.md` come into play and A1 changes shape.

**A1 and A2 are two asks.** They may sit in one message, but each is individually surfaced and individually answered (not batchable). A yes to the model is not a yes to the wording, and neither is a yes to anything wider. Each request follows the playbook format: what, why and which rule, what is reversed if denied, the smallest request.

**Where the run stops.**
1. The Architect finishes `02-tech-spec.md`, the ADR, and **`02-approval-request.md`** (A1 and A2, with the proposed INV-5 text verbatim) **then stops**. It does not edit `.agentic/SAFETY_INVARIANTS.md`, install anything, or download anything.
2. The Orchestrator surfaces A1 and A2 to the owner and **waits**. No Implementation spawn on silence, "looks good", or a relayed yes. If either is declined, or the owner wants a different model, a fresh Architecture spawn is needed (about 110k, over the 50k headroom): stop and ask with the numbers.
3. After both are approved and recorded, Implementation runs. The Implementer applies the **approved wording verbatim** (a wording change after approval is a new A2).

**Open gap I am flagging for the Orchestrator and owner (I cannot resolve it with my tools).** The plan says approval covers "revision, file hashes, source". The Architect has no network tool (and must download nothing), so it cannot know the sha256 values or file sizes from the live model repository. Options: (i) before the approval request is finalised, the Orchestrator or owner fetches the revision and each file's published sha256 from the model page and gives them to the Architect as a sourced input, so the owner approves exact hashes; or (ii) the owner explicitly approves "download of these named files at this revision, then record their hashes", which weakens the "hash approved in advance" property and must be said plainly in the request. I recommend (i). Either way, no file is used before it matches a committed sha256 (INV-5).

## 6. Freeze mechanics and what slice B needs

**The method files** are everything that decides ranking: the reranker module, `search.py`, `ingest.py` (as far as it pins model files), `docs-source.toml`, plus the existing first-stage files unchanged. The Architect lists them in the spec as the freeze set, as slice 2's ADR did.

**Sequence (git order is the proof):**
1. Implementation's last commit, full regression green and reported after that commit: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`, then `uv run pytest -m model` (needs the cached model files).
2. The Orchestrator records the **method commit SHA** in slice A's STATE.md. No fourth set exists anywhere in the repo, committed or not, before this.
3. Only then does the owner hand over the draft fourth set. Slice A ends. The Orchestrator opens `runs/docs-retrieval-3-proof/` with a byte-identical copy of this intent, the frozen SHA, and the Budget block (270k).

**What slice B needs from slice A (so it can start without coming back):**
- the frozen SHA and the method-file list;
- the pinned model files and a built index. `models/` and `index/` are gitignored; slice B's QA runs `retrieve` and `eval` offline, so either slice B runs in this worktree or the cache is rebuilt by `ingest` (approved pinned downloads; deterministic; the index sha256 should match slice A's recorded hash). The Implementer records the index sha256 in `03-implementation.md`;
- a way to score `file-rrf-v1` and the reranked method on the same sets (section 4), documented in `LOCAL_COMMANDS.md`;
- the existing set format in `evals/`, unchanged (a schema change would leak into the set; if the Architect wants one, the owner is told before the set is written);
- the rule that nothing in the method files changes between the set's commit and the scoring run (QA diffs `<frozen>` against HEAD over the method files).

**Label review and scoring (slice B, recorded here so slice A does not undermine it):** B1 is a fresh QA spawn given only the draft set and the pinned docs, listing every file that defensibly answers each question (`project-packs/ai-agent-product.md` "Held-out gates" rule 4). The owner commits the reviewed set. B2 is a **different** fresh QA spawn that scores once. The set is drafted by the owner or QA and never by anyone who built the method (rule 1); the slice-2 provenance note applies (the draft must come from someone who has not seen the reranker or its results, and who reports never having run retrieval on the questions). Bar and labels are never changed after a result (rule 5).

## 7. Risks

| # | Risk | Control |
|---|------|---------|
| R1 | Tuning by score. A reranker, N and a combination rule invite "try a few and keep the best". The close-out's five misses (narrow template/role files losing to broader neighbours) are motivation, **not evidence to fit to**; they come from seen sets | The Architect argues the model, N and combination on general grounds, **before any result exists**, and records the arguments. No role runs `eval` on any set (section 8). The three earlier sets are read-only and scored only once, in B, as diagnostics |
| R2 | The reranker's tokenizer. A cross-encoder needs a tokenizer; `embed.py` has a WordPiece implementation for the embedding model; some rerankers use a different tokenizer (for example SentencePiece), which would be a new library or hand-rolled code. "ONNX Runtime + numpy only" is a hard constraint | The Architect states, in the spec, how the chosen model is tokenised with the existing dependencies. No viable answer means pick a different model or stop and ask. Tokenisation correctness gets a golden-file test (slice 1 hit exactly this gap: `wordpiece_golden.json`) |
| R3 | INV-4 drift. A reranker only orders; a bug that truncates, merges or rewrites candidate text would break "never alters the text returned" | The returned passages must still pass `test_result_invariant_enforced`, `test_retrieved_text_is_verbatim_slice_of_file` and the hybrid-hits test, at full strength; the reranker interface takes text in and returns an order only. Name any retired or rewritten INV-enforcing test in the spec, with the reason (as in slice 2 contradiction 1) |
| R4 | INV-5 / supply chain: new files from a new repo and revision | A1 and A2; 40-hex revision; per-file sha256 checked before use; mismatch deletes the file and fails ingest; redirects only to `hf.co` hosts; `retrieve`, `eval` and the default suite stay offline (the autouse network block); a licence check in the request |
| R5 | Determinism: a model's ONNX output can differ across threads or platforms, and ties in combined scores break by arbitrary order | The Architect specifies a deterministic tie-break and a deterministic runtime setting; a test runs rerank twice and compares |
| R6 | Cost and the 600k signal. Slice 2 used 311k + 67k; this slice adds a model proposal and two approvals; headroom is 50k in A and zero in B | Section 3. Fresh spawn per stage, no resumes across passes (slice 1 processed 19.5M tokens, slice 2 6.2M, mostly from resumes) |
| R7 | The set is only about 15 to 16 questions: one question is about 6 points, so 80% needs 12 of 15 or 13 of 16, and a few questions decide it. A pass or fail is high-variance | Not a reason to change the bar (never after seeing results). Say so in the close-out; do not hide it |
| R8 | A pass is not a release. The reranker fixes ranking only; nothing here abstains. Decision 3 holds: nothing that writes text for a user ships before the check-step slice passes its own gate | Out of scope here; carried in B's close-out |
| R9 | Reading the sets by accident. The `evals/` directory sits in the repo | Constraint in section 8 |

## 8. What each downstream role must and must not do

**All roles.** One fresh spawn per stage; never resume an agent across passes (an infrastructure interruption resumes from its own partial artefact, per RUN_ECONOMICS section 6, and is not a retry). Write the artefact section by section. Targeted `Read` and `grep -n`, not wholesale reads; about 10 files for context at most. Read-only: `evals/retrieval.toml`, `evals/retrieval-heldout.toml`, `evals/retrieval-heldout-3.toml`, `evals/calibration-offtopic.toml`.

**Software Architect (Stage 2).**
- Must: write `02-tech-spec.md` and `docs/adr/0005-*.md`; propose one specific reranker (source, exact revision, file list, sizes, licence, why a cross-encoder of that kind), N (how many first-stage candidates), and how its score combines with the first stage (including a tie-break), each **argued on general grounds before any result and recorded as argued**; state how the model is tokenised and run with ONNX Runtime and numpy only; define the INV-4 and INV-5 deltas, with the **proposed INV-5 wording verbatim**; list the method files for the freeze, the exact expected file list against the section 4 cap, and the tests to add, retire or change (INV-enforcing ones by name); say how baseline `file-rrf-v1` stays runnable for slice B's diagnostics; write `02-approval-request.md` (A1 and A2, separately answerable); state what remains unknown (hashes, sizes) and who must supply it.
- Must not: **download, install, fetch or open any model file or website**; run `eval` or `retrieve` on any set; read or ask for any `evals/*.toml` file for the purpose of choosing the method (it may read `runs/docs-retrieval-2-proof/02-close-out.md` for the motivation; treat its five-miss list as context, not tuning data); touch `.agentic/SAFETY_INVARIANTS.md`; write product code; change the corpus, first stage, embedding model, bar or labels; propose a generative model, query rewriting, or a hosted API; choose anything by what scored well. Stop after writing the request.

**Backend Architect / Implementer (Stage 3), only after A1 and A2 are recorded as approved.**
- Must: implement exactly the approved model, revision and hashes; fetch only in `ingest`, hash-check before use, delete and fail on mismatch; add the offline-by-default tests (redirect refusal outside `hf.co`, short or non-40-hex revision rejected, hash mismatch rejected and deleted, cached file re-hashed, retrieve offline with the cache, the autouse network block intact); a tokenisation golden test; a rerank determinism test; first-stage-unchanged test (byte-identical first-stage output); tests on **synthetic fixtures**; apply the approved INV-5 text verbatim; update `LOCAL_COMMANDS.md` and `CURRENT_MVP_STATUS.md`; run the full regression after the last commit and report it; record the index sha256 and the method commit; commit locally.
- Must not: **run `eval` against any set, including the three earlier ones, and including a "quick sanity check"**; open any `evals/*.toml` file other than to see the schema through code; tune N, the combination or any threshold by looking at results (hand-check `retrieve` only on its own non-eval questions, and do not change the method from what it shows); add a dependency; widen the INV-5 wording or the file cap; push, open a PR, or merge; read or create the fourth set.

**Orchestrator.** Check `spent + estimate <= budget` before each spawn and update STATE.md's Next stage line first; the trace Model and Tokens columns come from `execution/usage.mjs`, never from agent self-reports; relay A1 and A2 verbatim and record the owner's own words; do not start Implementation without both; record the method commit at the freeze before the set exists; open slice B only after that.

## 9. Acceptance criteria (slice A exit, from the intent's "Done means")

- [ ] Starts from `main` (`file-rrf-v1`, 123-file corpus, pack v12): corpus, first-stage ranking and embedding model unchanged (a test and a diff of the unchanged files show it).
- [ ] A local reranker over the first stage's top-N, N and the score combination argued before any run; reads text, never produces text; one pinned revision, every file hash-checked, ONNX Runtime + numpy only, no PyTorch, no `trust_remote_code`; A1 and A2 recorded as approved in the owner's own words **before** anything was installed or downloaded.
- [ ] INV-4 enforcing tests pass at full strength; INV-5's enforcing tests extended to the new files and pass; `retrieve`, `eval` and the default suite are offline.
- [ ] Deterministic ingest (twice, same index sha256); provenance on every passage; no generative model.
- [ ] A way to score `file-rrf-v1` and the reranked method on the same sets exists and is tested on synthetic fixtures; it was not run on any `evals/` file in slice A.
- [ ] Full regression green after the last commit: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`, plus `uv run pytest -m model`.
- [ ] File count at or under the cap of 13; no `pyproject.toml` or `uv.lock` change (or a recorded approval).
- [ ] Freeze: the method commit SHA is recorded in STATE.md before any fourth set exists.

**Slice B owns (for its own Scope Review):** the fourth set (>= 15 answerable), B1 label review, B2 single scoring run (gate: a correct file in the top 5 for at least 80% of answerable), the three earlier sets and `file-rrf-v1` as diagnostics, Security, the Release Gate, close-out. If the gate fails: failure loop (cap 2); nothing ships; the next move is a new intent and a new fifth set.

## Context bundle for the Architect (paths only; about 10 files)

- `runs/docs-retrieval-3/intent.md`, `runs/docs-retrieval-3/01-scope.md` (this file)
- `.agentic/SAFETY_INVARIANTS.md` (INV-4, INV-5 and their enforcing tests), `.agentic/LOCAL_COMMANDS.md`
- `runs/docs-retrieval-2-proof/02-close-out.md` (sections 1 to 4)
- `docs/adr/0004-*.md` (the file-level method, for its format and for what the freeze covered)
- `docs-source.toml`; `aveto_support/search.py`, `aveto_support/ingest.py`, `aveto_support/embed.py` (targeted `grep -n` reads: how model files are pinned and hash-checked, and how WordPiece tokenisation is done)
- Tests: names only via `grep -n "def test_" tests/`
- `/Users/gopalpatwa/opt/agentic-sdlc-playbook/project-packs/ai-agent-product.md` ("Held-out gates")
- Commands: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`; `uv run pytest -m model` (`.agentic/LOCAL_COMMANDS.md`)
- **Do not read:** any `evals/*.toml`; `runs/docs-retrieval/` beyond what the close-out cites.

## Open questions for the next agent

- [ ] Which exact reranker, and can it be tokenised and run with ONNX Runtime and numpy alone? Resolver: Architect, then owner (A1).
- [ ] Who supplies each file's sha256 and size before A1 (section 5 gap)? Resolver: Orchestrator or owner; Architect states the need.
- [ ] Is reranking done on files or passages, and what is the score combination and tie-break? Resolver: Architect, argued on general grounds, before any result.
- [ ] Does `embed.py` need to change (shared tokenizer code)? Default: no. Resolver: Architect; a yes is a flagged exception.
- [ ] Does the eval file schema need to change? Default: no. A yes means the owner is told before the set is written.

## Escalation path

- More than the 13-file cap, or more than about 10 files of context: hand back to the Engineering Manager for a re-split.
- A new host, dependency, `trust_remote_code`, or any generative element: stop; write an approval request; wait for the owner's own yes through the Orchestrator.
- Failed gate or repeated failure: `FAILURE_LOOP.md` (2 retries, then the owner). Over budget: degrade, drop, or stop and ask with the numbers; never raise 330k or 270k.
