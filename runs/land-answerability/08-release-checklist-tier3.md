# Release Checklist, Tier 3 — land-answerability (stage 9: Release Manager, fresh spawn)

> Owner: Release Manager Agent (fresh spawn; wrote, built, reviewed and scored none of this slice). Depth: standard. Nothing here is an approval.
> Tier: **3** (Charter C7.2, not lowered; owner's ruling `APPROVAL_RECORD-9` of slice `docs-answerability-2`). Re-derived below: it stays 3 and the code-review tier stays High.
> Worktree `/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/land-answerability`, branch `claude/land-answerability`. Freeze `bca0e403a69a5cda7826ea36897734bc63dc7b87`.
> **HEAD at the start of this spawn: `653ecddeae50675e18602065bc8ab60fecab7e51`** (worktree `logs/HEAD`). **Final-tree QA ran at `e2b228eaf01d9732be54e3268c0ca9265d77f0f9`** (`07-final-tree-qa.md`). See T6 for the two commits between them.
> Read: `.agentic/*`; `intent.md`, `CHARTER.md`, `charter-check-output.txt`, `APPROVAL_RECORD-1.md`, `00-slice-plan.md`, `STATE.md`, `trace.json`, `code-review.md`, `01-s5-fix.md` to `07-final-tree-qa.md`; from slice 7 `13-release-checklist-tier3.md`, `11b-vendor-risk.md`, `11c-change-request.md`, `11-monitoring-plan.md`; `README.md`, `.agentic/CURRENT_MVP_STATUS.md`, `docs/runbooks/answerability-judge.md`, `.claude/skills/aveto-judge-seen/SKILL.md`, `tests/test_judge_seen_skill.py` (lines 1 to 215), `.claude/settings.local.json`; playbook `docs/RELEASE_GATES.md`, `docs/HUMAN_APPROVAL_RULES.md`, the checklist template.
> Not opened, by the slice's own limits: `evals/retrieval-heldout-5*.toml`, `judge-check/` labels, any `diffs.md`.

## 0. What I ran, and what I could not

I have Read, Write, Edit, Grep and Glob. **No shell.** I ran nothing; I read recorded output.

| Item | How I know |
|---|---|
| `uv sync --locked`, `mypy`, `ruff check`, `pytest` | Not run by me. Recorded by QA at `e2b228e`: exit 0, 24 source files clean, ruff clean, **425 passed, 12 deselected**, stable over 3 runs (`07-final-tree-qa.md` section 1). I rely on that report; it is not mine. |
| `git diff` of any kind | Not available to me. Where a claim below needs a diff I name who recorded it (QA checks a, b, d; Security 1.1) or say it is indirect. |
| HEAD and commit list | Read from `/Users/gopalpatwa/opt/aveto-support/.git/worktrees/land-answerability/logs/HEAD` and `HEAD` (branch ref). |
| `main` | `.git/refs/heads/main` = `132b548abd1d50433ae4e6c31d96f3c22714cca5`, the base of the rollback rehearsal (`02`). Unmoved. `refs/remotes/origin/main` is the same value. |
| Pushed? | **No.** There is no `refs/remotes/origin/claude/land-answerability`. (`origin` already holds a `claude/docs-answerability-2` ref; I did not compare its value.) |
| Judge spawn, network, API | None. |

## 1. Tier classification and Charter verification

**Tier 3 stands.** The slice changes `.claude/skills/aveto-judge-seen/` (a skill whose `!` line runs a shell command, a permission surface), lands on `main` a judge that sends data to a third party through the operator's session, and ends in a push and a pull request. Charter C7.2 fixes the tier and forbids lowering it.

**Risk tier re-derived from the change (`CODE_REVIEW.md` section 2).** The diff against `main` touches: `.agentic/SAFETY_INVARIANTS.md` (INV-4, INV-5 rewritten in slice 7, records 5 and 8), `.claude/agents/aveto-answerability-judge.md` (model line, deny list, hook), `.claude/skills/aveto-judge-seen/` (a Charter C5.3 line), a processor line (Anthropic, C4.1). All are named in the High row ("safety invariants, hooks, permission rules or settings, deny lists, ... a model or processor line, ... anything a Charter line (C5.x) names"). **High, as `code-review.md` recorded; not higher (there is no higher row).** The High requirement "a rollback is rehearsed before it is offered" is met by `02-rollback-rehearsal.md`; "the owner reads the change itself" is the owner's at the end review (section 12).

**Charter verification (Process v2).**

| Check | Result |
|---|---|
| `APPROVAL_RECORD-1.md` holds the owner's verbatim approval naming the file and its sha256 | **Yes.** "I approve runs/land-answerability/CHARTER.md, sha256 `5cb44338417a13038e29d6bf9f12320c9367f5199847ccb6680385d31cc976fb`, with plan 450k, ceiling 600k, hard cap 750k. Intent and plan confirmed; run to the end." Approver Gopal Patwa, in the driving session. Time of day not given; the Orchestrator did not invent one. |
| `charter-check-output.txt` shows the same sha256 and "charter complete" | **Yes.** `charter complete: runs/land-answerability/CHARTER.md` / `sha256 5cb44338417a13038e29d6bf9f12320c9367f5199847ccb6680385d31cc976fb`. Identical to the approval record, the `STATE.md` header, `trace.json` and `11b`. I cannot recompute the hash (no shell); I compare the recorded strings. |
| Gated actions cite a Charter line that names them exactly | **Charter side: yes.** C5.3 (the skill change, bounded to the `!` line and the tests), C8.2 and C8.3 (push of `claude/land-answerability` and a PR into `main`; "never merge, never deploy, never send"). **Record side: gap.** `STATE.md` Approvals table holds one row, "Approve the Charter ... PENDING", and no row citing `CHARTER.md#C5.3` or `#C8.2`; `trace.json` carries one combined approval entry naming both lines. Required fix (condition C-2, section 10). |
| C1.1 and C1.2 hashes (intent, plan) | Not recomputed by me. `intent.md` and `00-slice-plan.md` still carry their "Draft"/"Proposed; not confirmed" banners because they are hash-locked; the confirmation is the sentence in `APPROVAL_RECORD-1`. Noted, not a defect. |
| `code-review.md`: every finding fixed or carried with a reason | **Yes.** One finding, F1 (Important): fixed (`ad181ee`). Deviation from the Charter's C6.P wording is discussed in section 5. No unaddressed correctness finding. |
| Budget (C2) | `STATE.md`: spent 464k (103% of the 450k plan, 77% of the 600k ceiling, 62% of the 750k cap). Ceiling and cap not reached; this stage's 60k estimate lands near 524k, still under the ceiling. The 14k plan overrun draws on nothing the Charter forbids. The figures are self-reported (`trace.json` `telemetrySource`), and its per-stage `toolCalls` of 0 are not measurements. |

## 2. T1 to T11, one by one

Legend: **MET** / **MET WITH GAPS** / **WAIVED** (the owner accepted the limitation in the Charter; the item is not met) / **NOT MET**. "Scope" says what the status covers. The T text is from `runs/docs-answerability-2/13-release-checklist-tier3.md` section 8.

| # | Item | Status | Evidence | What the status does and does not say |
|---|---|---|---|---|
| **T1** | Owner's approval of the release action | **MET WITH GAPS**, scope: the push and the PR only | `CHARTER.md` C8.2, C8.3; `APPROVAL_RECORD-1.md` | See T1 decision below. |
| **T2** | Change request decision recorded | **MET WITH GAPS** | `runs/docs-answerability-2/11c-change-request.md` Approvals table, human owner row; `05-docs-note.md` | The row now reads APPROVED "as given by the Charter ... approve landing by pull request into `main`; the merge is the owner's own act and is not covered", Gopal Patwa, 2026-10-17, tested rollback yes. Gaps: time of day not recorded; the Release Manager row and the Compliance approver row are still **PENDING**; the body of `11c` is slice 7's draft and is stale (it still lists S6 and S5 as open, C4(a) as open, and "Tested? no"). The decision is recorded; a reader of the body alone would be misled. The Release Manager row stays PENDING because I sign off opening a PR, not a landing. |
| **T3** | Vendor risk: DPA | **WAIVED** (owner-accepted limitation). **Not MET.** | `CHARTER.md` C4.1; `03-vendor-risk-note.md`; `11b-vendor-risk.md` ("Update from the Charter") | See T3 decision below. |
| **T4** | Rollback rehearsed | **MET** | `02-rollback-rehearsal.md` | On a throwaway worktree and branch, a simulated `--no-ff` merge onto `main` (`132b548`) then `git revert -m 1`: clean, tree `ac20066039c43be60999f1651d6da4a915f00c36` identical to `main`, then `uv sync --locked`, `mypy`, `ruff check`, `pytest` (168 passed, 10 deselected) each with its own exit code. Branch and worktree removed (cleanup proof recorded); landing branch untouched. Limits, all stated by the rehearsal and all still true: only step 3 of the plan was rehearsed (not step 2, the `git rm -r .claude/skills/aveto-judge/` disable); a squash or fast-forward merge changes the revert target and is **not covered**; it ran against landing HEAD `1a8f5f8`, not `653ecdd`, but a `-m 1` revert of the merge restores `main`'s tree whatever the branch holds, so later commits do not change the result **as long as `main` is still `132b548`** (it is, section 0); the INV-4/INV-5 text revert still needs the owner's own words (rule 4). |
| **T5** | Monitoring adopted; runbook copy | **MET** for the item; the plan keeps the gaps it had | `11-monitoring-plan.md` adoption note; `CHARTER.md` C8.5; `docs/runbooks/answerability-judge.md` | The owner adopted the thresholds, cadence and stop rules "as written" and the standing mitigation "stop typing `/aveto-judge`, use `retrieve` alone", by hash (Charter C8.5, `APPROVAL_RECORD-1`); operator is Gopal Patwa. I read the runbook: sections 2 and 5 are present, with a source header, the S5/S6 moves, and the T4 update. Carried from slice 7, not closed by adoption: the operator path's accuracy cannot be observed, the tally is manual and self-reported, there is no on-call, signals 12 to 14 need a person with a shell. Small staleness in the runbook: step A still says "375 passed" (it says a higher count after a deliberate change is fine; the branch has 425). |
| **T6** | Final-tree regression on the PR head | **MET WITH GAPS** | `07-final-tree-qa.md` | Clean on `e2b228e` (below). The gap is that the head moves: QA's sha is not the head that will be pushed. Pre-push check is condition C-1. |
| **T7** | R-A, the retrieval limit | **MET** | `CHARTER.md` C8.5; `README.md` lines 10 to 13 and 142 to 150; `.agentic/CURRENT_MVP_STATUS.md` lines 40 to 48 | The owner accepted it in the Charter. README and status state: 19 of 24 (79.2%, under its 80% bar; not a registered judge bar), 16 of 24 right file shown after judging, "the bars describe the eval path; the operator path is unmeasured", the one-question margin, the D4 overlap, and "This is not a capability claim". Figures match the scorers' lines quoted in `04` section 5 and slice 7 section 9. AI Governance's G1 disclosure condition is met by the same text. |
| **T8** | S5 | **MET** | `01-s5-fix.md`; `06-security-recheck.md` 1.2, 1.3, 1.4; `SKILL.md` line 9; `tests/test_judge_seen_skill.py` | **Fixed, not retired** (Charter C8.5). The `!` line is fixed text with no `$ARGUMENTS`; the run id is read from the gitignored `.aveto-judge/seen-id` as data, refused unless a symlink-free ASCII file of at most 64 bytes matching `^r[0-9]{3}$` and present in the committed key. 21 hostile values (including `r101' ; echo INJECTED ; '`) run three ways (id file, argv, rendered line under `/bin/sh` with a stub `uv`). `/aveto-judge` and every method file byte-identical to `bca0e40` (QA a; Security 1.1). **Residual, advisory, carried:** A1 (a wildcard remains inside `allowed-tools`), A2 (the harness still appends `ARGUMENTS:` text before extracting `!` lines and is relied on to escape it; read from the binary, not run live), A3 (symlink at `q/<id>.txt`), and G7 (not shown against a live harness). The fix removes the interpolation; it does not prove the harness. |
| **T9** | S6, stale text, slice 7 STATE | **MET** (a, b, c) | (a) `CHARTER.md` C8.5; `06-security-recheck.md` 1.5. (b) `README.md`, `CURRENT_MVP_STATUS.md`, `docs/ARCHITECTURE.md` lines 20, 169 to 171, 239 to 240; `06` 1.6. (c) `runs/docs-answerability-2/STATE.md` | (a) The Charter, approved by hash in the driving session, records the S6 rule as deleted "as the owner said on 2026-10-16"; Security independently found no `seen_payload` permission rule in any settings file under the repo's `.claude/`, any worktree, or `~/.claude/settings.json`. (b) The docs say tier 3, landing by PR, owner merges, S5 fixed, S6 deleted; Security checked those sentences true. They make no GO claim. (c) Slice 7 STATE: `Updated: 2026-10-17`; record 7 appears once in its Approvals table (line 46; line 25 is the stage table), so there was no duplicate to remove. `docs/ARCHITECTURE.md` was written by the Architect (the Tech Writer was refused by the write-scope guard, as `05` records). **Note A4:** the worktree's gitignored `settings.local.json` is back, now holding the C6.P run rules, which is a permission surface of S6's class; see section 5. |
| **T10** | Which governance gates apply | **MET WITH GAPS** | `CHARTER.md` C8.5; `04-ai-risk-assessment.md`; `00-slice-plan.md` "Data Governance (T10): waived" | AI Governance at standard ran: tier minimal, **provisional** on the EU AI Act Art. 50 question (OI-1), which is for the owner or legal and which no one has answered. Both its gate rows are MET WITH GAPS (section 4). **Data Governance WAIVED by the owner** (C8.5) with the reason recorded in the plan, the AI risk assessment and `11b`: the program stores no user data and the operator's session is covered by records 3 and 6 of slice 7. What the waiver does not say (`04` section 4): it does not assert a DPA exists; it does not cover the committed eval material; I record it, the owner granted it. The Charter rules on those two roles only; the other rows of the section 5 table are walked in section 4 below on their own evidence. |
| **T11** | Record hygiene: `trace.json`, operator, time | **MET WITH GAPS** | `trace.json`; `STATE.md`; `APPROVAL_RECORD-1.md` | `trace.json` exists, `operator: "Gopal Patwa"`, the approval entry names the same person as the approver (rule 3's "same handle" holds), `landed: false`, `leastPrivilegeEnforced: true` with a note, three `gateCatches`. Gaps: **no time of day** on the Charter approval (the Orchestrator did not invent one; the only bound is the Charter-approval commit, reflog epoch 1792276675, which is about 22:37 UTC on 2026-10-17 and is the commit time, not the approval time); `stages` lists the eight subagent stages and omits the Orchestrator-run ones (setup, the code-review layer), which the trace@2 schema asks for; `STATE.md` is stale (Intent "drafted, awaiting confirmation", Charter "awaiting approval", Approvals row "PENDING", no rows for stages 6 and 9 until mine) while `APPROVAL_RECORD-1` and `trace.json` say approved. Condition C-2. |

### T1 decision, in full

**Does the Charter satisfy T1 as the owner designed it? Yes, for what the run itself does; and it does not, and was not designed to, satisfy T1 as slice 7's checklist worded it for the merge.**

- *What the run does that needs approval:* push `claude/land-answerability` to `origin` and open a PR into `main` (rules 2 and 3 boundary; irreversible-ish). Charter C8.2 and C8.3 name exactly those two actions, with the target, the base, "end review linked", "never merge, never deploy, never send" and a rollback ("close the PR and delete the remote branch"). They are surfaced as their own lines, the Charter passed `charter-check`, and the owner approved it by hash in their own words in the driving session (`APPROVAL_RECORD-1`). That is the Charter path in `HUMAN_APPROVAL_RULES.md`, and it is the approval of the specific action, not a carry-over from another request. The identity is a named person (Gopal Patwa), the same as `trace.json` `operator`.
- *What the run does not do:* merge. The intent and plan say the merge is the owner's own act and the run never merges. No agent merges, so no agent action exists whose approval I would have to verify. The owner performing the merge is a stronger control than approving an agent to do it, and it is the design the owner chose. Slice 7's T1 asked for a merge approval record naming the method; under this design that record is the owner's act itself, and I do not manufacture it, nor treat the Charter as having given it ("Merge is not covered", `APPROVAL_RECORD-1`).
- *Gaps I will not smooth over:* (i) no time of day (rule 3 asks the Release Manager to record it; none exists); (ii) the approval is prospective: the push and PR have not happened, so I confirm the approval and its scope, not that the action matched it (condition C-3: only the two commands the Charter names); (iii) the **merge method is not named**, and the rollback I rehearsed assumes a merge commit (T4).
- *What stays the owner's:* the merge itself and its method; the PR review; whether to add a time of day. Opening the PR is not a landing and I do not sign a landing.

### T3 decision, in full

**WAIVED (owner-accepted limitation), not MET.** The enterprise row "New subprocessor risk-assessed + DPA in place" is not satisfied: there is no DPA (personal subscription; Charter C4.1, `11b`). Retention and training use are "per the plan's public terms, not verified by an agent". The other vendor fields (subprocessors, certifications, liability and breach SLA, residency, export and deletion, whether the terms permit this use, plan tier by name) stay **UNKNOWN**. Nothing is inferred from an unknown.

Why WAIVED and not NOT MET or MET: slice 7 said that proceeding with fields unknown needs the owner's recorded sentence and that the checklist would then say "waived by the owner", not "met". The sentence that exists is Charter C4.1 (DPA not in place; operating rule "public-docs questions only until a DPA is in place" **adopted**), approved by hash. The intent itself defined T3 as "record the status and adopt or decline the operating rule", so the item as the owner designed it is closed; the playbook gate "DPA in place" is not. The Compliance Reviewer asked me to decide whether `APPROVAL_RECORD-1` suffices: **it suffices to open the PR, because opening a PR sends nothing to Anthropic and the data flow starts only when an operator types `/aveto-judge`.** It does not contain a sentence accepting the residual risk (`11b` says so and claims none), and it does not tick the Compliance decision box; both stay the owner's (section 12). The operating rule is a policy control the repo cannot enforce, and it does not reduce what the harness attaches to every request (personal email, git user name, local username, organisation ID), which sits within no DPA.

### T6 detail: the sha, and what came after it

- **QA ran at `e2b228eaf01d9732be54e3268c0ca9265d77f0f9`:** `uv sync --locked` exit 0; `mypy` 24 files clean; `ruff check` clean; `pytest` **425 passed, 12 deselected**, three runs, exit 0; tree clean before and after. The count is explained: 375 (slice 7) + 50 from `tests/test_judge_seen_skill.py` (20 to 70 non-model tests) = 425; Security's R1 removal of one hostile value (`0379f59`) accounts for stage 1's 428. Checks a to g pass (method files and INV text identical to `bca0e40`; every `test_` name cited in `SAFETY_INVARIANTS.md` exists, 49 of 49; `settings.json` identical to `main`; the S5 hostile list includes `r101' ; echo INJECTED ; '`).
- **Commits after `e2b228e`:** `16ebd22` "final-tree QA (T6)" and `653ecdd` "trace.json, charter-check output, spend" (the current head). By subject and by content they add `07-final-tree-qa.md`, `trace.json`, `charter-check-output.txt` and `STATE.md`. **I cannot diff.** Indirect evidence I did gather: the worktree was clean at the start of this spawn; and by file modification time, no tracked non-`runs/` file I listed (`aveto_support`, `tools`, `prompts`, `tests`, `docs`, `.agentic`, `.claude/skills`, `.claude/agents`, `.claude/settings*.json`, `README.md`, `pyproject.toml`, `uv.lock`, `evals`, `.gitignore`) is newer than `docs/adr/0008-operator-run-answerability-judge.md` and `tests/test_judge_seen_skill.py`, which are `e2b228e`'s content; everything newer is under `runs/land-answerability/`. That supports "later commits touch only run records". It is not a diff.
- **This checklist and the `STATE.md` update are further commits** the Orchestrator will make before the push. The head that is pushed is therefore neither `653ecdd` nor `e2b228e`. Condition C-1 turns the indirect evidence into a recorded one on the pushed head.
- **R1's fix (`0379f59`) postdates Security's review base `14303a0`** and was not re-probed by Security or mutation-tested by QA. I read the fixed test: the `sandboxed` fixture redirects `prepare` to a temporary copy of the key and batch files and replaces `subprocess.run` with a function that raises, and each refusal test asserts it was never reached; `"r001\n"` (an accepted value) is gone from `HOSTILE`, replaced by `"r001 "` and `"r001\r"`, which are refused. By reading, the test no longer depends on whether `index/` and `models/` exist, which was the defect. Nobody has run it on a checkout that has them. Advisory.

## 3. Core gates and the tier 3 additions (`docs/RELEASE_GATES.md`)

Carried from slice 7's walk where this slice changed nothing; Charter non-goals forbid re-running any gate. "Source" is who recorded it.

### Implementation and QA

- [x] **Typecheck passed** — `mypy` clean, 24 files, at `e2b228e` (`07` section 1).
- [x] **Targeted tests passed** — `tests/test_judge_seen_skill.py` 73 passed, 2 deselected at `14303a0` (`06` 1.3); in the full run at `e2b228e` after R1.
- [x] **Full test suite passed** — 425 passed, 12 deselected at `e2b228e`. The `-m model` suite still has its one known failure (`test_sample_derivation_reproducible`, R-D), which is not in the regression command and is disclosed in `CURRENT_MVP_STATUS.md`.
- [x] **Build** — n/a (no build step in this pack's commands; unchanged from slice 7).
- [x] **One commit per task** — the reflog shows one commit per stage (S5 fix, rollback, vendor, AI risk, test restore, docs, architecture, F1, code review, security, R1, ADR note, QA, trace). Read from `logs/HEAD`; I cannot run `git log`.
- [x] **No new lint warnings** — by the pack equivalent: `LOCAL_COMMANDS.md` names `uv run ruff check` as the lint command, clean at `e2b228e`. Nobody recorded a literal `git diff --check`. The D6 exemption (`# ruff: noqa` on three Security probe scripts) is carried from slice 7 and was acknowledged by the owner (record 9); the gate passes because those scripts opt out, not because they are clean.
- [x] **UI in preview** — n/a, no UI.
- [x] **Local regression command passed** — `uv sync --locked`, `uv run mypy`, `uv run ruff check`, `uv run pytest` (`LOCAL_COMMANDS.md`), at `e2b228e`.
- [x] **Safety invariants verified** — INV-4 and INV-5 byte-identical to `bca0e40` (sha256 `8900da14fe2672752c6145d3be53db33584637a68cbc5b232388dcd0748d11fd`, `06` 1.1; `diff` rc 0, QA b), every cited test exists and passes (QA c). Not testable: that Claude Code runs the judge's hook; that the live harness escapes an appended `ARGUMENTS:` line (A2). INV-1 and INV-3: no product code changed (QA a).

### Security

- [x] **No secrets / credentials in diff** — `06` 1.5: 20 non-run files and `runs/land-answerability/` scanned, 0 key-like strings, owner's e-mail absent, `settings.local.json` not committed. The UUIDs are Claude Code session ids classified "not credentials" by slice 7.
- [x] **No PII / sensitive data logged** — `06` 1.5, 3; the program stores nothing (INV-4); `.aveto-judge/` is gitignored and deleted on every `judge-apply`.
- [x] **Audit events cover state changes** — none removed or weakened (`06` 3); the product is unchanged.
- [x] **Adapter boundary placeholder still throws** — no model client, network call or dependency added; `aveto_support/` has an empty diff against `bca0e40` (QA a; `06` 1.1).

### Tier 3 only

- [x] **Human approval obtained per `HUMAN_APPROVAL_RULES.md`** — rules 4, 5, 6 actions of slice 7 (records 2 to 8) stand; this slice's actions are under Charter lines C5.3, C8.2, C8.3 (T1). Merge not covered, by design. Scope as T1.
- [x] **Approval recorded: who, when, exact request, exact response** — `APPROVAL_RECORD-1.md`: Gopal Patwa, 2026-10-17, the owner's verbatim words quoted above. **Time of day: not recorded.**
- [x] **Dry-run passed on fixture** — carried, slice 7 `12-tier3-dryrun-audit.md` part (a): 11 of 11 criteria; no model ran in it. Not re-run (Charter non-goal). The operator path has never been measured (G1).
- [x] **Audit event coverage manually verified** — carried, `12-tier3-dryrun-audit.md` part (b): pass with gaps G1 to G9. This slice changes no program code, so coverage stands. Unchanged gaps, not new ones.
- [x] **Post-launch monitoring plan exists** — `11-monitoring-plan.md`, now adopted (T5); section 9.

### Skipped, waived or partly met gates

| Gate | Reason | Approved by |
|---|---|---|
| Data Governance review (enterprise row) | Waived: the program stores no user data; the operator's session is covered by slice 7 records 3 and 6 | Owner, Charter C8.5 (`APPROVAL_RECORD-1`) |
| DPA in place (enterprise row; T3) | Not in place. Owner-accepted limitation under the adopted operating rule; recorded as WAIVED, not MET | Owner, Charter C4.1 (`APPROVAL_RECORD-1`); no separate risk-acceptance sentence exists |
| `git diff --check` (literal) | Not run by anyone; the pack's lint command (`ruff check`) is clean and is the pack equivalent | Nobody; the equivalent was used |
| Build | No build step | n/a, unchanged since slice 7 |
| UI in preview | No UI | n/a |

No skipped gate lacks a rationale.

## 4. Enterprise and governance gates, walked again (slice 7 checklist section 5)

Whether every row applies is the owner's ruling (T10). The Charter names two roles; I walk all twelve on the evidence rather than mark "n/a" without a reason.

| Gate | Owner role | Slice 7 | Now | Basis |
|---|---|---|---|---|
| New data classified + retention set | Data Governance | NOT MET | **WAIVED** | Charter C8.5. Classification exists as the Compliance Reviewer's assignment in `11b` ("owner to confirm"); retention is "per the plan's public terms, not verified". No Data Governance review exists, by the owner's waiver. |
| Catalog / RoPA updated for new data flows | Data Governance | NOT MET | **WAIVED** (same waiver) | None kept; the Charter is silent; `11b` condition 5 leaves the owner's one-line optional. |
| Schema / data migration plan + rollback | Backend Architect | n/a | **n/a** | No schema, no migration, no stored product data. |
| Threat model for new attack surface | Security & Privacy | MET WITH GAPS | **MET WITH GAPS** | No `THREAT_MODEL_TEMPLATE` file. `08-security-review.md` (slice 7, eight surfaces, probes) plus `06-security-recheck.md` (S5 fix, hostile-id probes, harness behaviour read from the binary) cover the substance; not in the template's form. I did not compare. |
| Controls mapped + evidence; named approver | Compliance Reviewer | NOT MET | **MET WITH GAPS** for the mapping; **the approval is the owner's and is PENDING** | `11b` maps GDPR Art. 5, 28, 30, SOC 2 CC9.2, ISO 27001, ISO 42001 and flags Art. 50 as a legal reading not made. Approver named (Gopal Patwa). The Compliance decision boxes in `11b` are unticked ("this file does not tick it for them") and the `11c` Compliance row is PENDING. Every supplier-assurance field beyond C4.1 is UNKNOWN. Read: the Charter covers the Compliance Reviewer's conditions 3 (operating rule adopted) and 4 (S5, S6) and part of 1; the box is the owner's act at review (section 12). |
| New subprocessor risk-assessed + DPA in place | Compliance Reviewer | NOT MET | **WAIVED** (limitation; **not MET**) | T3. |
| AI capability risk-tiered; obligations met | AI Governance | NOT MET (not run) | **MET WITH GAPS** | `04-ai-risk-assessment.md`: tier minimal, **provisional on OI-1** (Art. 50, owner or legal); every template obligation met with an evidence pointer; gaps G1 (operator path unmeasured), G2 (bar 2 one question of margin, twice), G3 (retrieval 79.2% / 16 of 24, accepted), G4 (hook never fired), G5 (no hostile-passage cases in the suite), G7 (S5 fix not shown against a live harness), G8 (no unseen held-out set remains). **G6 is resolved:** the AI assessment found INV-5's cited `test_refuses_wrong_argument_count` missing; commit `501ec3a` restored it, `tests/test_judge_seen_skill.py:248` has it, and QA check c found 49 of 49 cited names present. `04` was written before the restore, so its G6 text is stale, not wrong at its time. |
| Eval coverage for AI safety invariants | AI Governance | MET WITH GAPS | **MET WITH GAPS** | `04` section 6.1 maps INV-4 and INV-5 clauses to named tests, probes and the two pre-registered bars; gaps as above. |
| Cost-per-action estimated; kill-switch tested | FinOps | n/a with reason | **n/a with the same reason** | Subscription window, no metered API (and none may be added). Per-spawn cost is monitoring signal 10 (about 7.9k and 8.6k mean peak). The kill switch is "do not type `/aveto-judge`", or `git rm -r .claude/skills/aveto-judge/`; **only the full revert (step 3) was rehearsed**, not that `git rm`. |
| Docs match shipped behaviour; migration notes | Tech Writer | MET WITH GAPS (stale on tier and S6) | **MET WITH GAPS** | The stale tier and S6 text is fixed in README, status, `ARCHITECTURE.md` (the Architect), and the runbook; Security 1.6 checked the S5 and S6 sentences true, and its A5 items were addressed (runbook item 6 reworded; ADR 0008 note at line 28, ADR stays Proposed). Remaining gaps: `11c` body and parts of `11b` "Access scope" still describe S5 and S6 as open; the runbook's "375 passed"; `04` G6 stale. All are run-record or reference text, none is user-facing behaviour. |
| SLOs + runbook + tested rollback (production service) | SRE | MET WITH GAPS / part n/a | **MET WITH GAPS / part n/a** | Not a production service; no SLO, said plainly in the plan. The runbook is now in `docs/runbooks/`. Rollback step 3 rehearsed (T4); steps 2, 4, 5 and the squash or fast-forward variants were not. |
| Change request recorded + approved (CAB) | Release Manager | NOT MET (approval PENDING) | **MET WITH GAPS** | T2. Recorded, named approver, human owner row APPROVED as given by the Charter for landing by PR; time of day absent; Release Manager and Compliance rows PENDING; body stale. The merge approval proper is the owner's act. |

## 5. Residual items carried, and the one deviation

### R-A to R-F (slice 7), and who has accepted what

| # | Item | Status now | Basis |
|---|---|---|---|
| R-A | Retrieval gate exit 1 on the fifth set (19/24 = 79.2%; 16/24 end to end) | **ACCEPTED by the owner** and stated plainly | Charter C8.5 (T7); README and status (T7 above) |
| R-B | Bar 2 passed by one question at both stages; fifth-set source overlap (D4) | **Not accepted.** Disclosed in README and status | Not in the Charter. `04` G2: do not read 84.2% as a precise rate |
| R-C | Advisories S1 to S4, S7, S8 (slice 7) | **Not accepted.** Carried. S5 is fixed and S6 deleted, so they are off this list | Not in the Charter |
| R-D | The failing `-m model` test `test_sample_derivation_reproducible` | **Not accepted.** Disclosed in status ("A later slice must change it"); outside the regression command | Not in the Charter |
| R-E | The deny hook never fired live; the INV-5 session-context list is not complete | **Not accepted.** Disclosed in INV-4/INV-5 and `04` G4; monitoring signals 4 and 5 are zero-tolerance | Not in the Charter |
| R-F | Telemetry is self-reported | **Not accepted.** `trace.json` says `self-reported`; its `toolCalls` are 0 placeholders | Not in the Charter |

The Charter accepts R-A only. None of R-B to R-F is a failed Charter check (C8.1), and none blocks opening a PR; each is on the owner's list (section 12).

### Security re-check (`06`) and code review

| id | Status | Note |
|---|---|---|
| R1 (required-fix: `"r001\n"` in the hostile list passed only because `index/` and `models/` were absent) | **Fixed** in `0379f59`; confirmed by QA's 425 and by my reading of the sandboxed test | Not re-probed by Security on a checkout with `index/` and `models/`; see T6 |
| A1 `allowed-tools` keeps a wildcard inside the command (S6's class) | **Carried**, advisory | Narrowed by this slice (trailing `*` removed); not reachable today; a later slice should pin the project path |
| A2 the harness still appends `ARGUMENTS:` to a skill with no placeholder and is relied on to escape it | **Carried**, advisory; **must be in the end review** | `01-s5-fix.md` says "no harness substitution behaviour is relied on", which is slightly overstated; optional later `disable-model-invocation: true` |
| A3 `q/<id>.txt` write and `seen-id` read follow a symlink (check-then-use) | **Carried**, advisory | Needs a local writer already in the tree; unchanged since slice 7 apart from `read_id` |
| A4 the run's local permission rules (`uv run pytest *`, `git branch *`, `git diff *`, ...) in the gitignored `.claude/settings.local.json` | **Open until the file is deleted.** The file is present and holds exactly the C6.P list (I read it) | Delete it when the run ends and say so in `END_REVIEW.md` (condition C-4). Same class as S6, owner-approved by C6.P, not shipped |
| A5 stale runbook item 6; ADR 0008 usage line | **Addressed** (runbook line 63 reworded; ADR 0008 line 28 note, `e2b228e`) | ADR 0008 stays Proposed |
| G6 (INV-5 cites a test that no longer existed) | **Resolved** by `501ec3a`; INV-5's text did not change (Charter C5.2 held) | Not an owner decision any more |
| OI-1 EU AI Act Art. 50 | **Open, owner or legal** | The AI risk tier is provisional until answered; section 12 |

### Code-review F1: the deviation from Charter C6.P

C6.P said the run's allow rules are written to `.claude/settings.json`. The Orchestrator's `/code-review` found them committed there (F1, Important: they would have shipped to `main` and auto-allowed, for example, `git branch -D` in every later session) and moved the identical list to `.claude/settings.local.json`, which `.gitignore` line 9 excludes. Verified: `settings.local.json` holds exactly the 16 C6.P rules (read); `.claude/settings.json` is identical to `main`'s (QA check d; Security 1.1).

My reading: this is a **narrowing**, not a new gated action. The rules are the same; the scope of effect is the owner's local worktree instead of every later session on `main`; the only thing that differs from the Charter's words is the file name. Charter section 9 stops are not triggered (no new model, processor, data, file in the repo, invariant or irreversible action). I do not treat it as a defect. It must still be **stated, not buried**: it goes into `END_REVIEW.md` with the delete-at-end step (C-4), because the owner approved a specific file and is entitled to know a different one was used.

## 6. Evidence figures to carry (verbatim from the scorers via `04` section 5; not rounded up)

| Measure | Stage 5 (seen-set sample) | Stage 7 (fifth set, scored once) |
|---|---|---|
| Bar 1 (abstain on unanswerable) | 20/20, at least 16: MET | 24/24, at least 20: MET |
| Bar 2 (answerable, right file in top 5, not abstained) | 24/28 (85.7%), at least 23: MET, **one question of margin** | 16/19 (84.2%), 80%: MET, **one question of margin** |
| Judge errors; tool-use audit | 0; offered tools 0, `tool_use` 0 | 0; same |
| Best-score rule (`top1 < 0.67`) | not met, both bars | not met, both bars |
| Retrieval gate on the set | exit 0 (28/28) | **19/24 = 79.2%, under its 80% bar, exit 1** (not a registered judge bar); **16/24 end to end** |

These are **eval-path** figures. The operator path (`/aveto-judge`) has never been measured, and no sentence in the PR may say otherwise. The judge was not re-run in this slice (Charter non-goal).

## 7. Rollback plan

Lifted from slice 7's `11c` and spec section 13, confirmed against what exists and against `02-rollback-rehearsal.md`. I ran none of it.

1. **Before any merge:** close the PR and delete the remote branch (Charter C8.3). Nothing is on `main`; the branch can also be reverted commit by commit.
2. **After a merge, disable the operator path only:** `git rm -r .claude/skills/aveto-judge/` and commit; consider the same for `.claude/skills/aveto-judge-seen/`. `retrieve` is untouched. **Not rehearsed.**
3. **Full revert:** `git revert -m 1 <merge-commit>` then `uv sync --locked`, `mypy`, `ruff check`, `pytest`. **Rehearsed (T4)** against a simulated `--no-ff` merge onto `main` `132b548`: clean, tree identical to `main`, 168 passed. **Assumes the owner merges with a merge commit.** With a squash or fast-forward the target differs and the rehearsal does not cover it. If `main` moves before the merge, the owner re-checks. **INV-4 and INV-5 return to their pre-slice text, a rule 4 change: the owner's own words first, never an assumed approval.** README and `CURRENT_MVP_STATUS.md` revert with it.
4. **D1 only** (seven harness tools in the deny list): `git apply -R` of `03a-d1-proposed-diff.md`, owner's approval, `uv run pytest tests/test_judge_artefacts.py`, fresh-load session. Not rehearsed; the SRE advises stopping rather than reversing D1 alone.
5. **Eval data only:** `git rm -r runs/docs-answerability-2/judge-check/`. No product effect.
6. **Outside git, unreachable by any revert:** Claude Code transcripts in `~/.claude/projects/` (full payloads and replies); the gitignored `settings.local.json` (delete it at run end, A4); whatever Anthropic retains, under terms that are not verified. No repo rollback recalls data already sent.
7. The program writes nothing persistent except the gitignored `.aveto-judge/`.

Confirmed against the diff: the paths in steps 2, 4 and 5 exist in the tree (Glob). Rollback gate: **plan exists, step 3 tested.**

## 8. What this verdict allows, and what it does not

**Allows:** the Orchestrator's closing of the run: the pre-push check, the record fixes, `END_REVIEW.md`, the push of `claude/land-answerability` and the PR into `main` under Charter C8.2, exactly as written.

**Does not allow, and I have not done or approved:** a merge (the owner's act); a deploy, tag, announcement or external description of the result as a capability; any claim in the PR body that the slice is released, approved, GO for landing, or "answers questions"; any claim of a pass on the retrieval gate; unattended, scheduled, API or `claude -p` use of the judge; any non-public question to the judge (the adopted operating rule); a rescore, a rerun of any gate, or an edit to a method file; any push or PR other than the two Charter C8.2 names; a revert of INV-4 or INV-5 without the owner's words. I sign off **opening a PR**, not a landing. The Release Manager row of `11c` stays PENDING for that reason.

## 9. Post-launch monitoring (Tier 3)

There is no service, telemetry or on-call; "monitoring" is what the operator looks at after each use and what the owner re-checks every four weeks and on triggers. Adopted as written by the owner (Charter C8.5): `runs/docs-answerability-2/11-monitoring-plan.md`; sections 2 and 5 are in `docs/runbooks/answerability-judge.md`.

- **Signals that matter most:** offered tools 0, `tool_use` 0, model `claude-sonnet-5-5` (zero tolerance; signals 4, 5, 7); judge errors, stop at 2 in the last 10 uses; ANSWERABLE where the shown passages do not answer, stop at 2 in the last 20 (the failure that shows a wrong file labelled judged); over-abstention on known-answerable questions, watch 4 of 10, stop 5 of 10 (baseline 14 to 16%); retrieval dev set 19/24, stop below; prompt hash `24b244d2...a159427`, pins and frozen files unchanged.
- **Threshold for concern / stop:** as the plan's Stop column. Stop means the operator does not type `/aveto-judge` and uses `retrieve` alone (the standing mitigation the owner adopted); anything beyond that, and any revert of safety text, is the owner's.
- **Owner:** Gopal Patwa, as operator and as the reader of the four-weekly note. **Post-Launch Learning Agent** receives the carry-forward list in section 13 after the owner merges and shares a period note.
- **What it cannot show:** whether the operator path behaves like the measured eval path. `04` adds that the first months of tally are the first measurement of that path, not a confirmation of the bars. A quiet period proves nothing.

## 10. Conditions before the push and the PR

These are checks and record fixes for the Orchestrator, who has a shell; I could do none of them. Each is verifiable, none changes a fact I rely on except C-1, which is the pre-registered flip to NO-GO.

- **C-1. Pre-push check on the exact head to be pushed** (after this checklist and `STATE.md` are committed). Record the output in `END_REVIEW.md` or `STATE.md`: `git rev-parse HEAD`; `git status --short` empty; `git diff --stat e2b228eaf01d9732be54e3268c0ca9265d77f0f9 HEAD` lists **only paths under `runs/`**; `git diff --stat bca0e403a69a5cda7826ea36897734bc63dc7b87 HEAD -- aveto_support tools prompts .claude/agents/aveto-answerability-judge.md .claude/skills/aveto-judge` empty; `git diff main -- .claude/settings.json` empty; `diff` of `.agentic/SAFETY_INVARIANTS.md` against `git show bca0e40:.agentic/SAFETY_INVARIANTS.md` identical; `git diff --check` clean. **If any non-`runs/` path appears after `e2b228e`, this verdict becomes NO-GO until stage 8 is re-run on the new head and recorded.**
- **C-2. Record fixes in `STATE.md` and `trace.json`.** Approvals rows for the gated actions, each citing the Charter line and its sha256: `CHARTER.md#C5.3` (skill change, done), `#C8.2`/`#C8.3` (push and PR, pending until done). Correct the stale Intent, Charter and Approvals rows (the Charter row reads "awaiting approval" and the Approvals row "PENDING" while `APPROVAL_RECORD-1` records the approval). Add rows for the review layer and this stage. In `trace.json` list the Orchestrator-run stages (`"executor": "orchestrator"`) and keep `landed: false`. Do not invent a time of day.
- **C-3. The push and the PR are exactly Charter C8.2 and C8.3.** `git push -u origin claude/land-answerability`; `gh pr create` with base `main` and `END_REVIEW.md` linked. No merge, no auto-merge, no other branch, no tag, no deploy, no announcement. The PR text states: tier 3; the owner merges; not announced; the eval-path caveat; the 79.2% and 16 of 24 known limit; DPA not in place with the operating rule; and that no release or capability claim is made.
- **C-4. `END_REVIEW.md` discloses what this checklist carries:** the F1 file deviation (section 5); A2 (reliance on the harness's escaping) and A1, A3; A4; T3 as WAIVED not MET; R-B to R-F not accepted; OI-1; the merge method and its effect on rollback; the missing time of day; the stale `11c` body and the Compliance and Release Manager rows PENDING; that this verdict opens a PR and is not a landing sign-off. **After `gh pr create` has run, delete `.claude/settings.local.json`** (the `gh pr create` and `git push` rules live there and are not needed again) and record that it is gone.

**Pre-registered NO-GO triggers:** C-1 finds a non-`runs/` change after `e2b228e` and no new clean regression exists; any method file or INV text differs from `bca0e40`; a push or PR beyond the two Charter lines, or any merge by an agent; the Charter's sha256 differs between `APPROVAL_RECORD-1`, `charter-check-output.txt` and the file as pushed.

## 11. Verdict

- [ ] **Go** — the slice lands now. Not ticked. Nothing lands from this file; landing is the owner's merge.
- [x] **GO WITH CONDITIONS — for opening the pull request** (push `claude/land-answerability`, PR into `main`) under Charter C8.2 and C8.3, subject to C-1 to C-4 above. C-1 is mechanical and flips this to NO-GO if it fails; C-2 to C-4 are records and disclosures, not facts I depend on.
- [ ] **No-go.** Not issued. Triggers are listed in section 10.

Tally of T1 to T11: **MET** T4, T5, T7, T8, T9; **MET WITH GAPS** T1 (push and PR only), T2, T6, T10, T11; **WAIVED, not MET** T3. **NOT MET: none.**

Why GO WITH CONDITIONS and not a plain GO: the head that will be pushed is not the head QA ran on and I cannot diff (T6); the approval record lacks a time of day and `STATE.md` is stale (T1, T11); and the owner-side items below are open. Why not NO-GO: no Charter pre-registered check failed (C8.1); every gate the run can close is closed or has its limitation stated and, for T3 and Data Governance, accepted by the owner in the Charter; nothing the PR does sends data to a third party or changes `main`.

Said without the label: **the run may push and open the PR. The slice is not released. Nothing here is the owner's approval to merge, and nothing here treats an unknown as met.**

## 12. What the owner must still decide at the review and the merge

Each is the owner's. None is satisfied by this file.

1. **The merge itself, and its method.** Name merge commit, squash or fast-forward. The rehearsed rollback (`git revert -m 1`) covers a **merge commit only**. Re-check that `main` is still `132b548` (the rehearsal base) when you merge.
2. **Read the change itself** (tier High). The words that go to `main` and that you approved in slice 7 records 5 and 8: INV-4 and INV-5 in `.agentic/SAFETY_INVARIANTS.md` (unchanged this slice, byte-identical to `bca0e40`); the judge agent file (model, deny list, hook); the S5 change in `.claude/skills/aveto-judge-seen/` (the only safety-control file this slice changed, bounded by C5.3).
3. **T3, the DPA.** The DPA is not in place and the gate is waived under the adopted rule. If you want a risk acceptance on the record, it is one sentence in the driving session; a later session writes it into `11b`. Also yours: tick or decline `11b`'s Decision boxes (Compliance), the Compliance and Release Manager rows of `11c`, the optional RoPA one-line (Data Governance is waived), and the unknown fields (plan tier by name, retention period, training-use position, subprocessors, residency, whether the plan's terms permit this use). The operating rule is a policy the repo cannot enforce, and the personal e-mail, git user name, local username and organisation ID that ride on every request are within no DPA.
4. **OI-1, EU AI Act Art. 50.** A line from you or legal: applies, does not apply, or ask legal. The AI risk tier (minimal) is provisional until then.
5. **The not-accepted residuals, R-B to R-F** (section 5): accept them, or keep them open and carried. Plus the advisories A1 to A3 for a later slice (pin `allowed-tools`; optional `disable-model-invocation: true`; `O_NOFOLLOW`), G1 (the operator path is unmeasured, so your first months of tally are its first measurement), G5 (add hostile-passage cases at the next eval refresh) and G8 (no unseen held-out set remains).
6. **A4:** confirm `.claude/settings.local.json` is deleted after the PR (condition C-4), and that you are content with the file-name deviation in F1.
7. **Time of day** for the Charter approval, if you want one on the record (rule 3). The Orchestrator did not invent one.
8. **Whether to merge at all now.** Landing puts the judge on `main` for any later session opened there, behind a personal subscription with no DPA, and with an unmeasured operator path. That is the owner's weighing; this file only lists what is and is not established.

## 13. Hand off

- **To the Orchestrator:** conditions C-1 to C-4; then the push and PR under C8.2; record this stage's spend (I record none); do not merge. Do not edit this file's verdict; if C-1 fails, hand back to QA Evidence with the list.
- **To the owner:** section 12.
- **To the Post-Launch Learning Agent:** not yet; after the owner merges and shares a period note. Carry-forward: the advisories A1 to A3, the R-D test fix, G5 and G8, the unmeasured operator path, `11c` and `11b` stale-body cleanup, the runbook's "375" count, and `trace.json` `toolCalls` being placeholders.
