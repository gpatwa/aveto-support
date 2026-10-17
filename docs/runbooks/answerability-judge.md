# Runbook: the answerability judge step

> **Where this comes from.** Sections 2 and 5 of the SRE's monitoring plan,
> `runs/docs-answerability-2/11-monitoring-plan.md`, copied without change of
> substance. **Adopted as written** by the owner, Gopal Patwa (operator), in
> Charter C8.5 of `runs/land-answerability/CHARTER.md`, approved in
> `runs/land-answerability/APPROVAL_RECORD-1.md` (2026-10-17). The standing
> mitigation the owner adopted is: **stop typing `/aveto-judge`, use `retrieve`
> alone.**
>
> The two sections below cite other parts of the plan ("section 1" signals and
> Stop values, "section 3" triggers, "section 7" open items, "signal 9",
> "signal 14"). Those stay in the plan; read them there. Two open items the plan
> lists in its section 7 have since moved (Charter C8.5): S5 was fixed in slice
> `land-answerability` (`/aveto-judge-seen` now takes no caller text; the operator
> writes the run id to `.aveto-judge/seen-id` and runs `/aveto-judge-seen` with
> no argument), and the S6 rule was deleted (owner, 2026-10-16). The bars in the
> plan describe the eval path; the operator path (`/aveto-judge`) has not been
> measured.

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

## 5. Runbook and rollback

This is a short runbook for someone who did not build the slice.

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
6. **Outside git:** S6's rule was deleted 2026-10-16. `.claude/settings.local.json` now holds only the run's local rules (Charter C6.P); it is gitignored, in no commit, and deleted when the run ends. Transcripts in `~/.claude/projects/` are the owner's session data; no rollback touches them.
7. The program writes nothing persistent except `.aveto-judge/` (gitignored; deleted on every `judge-apply`; a symlink there survives, S2).

**Rollback is tested, not assumed:** what was tested is only that the paths named exist, that the pre-merge revert is trivial, and that the pin tests would fail on a changed agent file. **No revert has ever been rehearsed.** I propose one rehearsal on a throwaway branch as a first item for the owner (a `git revert` of the slice commits plus the regression, nothing merged), and I record that it is proposed, not done.

> **Update, slice `land-answerability` (2026-10-17).** Rollback step 3 was
> rehearsed on a throwaway branch: `git revert -m 1` applied cleanly, the tree was
> identical to `main`, and the regression passed on it (168 passed). Only step 3
> was rehearsed, against a simulated `--no-ff` merge. Record:
> `runs/land-answerability/02-rollback-rehearsal.md`. The sentence "No revert has
> ever been rehearsed" above is the SRE's original text and is superseded by it.

**After any Stop or rollback, the review:** write what happened, which signal tripped, the 2 to 5 system conditions, and at least one **preventive** (not just mitigative) action, with an owner and a date, using `templates/INCIDENT_REVIEW_TEMPLATE.md` in the playbook. No person is named as the cause.
