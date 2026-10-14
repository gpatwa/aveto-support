# Standing instructions (owner, typed in the driving session, 2026-10-12)

- **SI-1:** for a design question with a recommended default (not rules 1 to 6, a budget change, a credential, or push/merge/deploy), proceed on the default and list it in the next digest; the owner vetoes by exception.
- **SI-2:** any Reply N in `runs/docs-answerability-2/SUPPORT_REPLIES.md` that marks its decisions as recommended defaults under SI-1 is adopted under SI-1, with each decision listed in the next digest. This never covers budget or ceiling changes, rules 1 to 6, credentials, safety-control wording, lowering a depth the intent names, or push, merge and deploy.

## Other owner instructions at start (same message)
- Fresh worktree off main (done: `.claude/worktrees/docs-answerability-2`, branch `claude/docs-answerability-2`).
- First commit brings slice 6's judge code, skills, tests, `mcp__*` deny list; NOT a8c9604 (INV words), NOT slice 6 run records.
- After that commit, the owner starts a fresh session in the worktree before any judge spawn (agent and skill files load at session start).
- Plan confirmation shows stages with Environment, the estimate, and a ceiling and hard cap derived from slice 6's measured ratios; the owner types the figures.
- Stage 1 is a two-spawn Sonnet measurement in the real forked-skill configuration, before anything is built; bring measured numbers and a projection.
- Never approve, relay or infer an approval. Stop and ask for rules 1 to 6, a ceiling or hard-cap change, lowering a depth the intent names, credentials, push/merge/deploy. No `claude -p`, no metered API. Do not ask for or look for the fifth gate set.

## Digest: decisions taken under SI-1
| # | Decision | Default taken |
|---|----------|---------------|
| D1 | The first commit cannot be a plain `git cherry-pick 37c21d2` (it is a delta on slice 6's 3a/3b commits, main lacks the base files: modify/delete conflicts). | Take the files 37c21d2 touches, plus the files they need to run (`judge_eval.py`, `__main__.py`, prompt, `/aveto-judge` skill, tests, `.gitignore`), at their 37c21d2 state, in one commit (5eb2a8a). Left out: a8c9604, ADR 0008, `.agentic/LOCAL_COMMANDS.md`, all `runs/`. |
| D2 | Stage 1 needs a seen-check directory for the forked skill (its path is hardcoded). | Created `runs/docs-answerability/seen-check/` with only two rows (r001, r002; public eval-set questions) and a key with membership only, no answers. Not slice 6's records; stage 4 rebuilds it for the 48 sample. |
| D3 | The worktree had no `index/` or `models/` (gitignored). | Copied both from the main checkout (local copy, no network). |
| D2' | Reply 1 D2: the harness prefix is the `Base directory for this skill: <path>` line, not the 94-char cliPrefix. | Adopted under SI-2 (owner, 2026-10-12). Stage 3 states the line's length as measured in this worktree; never uses 94. |
| D3' | Reply 1 D3: INV-5's wording lists what the judge receives (question and passages; CLAUDE.md/AGENTS.md from the main checkout path; user email; git branch, user, five recent commit subjects; environment lines). | Adopted under SI-2 as the content to draft from. The words themselves are the owner's at rule 4 (end of stage 3b). |
| D4' | Reply 1 D4: no budget change from stage 1. | Adopted under SI-2. Plan 2.6M and ceiling 3.4M unchanged. |

## Not adopted under SI-1/SI-2 (owner decides)
- **Reply 1 D1** (add the seven harness tools to the judge's `disallowedTools`): it edits the agent file (a safety control, rule 5 territory). Per the owner (2026-10-12): bring the exact diff at stage 4 before applying; the owner approves then. Needs a fresh-load session afterwards.

## Digest: Architecture pass 1 defaults adopted under SI-1 (owner may veto; detail in `02-tech-spec.md` section 14.2)
A1 reply text kept only for rows that differ from the key or are judge errors · A2 smoke row r049 (never scored) · A3 one whole-batch rerun at stage 5 as well as 7 · A4 one continuation after a stop that affected no spawn · A5 no change to the product's "counted as failures on both bars" label · A6 seen-check data moves to `runs/docs-answerability-2/judge-check/` · A7 the gate set later served as r101 upwards by the same frozen helper · A8 new eval-only `tools/judge_run.py`, routed through `judge-apply` · A9 `judge-apply` keeps its two-line output (stated in INV-4 content, approved with the words) · A10 best-score rule `top1 < 0.67`, must first reproduce 13/20 and 37/56 on the seen sets · A11 one assertion added to the offline test · A12 `LOCAL_COMMANDS.md` updated at stage 4 · A13 no model reads transcripts (the audit is deterministic).
Also decided by the Architect, in the spec: payload layout line is 137 chars in this worktree (path-dependent; checked by form, any other length voids a batch); both grammar strictness details kept; sample order and parity registered (positions 1,3,…,55 of the 56).

## Digest: decision taken under SI-1 at the fifth-set handover (owner may veto)
| # | Decision | Default taken |
|---|----------|---------------|
| D4 | Support Reply 2: source reuse. Request 1 said no `sources` path may be a source in any seen set; the support session reports that cannot hold (the seen sets cite 96 of 123 corpus files; 21 of 24 answerable questions cite at least one file an earlier set cites; no question or topic repeats). | Reuse allowed and disclosed (the file's header says why the second bar may read slightly optimistic on those questions). Committed unopened as b692ffc, after the freeze (bca0e40 is its ancestor): `evals/retrieval-heldout-5.toml` and `evals/retrieval-heldout-5-reserves.toml`. The support session also reports the working copy was regenerated after a restart (base sha256 `9cca11aeb4cd66eb` matches the original's record). |

## Digest: label review (stage 6) decisions under SI-1 (owner may veto; detail in `06-label-review.md` section 6)
| # | Decision | Default taken |
|---|----------|---------------|
| D5 | Label-review source additions E2 to E11 (additions only, nothing dropped; the reviewer's "default" priority). | Applied to `evals/retrieval-heldout-5.toml` as data, `sources` lines of 10 answerable questions only (g01, g02, g07, g08, g09, g14, g17, g18, g19, g21); no question text changed; all paths checked to exist at the pinned commit. **Not applied:** the optional `docs/OPERATING_MODEL.md` addition to g02 (the reviewer says it answers a different quantity; leaving it out keeps the gate stricter). `docs/VALIDATION_MATRIX.md` stays on g08 (the owner may drop it; that would only be stricter). |
| D5b | **Held for the owner:** E1, replacing gu09 (AMBIGUOUS) with reserve gr02. | Not applied. Reviewer recommends replacing. Owner decides before scoring. |

## Owner decision recorded (D5b, 2026-10-13, typed): replace gu09 with reserve gr02
Owner's words: "D5b: approved. Replace gu09 with reserve gr02 in evals/retrieval-heldout-5.toml, exactly as the reserve is written (id becomes gu09 so the unanswerable ids stay gu01 to gu24), keep the hard-negative count at 18, commit it as data, and record it in the digest. Do not edit any other question."
Applied: the old gu09 block replaced by gr02's block with only the id changed (diff: one line, the `question` line; the flags were identical). Checked by a TOML parse: 48 questions, 48 unique ids, 24 answerable, 24 unanswerable (gu01 to gu24), 18 with `hard_negative = true`; no `sources` on gu09. No other question edited. gr02 stays in the reserves file unchanged (it is now also gu09; it must not be used again).

## SI-3 (owner, typed, 2026-10-14)
After a stage or pre-registered check passes, continue to the next planned stage without waiting. Stop only for: a failed pre-registered check; any rule 1 to 6 approval, safety-control wording, lowering a depth the intent names, a credential, or push, merge or deploy; spend above the 3.4M ceiling; an anomaly in a spawn audit; a Security finding rated blocking; or a session the owner must start (write the session request with the exact line and stop). The scoring run stays blind: the scoring driver does not read the key or the set. Everything else is decided under SI-1 and listed in the digest.
