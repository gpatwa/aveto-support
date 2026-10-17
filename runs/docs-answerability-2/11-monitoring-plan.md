# 11-monitoring-plan — docs-answerability-2 (tier 3 post-launch monitoring plan)

> Owner of this plan: SRE Agent (fresh spawn), depth standard. Plan only: no code change, no judge spawn, nothing approved, nothing committed.
> Tier: 3, as ruled by the owner in `APPROVAL_RECORD-9.md`. This is the item `09-release-checklist.md` ("Post-launch monitoring") said was absent.
> Source of every figure: `05-seen-check.md`, `07-gate-scoring.md`, `09-release-checklist.md` (copied, not re-derived). Not opened, by the brief: `evals/retrieval-heldout-5*.toml`, `batch-2.txt`, `q/`, `06-label-review.md`, any `diffs.md`.
> Status of numbers: **thresholds below are my proposals, derived from the recorded figures. The owner sets the final ones.** A threshold the owner has not confirmed is a default, not a commitment.
>
> **Adopted (added 2026-10-17 by slice `land-answerability`, T5).** The owner adopted the thresholds (section 1), the cadence (sections 2 and 4) and the stop rules (section 2) in this plan **as written**, in Charter C8.5 of `runs/land-answerability/CHARTER.md`, approved by Gopal Patwa (operator) in `runs/land-answerability/APPROVAL_RECORD-1.md` (2026-10-17; time of day not recorded). The owner also adopted the standing mitigation: **"stop typing `/aveto-judge`, use `retrieve` alone"**. The text below is unchanged from the SRE's draft; "my proposals" above is the history, and the owner's adoption is this note. Sections 2 and 5 are copied to `docs/runbooks/answerability-judge.md`.

## 0. What "monitoring" means here, stated plainly

There is no service, no server, no telemetry, no dashboard and no on-call. Nothing is deployed. After the branch is merged and used, the only things that exist are: the operator's own attended Claude Code session; the offline program (`retrieve`, `judge-input`, `judge-apply`, `eval --verdicts`); `tools/judge_run.py` (read-only audit of transcripts the operator's own session already wrote under `~/.claude/projects/`); the committed tests; and the frozen method (`bca0e403a69a5cda7826ea36897734bc63dc7b87`).

So "monitor" means: **what the operator looks at after each use, and what the owner re-checks on a calendar and on named events.** Everything is read by a human from a terminal or a transcript directory. This plan proposes no collector, no dashboard, no alert, no API key, no credential, no new service, and nothing on Azure. If a signal below cannot be read with an existing command, the plan says so and marks it "not observable" rather than inventing a way.

SLO language, kept honest: this slice has no user-facing availability surface, so I define **no availability SLO and no error budget**. The nearest thing to an SLO is the pair of registered bars, which are measured once, offline, not continuously. I do not dress them as SLOs. What replaces an error budget is the stop rules in section 2.

## 1. Signals, where each is read, and what trips an alarm

"Operator" reads it at use time. "Owner" reads it at the periodic check (section 2). Baselines are the recorded figures.

| # | Signal | Where it is read (existing command or place) | Baseline (recorded) | Watch | Stop (see section 2 for the action) |
|---|---|---|---|---|---|
| 1 | **Judge error rate** (exit 4, stdout `judge error`, one fixed category on stderr) | The terminal after each `judge-apply`; the operator keeps a tally. For a batch of transcripts, `uv run python -m tools.judge_run diagnostics ... --audit ...` prints `judge errors` and `judge error categories` | 0 in 96 spawns (48 at each stage) | Any 1 in a session | 2 in the last 10 uses, or any category that is not an empty reply during a usage-window end (the skill already writes an empty file for that case, so that one is expected and is the only benign cause) |
| 2 | **Abstain rate** (`no confident match` printed) | Operator tally per use | Not a rate of real use: the held-out set is 50% unanswerable by construction. Over-abstention is the stable number: 3/19 (15.8%) on stage 7, 4/28 (14.3%) on stage 5 | Over-abstention is only knowable when the operator already knows the answer is in the docs. Then: 4 abstains on the last 10 such questions (about 5% chance if the true rate is 15%) | 5 of the last 10 such questions (about 1% chance at 15%). This is a screening rule on a tiny sample, not a statistical test. Say so when reporting it |
| 3 | **ANSWERABLE rate** | Same tally (judge-apply prints the `Deciding signal:` line naming the verdict and prompt hash) | Not a meaningful stand-alone number (depends on question mix). The informative failure is **ANSWERABLE on a question the docs do not answer**: 0/24 unanswerable on stage 7, 0/20 on stage 5, 1/5 when the right file was missing (g19) | Any ANSWERABLE where the operator can see the shown passages do not answer the question | 2 such cases in the last 20 uses (bar 1 was 100%, so a second is a real change; it is also the failure that matters most: a wrong file shown). Do not average it away |
| 4 | **Offered tool count in a judge transcript must be 0** | `uv run python -m tools.judge_run check-transcripts <subagents-dir>` on the session's `subagents` directory (`~/.claude/projects/<project-slug>/<session-id>/subagents`). It prints offered tools per spawn | 0 on all 96 batch spawns and the smoke | Never non-zero | **Any non-zero. Zero tolerance** (INV-4: no `tools` entry, deny list, hook). Also stop on a model other than `claude-sonnet-5-5` |
| 5 | **`tool_use` must be 0** | Same command, same output | 0 on all spawns | Never non-zero | **Any non-zero. Zero tolerance.** The hook refusing every tool call has never fired (0 tools were ever offered); a tool call in a transcript means the pin has failed |
| 6 | **Base-dir line form** (length and layout; the tool prints "base-dir line length" and "layout ok") | Same command | 137 and layout ok on all 96, **in this worktree path**. The length depends on the checkout path, so a different checkout has its own baseline: take it from the first clean `check-transcripts` run there and record it | Layout not ok | Layout not ok, or length changes in the same checkout with no path change. It is the cheapest sign the harness changed what it injects (see signal 9) |
| 7 | **Model ID pinned, and available** | Pinned: `.claude/agents/aveto-answerability-judge.md` line `model: claude-sonnet-5-5`, guarded by `tests/test_judge_artefacts.py` (`uv run pytest tests/test_judge_artefacts.py`). Available: **not probeable offline**. The only evidence is that a spawn works. Read the `model` field in `check-transcripts` | `claude-sonnet-5-5` on 96/96 | A spawn fails or returns an empty reply (signal 1) | A different model in a transcript; the provider announces deprecation or replacement (section 3 trigger). A failed spawn is read as "unavailable until shown otherwise", not retried in a loop |
| 8 | **Prompt hash unchanged** | Every judged output ends with `Deciding signal: ... (prompt answerability-judge-v1, sha256 24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427)`. Tests pin it (`tests/test_judge.py`, `tests/test_judge_artefacts.py`) | `24b244d2...a159427` | Any other hash in output | Any other hash. The prompt is the thing the bars measured |
| 9 | **INV-5 session-context drift** (what the harness attaches to the judge changes with Claude Code updates) | **Cheap proxy, offline:** signals 6 and the usage figure in signal 10, from `check-transcripts`. **Full re-measure:** repeat `01-measurement.md`'s method (spawn on a public eval question, read the judge's first request from the transcript). That spawn sends data, so it is an attended, owner-worded action under rules 4 and 6 and is never run silently | Measured 2026-10-12: first request 14.2k tokens, of which about 2.7k were not itemised; contents listed in INV-5 | Peak per spawn outside the recorded band, or layout change, after a Claude Code update | Any item in the context that INV-5 does not list, or a change in the form of the injected lines. Then the INV-5 list is stale and the owner decides (section 3) |
| 10 | **Usage-window cost per judge run** | `check-transcripts` / `diagnostics` print peak per spawn and a sum | Peak per spawn about 7.4k to 14.3k (smoke 7,784; batch sums 378,696 over 48 spawns = about 7.9k mean at stage 5 and 410,748 = about 8.6k mean at stage 7) | Mean above 14.3k | A single spawn above about 20k (more than 1.4 times the recorded peak). It is not a cost alarm in money (the operator's subscription window, no API); it is a context-growth alarm for signal 9 |
| 11 | **Retrieval hit rate drift** (docs corpus or index changes) | `uv run python -m aveto_support eval --eval-file evals/retrieval.toml` (dev set, offline). Read the `answerable:` line and the exit code | Dev set **19/24 = 79.2%, exit 1 by design**. The fifth set was also 19/24 = 79.2% (misses g05, g06, g18, g19, g22), exit 1, **not a registered bar** | Same 19/24 | **Below 19/24 (18/24 = 75.0% or lower)**, a different miss list on an unchanged corpus pin, or a newly different exit code. Retrieval is deterministic on a pinned commit and index, so on an unchanged pin any difference means something other than the docs changed (model cache, dependency, index). A *better* number is also reported and not celebrated: it is a retrieval change and goes to section 3 |
| 12 | **Corpus pin and index** | `docs-source.toml` `commit = 3a83b669a8b53dfdff869a1bbe361bdb156e3a13`; `index/docs-index.json` is built by `ingest` against it (an index built by other parameters makes `retrieve` exit 2) | Pin above | Pin edited, or `ingest` re-run | Any edit to the pin (section 3, corpus trigger) |
| 13 | **Deny list and hook still the pinned text** | `.claude/agents/aveto-answerability-judge.md`: `disallowedTools` (ends in `mcp__*`, includes the seven tools D1 added), the `PreToolUse` hook line `echo "aveto-answerability-judge has no tools" >&2; exit 2`, no `tools:` line. Guarded by `tests/test_judge_artefacts.py` | As pinned (record 7 applied D1) | Test failure | Any failure of that test, or a diff to that file that is not an owner-worded rule 4 change |
| 14 | **Frozen method unchanged** | `git diff bca0e403a69a5cda7826ea36897734bc63dc7b87 -- <method files>` must be empty for the files the freeze record lists; the key's first 3,071 bytes must hash to `33109e85dd6a62ac099849cf3ddc2a8fdf090e54f355ba768a5b2a82c1ca5c38` (`head -c 3071 runs/docs-answerability-2/judge-check/key/key.toml \| shasum -a 256`; it is a prefix because 48 rows were appended, which R8 allows) | Empty diff at `69fd907` (QA); D6 touched only the three probe scripts | Non-empty | Any non-empty diff on a method file, or a different prefix hash: the registered figures no longer describe the code |

What cannot be observed, so no signal is claimed:
- **Whether the operator path behaves like the measured eval path.** Stages 5 and 7 used the eval path (fixed payload per run id). The operator path (`/aveto-judge`) has the main session retype the payload into the judge prompt (spec 14.1). Its accuracy was **never measured**. The recorded bars are for the eval path only. `judge-apply`'s input hash binds the verdict to the payload the program built, not to what the judge saw. The only evidence the operator can collect is `check-transcripts` on their own runs: it prints the payload attribution, and a payload that matches no key question is expected on the operator path (the key lists eval ids only), so this is **not checkable** and I do not pretend it is. State this limit whenever a result from real use is quoted.
- **Whether the hook runs.** Zero tools were ever offered, so it never fired (INV-4, INV-5, R-E). Signals 4 and 5 are the real control.
- **Model availability ahead of use**, as above.
- **Real accuracy on real questions.** The operator has no ground truth except their own knowledge of the docs. Signals 2 and 3 are screening rules, not measurements.

## 2. Periodic re-check protocol (offline, operator runs it, owner reads the result)

**Cadence:** every four weeks while the judge step is in use, and also immediately on any trigger in section 3. If the judge step has not been used for four weeks, run only items A and B; skip C and D.

Run from the repo root of the checkout in use. Record the date, the commit (`git rev-parse HEAD`), the Claude Code version string the operator sees, and each item's result as a short note in a file the owner chooses. **Do not paste question text, passage text or reply text into that note.** Counts, hashes and exit codes only.

| Step | Command or action | Pass | On breach |
|---|---|---|---|
| A. Regression | `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest` (local, no network) | mypy clean; ruff all checks passed; pytest 375 passed, 12 deselected (the figures at release; a *higher* passed count after a deliberate change is fine, any failure is not) | Any failure: **stop using the judge step**, do not "fix forward" in the same session, tell the owner. Known and accepted: `uv run pytest -m model` has 1 failing test (`test_sample_derivation_reproducible`, R-D); that is not a breach and is not in the regression command |
| B. Pins | `uv run pytest tests/test_judge_artefacts.py tests/test_judge.py`; `git diff bca0e403a69a5cda7826ea36897734bc63dc7b87 -- .claude/agents/aveto-answerability-judge.md aveto_support/judge.py` (read the diff by eye against the freeze record; D1 is the one recorded owner-approved change to the agent file and `DENY_LIST`, so the agent-file diff is expected to show exactly that and nothing else); key prefix hash from signal 14; `docs-source.toml` commit equals `3a83b669...` | All pass; diffs equal the recorded ones; hashes match | **Stop.** An unrecorded change to a pinned file is a safety-control matter (rule 4). Revert it only with the owner's words; tell the owner |
| C. Real runs | Pick the last 3 sessions in which the judge ran. `uv run python -m tools.judge_run check-transcripts ~/.claude/projects/<project-slug>/<session-id>/subagents` for each. Read: model, offered tools, `tool_use`, base-dir line length, peak per spawn | Model `claude-sonnet-5-5`; offered tools 0; `tool_use` 0; layout ok; length equal to this checkout's baseline; peak in 7.4k to 14.3k | Offered tools or `tool_use` non-zero, or another model: **stop using the judge step immediately**, do not run `/aveto-judge` again, tell the owner the same day. Layout or peak out of band only: **pause** (finish nothing new), run the full re-measure of signal 9 with the owner's word, tell the owner |
| D. Tally | Read the operator's tally for the period: judge errors, abstains on known-answerable questions, ANSWERABLE on known-unanswerable ones | Signals 1 to 3 below their Stop column | Meet a Stop value: **stop using the judge step**, fall back to `retrieve` alone (the pre-slice behaviour, which never abstains and is unchanged), tell the owner. Meet a Watch value only: keep using, note it, tell the owner at the next check |
| E. Retrieval | `uv run python -m aveto_support eval --eval-file evals/retrieval.toml`, read the `answerable:` line and exit code | `19/24 (79.2%)`, exit 1 | Below 19/24, or a different exit code: **do not rebuild the index to chase it.** Stop using the judge step until the owner decides, because the judge's behaviour was measured on this ranking only. Tell the owner |
| F. Standing open items | Check the S5/S6 status in section 7 | Matches the owner's last recorded decision | A change nobody recorded: tell the owner |

**Stop means:** the operator does not invoke `/aveto-judge`. `retrieve` stays usable alone. The operator does not delete, edit or revert anything on their own for a safety-control file. **Revert means** section 5, and a revert that returns INV-4 and INV-5 to their pre-slice text needs the owner's own words in the driving session first (rule 4). Nobody infers that approval, and no agent does.

**Who is told, and how:** the owner, in the session driving the work, in plain words: what was run, what was seen, which Stop or Watch value it met. There is no pager and none is proposed.

What is explicitly **not** a breach: the retrieval gate exiting 1 on `evals/retrieval.toml`, the failing `-m model` test, and over-abstention at the recorded 14 to 16%.

## 3. Re-evaluation triggers: each needs a new pre-registered check, not a reused result

The slice's figures describe one model, one prompt, one pinned corpus, one retrieval ranking, one harness behaviour, one set. A change to any of them makes the old bars unevidenced for the new state. **A reused result is not evidence for a changed system.** For each trigger below the owner and operator follow this order, none of it automatic:

1. Stop using the judge step (retrieve alone remains).
2. A new slice is planned (Orchestrator), with new bars registered **before** any run, a **new** held-out set (the fifth set is spent and cannot be rescored, and its source-file overlap with earlier sets, D4, already flatters bar 2), and the owner's rule 4, 5 and 6 words where they apply.
3. The judge step resumes only on a recorded owner decision.

| Trigger | Why it invalidates | Notes specific to this trigger |
|---|---|---|
| **Model deprecation, replacement or alias change** for `claude-sonnet-5-5`; or the operator proposing any other model | Rule 5 approval (record 2) is for that exact ID; the bars are for that model | Changing the ID in the agent file is a rule 5 and rule 4 matter. Watch the provider's deprecation notices the operator already receives; nothing here polls for them |
| **Prompt change** (`answerability-judge-v1` hash changes) | The bars measured that prompt | Includes any edit to the three-line system prompt or the payload layout |
| **Corpus pin change** (`docs-source.toml` commit or `include` list) or **re-ingest to another commit** | Retrieval, the passages shown and the 79.2% change | The index and eval sets are built against the old pin |
| **Embedding model, reranker, ranking name or a dependency in `uv.lock` that affects ranking** | Same | `file-rrf-v1` is the measured ranking; `file-rerank-v1` was not judged |
| **Claude Code version change** (including harness, desktop app or a changed subagent transcript format) | INV-5's context list was measured on one version; the transcript reader (`read_spawn`) fails closed on a changed format; the `tools` omission, deny list and hook behaviour are harness behaviour | First action after an update is item C and the signal 9 proxy. Whether to pay for a full re-measure (a data-sending spawn, owner's word) is the owner's call |
| **Any edit to INV-1 to INV-5** (`.agentic/SAFETY_INVARIANTS.md`) | Safety-control text (rule 4) | The check is a fresh read of what changed against what was measured |
| **Change to `.claude/agents/aveto-answerability-judge.md`, either skill, or `settings.local.json`** | Permission and tool boundary | Includes the S5 and S6 fixes themselves (see section 7) |
| **Question mix changes materially** (a different docs set, language, or the operator starts using it on non-documentation questions) | Bars measured one kind of question | Not detectable by a command; operator and owner judgement |
| **Any `judge error` category or tool offered/used event** | See Stop values in section 1 | Not a calendar trigger, an immediate one |

## 4. Owners and cadence

| Who | Owns | Cadence | Cannot do |
|---|---|---|---|
| **Owner** | The thresholds in section 1 (these are proposals until set), the Stop decisions that touch a safety control, S5/S6, the tier, every rule 1 to 6 approval, whether to resume after a Stop, any push/merge | Reads the period note from section 2 every four weeks; decides on every Stop within the same session it is raised | Delegate an approval to an agent or another session. An approval counts only when typed by the owner in the session driving the action |
| **Operator** (the person typing `/aveto-judge`; today the owner may be both, in which case the roles are still kept as separate steps in the note) | Running `/aveto-judge` attended, the per-use tally, section 2 steps A to F, stopping when a Stop value is hit | At each use (tally); every four weeks (protocol); on every trigger | Run it unattended, scheduled, in a loop, through `claude -p` or an API. Make a safety-control change on their own authority |
| **Post-Launch Learning Agent** | Reading the period notes after the owner shares them; proposing carry-forward (R-C advisories, R-D test fix, QA's proposal on `ruff` over `runs/`) | When the owner gives it a note, not before | Collect data; read transcripts on its own |
| **SRE Agent** | This plan; reviewing it when a trigger fires | On a trigger, not a calendar | Page, deploy, change a threshold without the owner |

There is no on-call rotation, because there is nothing to be paged about: the only person affected by the step failing is the operator, who is present when it fails, because the step is attended only.

## 5. Runbook and rollback

This is a short runbook for someone who did not build the slice. A product-repo copy in `docs/runbooks/` is **not** written here: this brief and the owner's instruction limit me to this one file, and the copy would be a repeat of this section. **Open item for the Orchestrator and owner:** the role brief puts runbooks in `docs/runbooks/` so they reach whoever uses the repo without the run record; a follow-up (Tech Writer) should copy sections 2 and 5 there. I did not do it, and I do not count its absence as done.

**Detect:** a Stop value in section 1, or a failed step in section 2.

**Diagnose, in this order (all offline, none sends data):**
1. `git status` and `git rev-parse HEAD`: is the tree the one you think it is?
2. `uv run pytest tests/test_judge_artefacts.py tests/test_judge.py`: are the agent pin, deny list, hook and prompt hash intact?
3. `uv run python -m tools.judge_run check-transcripts <subagents-dir>` on the failing session: model, offered tools, `tool_use`, base-dir line, peak.
4. `uv run python -m aveto_support judge-input --question-file <file>` (prints the payload, sends nothing) and compare with what the judge was given.
5. Judge error: read the one fixed category on stderr (the stderr message is the diagnosis; the program never prints the reply).

**Mitigate (the operator may do this alone, it is a pre-authorised, named step):** stop typing `/aveto-judge`. Use `retrieve` alone. No file changes. This is the one mitigation I pre-authorise, because it changes no production state and is reversible by simply resuming.

**Rollback (every item below beyond "stop" needs the owner; paths from spec section 13 and `09-release-checklist.md` "Rollback plan", checked against the tree):**
1. **Before any merge:** do not merge, or `git revert` the slice commits on the branch in reverse order.
2. **After a merge, disable the operator path only:** `git rm -r .claude/skills/aveto-judge/` and commit. The operator can no longer start the judge. `judge-input` and `judge-apply` stay offline and inert without a reply; `retrieve` is not in the diff against `main` and is untouched. **Also consider `.claude/skills/aveto-judge-seen/`** (the eval-only skill, S5): removing it is the same kind of `git rm -r`, and it is the safer default if S5 is not fixed. That is the owner's decision (section 7).
3. **Full revert:** `git revert -m 1 <merge-commit>`, then the regression (section 2 step A). Assumes a merge commit; if the owner squashes or fast-forwards the revert target differs and must be named at merge time. **INV-4 and INV-5 return to their pre-slice text, a rule 4 change: the owner's own words first, never an assumed approval.** README and `CURRENT_MVP_STATUS.md` revert with it.
4. **D1 only (the seven harness tools in the agent file and `DENY_LIST`):** it is a **separate hunk**, applied by `git apply` of the fenced diff in `runs/docs-answerability-2/03a-d1-proposed-diff.md` (record 7). Reverse with `git apply -R` of that same diff, only with the owner's approval (it narrows a deny list, so it is a safety-control change). Then `uv run pytest tests/test_judge_artefacts.py`, then a fresh-load session before any spawn. Correction carried from the release checklist: the spec's `D1-diff.md` does not exist; that file is the right one. Reversing D1 alone leaves the agent with a shorter deny list and still no `tools` entry; whether to do that instead of stopping is the owner's decision, and I advise stopping instead.
5. **Eval data only:** `git rm -r runs/docs-answerability-2/judge-check/`. No product effect.
6. **Outside git:** `.claude/settings.local.json` (S6) is gitignored and in no commit; no git rollback removes it. Removing it is the owner's. Transcripts in `~/.claude/projects/` are the owner's session data; no rollback touches them.
7. The program writes nothing persistent except `.aveto-judge/` (gitignored; deleted on every `judge-apply`; a symlink there survives, S2).

**Rollback is tested, not assumed:** what was tested is only that the paths named exist, that the pre-merge revert is trivial, and that the pin tests would fail on a changed agent file. **No revert has ever been rehearsed.** I propose one rehearsal on a throwaway branch as a first item for the owner (a `git revert` of the slice commits plus the regression, nothing merged), and I record that it is proposed, not done.

**After any Stop or rollback, the review:** write what happened, which signal tripped, the 2 to 5 system conditions, and at least one **preventive** (not just mitigative) action, with an owner and a date, using `templates/INCIDENT_REVIEW_TEMPLATE.md` in the playbook. No person is named as the cause.

## 6. What is NOT monitored, and why

- **Unattended, scheduled, API or `claude -p` use.** Not monitored because it is not permitted (rule 5, records 2 and 3: attended only). If the transcript directory ever shows a judge spawn nobody typed, that is a breach in itself: tell the owner.
- **No server telemetry, no usage analytics, no error reporting, no uptime check.** There is no server. Nothing here sends the operator's questions, passages or replies anywhere, and **I propose no collection of any user data or content.** The usage figure in signal 10 is read from the operator's own local transcripts, by the operator, and never leaves the machine.
- **No question or reply text is recorded in the period note.** The tally holds counts. The audit tools already avoid printing reply text; the plan keeps that property.
- **The provider's side.** What Anthropic retains or does with the session context is outside this repo and is governed by the owner's account terms. DPA and vendor-risk status are still an open owner item (C5c in `09-release-checklist.md`); this plan neither states nor assumes it.
- **Anything the harness does for its own purposes** (INV-5: outside the invariant and not measured).
- **The operator path's accuracy** (section 1, "cannot be observed").
- **Whether the owner's real documentation questions resemble the eval set.** No instrument for it.
- **Cost in money.** The operator's subscription; there is no metered API and none is to be added.

## 7. Known open items to watch

Owner-held; this plan does not resolve any of them and does not choose for the owner. "Watch" is what to look at; "Retire the item when" is what the owner records.

| Item | State at this plan | Watch | Interim rule |
|---|---|---|---|
| **S5** quote breakout in `.claude/skills/aveto-judge-seen/SKILL.md` (`'$ARGUMENTS'` in a shell line) | Required-fix, undecided. Whether the harness escapes `$ARGUMENTS` was never tested offline | That the skill is not invoked (a `/aveto-judge-seen` use in any transcript is a finding); any edit to the file (a fix edits a frozen method file and voids the freeze for further eval use, a section 3 trigger) | **`/aveto-judge-seen` is not used until S5 is fixed.** The owner decides fix, disable (`git rm -r` of the skill directory) or accept. Prefer a decision before any further use of this repo's sessions |
| **S6** `.claude/settings.local.json` rule `Bash(uv run -q --project * python * seen_payload.py *)` | Required-fix, undecided, gitignored | That the file exists, its size and content (`wc -c .claude/settings.local.json`; recorded 87 bytes), at each check. A larger file or a changed rule is a finding | Owner records: deleted, narrowed, or kept as an accepted risk. While it exists, INV-5's "acts under its own permission prompts" is weaker than stated for sessions opened in this worktree |
| **S1 to S4, S7, S8** (advisories: question echo, symlink `reply.txt`, passage text imitating payload structure with Cc/Cf characters, any model can spawn the judge with an override, bare `no confident match` from a crafted question, a stale docstring citation) | Advisory, carry-forward (R-C) | S4 is the one with a signal: a judge transcript whose model is not `claude-sonnet-5-5` (signals 4, 7). S2: a leftover `.aveto-judge/reply.txt` that is a symlink (`ls -l .aveto-judge/`). S3: unusual characters in a shown passage after a corpus change (section 3 trigger anyway). S1, S7, S8: none | Carry forward to the close-out / a later slice |
| **One-question margins** (bar 2 passed 24/28 against needed 23, and 16/19 against needed 15 (80%): one fewer correct would have failed each) | Accepted by the registered design (R-B) | Over-abstention staying near 14 to 16% (signal 2). A single over-abstention more or fewer in real use is within noise; do not read a single case as a trend | The plan's stop rule for it is 5 of the last 10, and it is deliberately loose because of the denominator. It is not a re-test of the bar |
| **Retrieval gate exit 1** (19/24 = 79.2%, five misses on the fifth set; end-to-end 16/24 = 66.7%) | R-A: the owner to accept in their own words or declare relevant | Signal 11 | Do not describe the product as answering questions; the judge cannot repair a retrieval miss |
| **D6 lint exemption** (`# ruff: noqa` on three probe scripts), **C4a final-tree run by a session with a shell** | Listed in the checklist | That step A still passes; that `pyproject.toml` has gained no `exclude` | Owner's veto by exception |
| **R-D model-marked test** failing by design | A later slice | `-m model` red by exactly 1, not 2 | Not a breach at 1 |
| **R-E** hook-never-fired; session-context list not complete | Disclosed | Signals 4, 5, 9 | Zero tolerance on 4 and 5 |
| **Approval record gaps** (approver identity, time of day, DPA line, STATE out of date) | `09-release-checklist.md` C5 | Owner's own record | Not a monitoring signal; listed so it is not forgotten |
| **Release action itself** (push/merge/deploy) | None requested or recorded. `APPROVAL_RECORD-9` rules the tier only | That nothing is pushed or merged on an agent's say-so | Rule 3: the owner's typed yes in the driving session |

## 8. Honest limits of this plan

- The thresholds are small-sample screening rules, set against 19 to 28 questions per stage; they will have both false alarms and misses. Their purpose is that the owner decides on evidence rather than on a feeling.
- Model availability and the harness's behaviour cannot be probed without sending data, so those two are read from failure, not predicted.
- None of the section 2 commands has been run by me; I ran only read-only listing and file reads, and no judge spawn. Every figure is copied from the artefacts named at the top; the corpus pin, agent-file lines and skill text were read from the tree in this session. The key prefix hash is copied from `09-release-qa.md`, not recomputed, and the key path `judge-check/key/key.toml` is taken from that file.
- The plan has no way to see problems the operator does not notice. That is why the judge stays attended, and why a quiet period proves nothing.
- Done is not claimed: the `docs/runbooks/` copy, the revert rehearsal and the owner's confirmation of the thresholds are all open.

## Handoff

- **To the owner:** confirm or change the thresholds in section 1 and the cadence in section 4; decide S5, S6; decide whether to do a revert rehearsal; the release action stays yours and is not requested here. This plan approves nothing.
- **To the Orchestrator:** record this stage; a Tech Writer follow-up to copy sections 2 and 5 into `docs/runbooks/`; STATE is yours to update (I did not touch it).
- **To the Post-Launch Learning Agent:** only after the owner shares a period note.
