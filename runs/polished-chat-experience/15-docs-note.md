# 15 Docs note - polished-chat-experience (stage 10, Tech Writer, standard)

Files changed: `README.md`, `docs/runbooks/public-ask.md`, `.agentic/CURRENT_MVP_STATUS.md`. No privacy or Article 50 wording, INV text or other `.agentic/` file touched.

## Changes
- **README.md**: banner "This branch is not merged" replaced (see stale line below); Routes paragraph lists `GET /scorecard`, `POST /warm`, `POST /count/docs-click`; new "The page" list (answer card, refusal card without passages, suggested questions, waiting, resting state, drawer, scorecard, counts); how the figures file and strict reader work and how to add a figure (record file first); recorded-figures table; "Not yet recorded" list; result-store note (S1); rollback line.
- **Runbook**: section 2 gets the rollback-is-a-Bicep-deployment and rehearsal-is-a-release-gate note; new section "New routes" (what each route does, none reaches the judge or logs, counts are raw totals since restart and inflatable S2, result store S1, figure-adding steps, not yet recorded).
- **CURRENT_MVP_STATUS.md**: stale "not merged / not on main" lines corrected; new bullet for this slice; "not yet recorded" bullet.

## Record behind each figure
| Figure | Record |
|---|---|
| 731 passed, 0 failed; 668 at start | `10-test-count.txt` (731); `00-slice-plan.md` (668) |
| axe-core 4.10.2, no serious or critical on 5 views; no sideways scroll at 375 px | `08-browser-checks.md` |
| no P0/P1, two P2; S1, S2, A1, A2 | `14-security-review.md` |
| 30.8 s, 1.66 s, 5.09 s, $0.00785, earlier release | `runs/public-ask-the-docs/18-gate/RESULT.md` (via `scorecard.toml`, existing text) |
| 60 clicks an hour, 10 minutes, 1,000 results | `05-tech-spec.md` 3.8; `14-security-review.md` S1 |

## Flags
1. **Discrepancy: `10-figures.md` and `scorecard.toml` say "731 passed" citing `13-qa-evidence.md`, but that file records 730** (and no file in `runs/polished-chat-experience/` contains 731). I used 730. The scorecard shows 731 against a record that says 730; the Release Manager should either point it at a record of the D8 re-run or correct the row. Needs a Backend Architect edit of `scorecard.toml` (outside my scope).
2. **Stale line fixed.** Scope review (`01-scope.md` section 4) called "not on main / not merged" stale. Proof in the repo: `00-slice-plan.md` has the branch level with `main` at `32e54a6` and `aveto_service/` is in this tree; the fix-service-accounting 668-test count is the baseline of that tree. Stated only as "in the tree of `main` at 32e54a6". The pull request number (scope review says #9) has no file record: marked unconfirmed. Other "deployed from branch" wording in `runs/` history left alone.
3. Suggestion labels: judge verdict for the four questions unconfirmed (QA Q5); stated so in README and status.
4. "First load about 26 seconds" (intent) has no record (D5); not used.
5. Not written anywhere: deploy, health, merge, release verdict, live timings, rollback timing, Codex review.
6. The runbook's other sections (5, 7, 8) still describe the earlier release (e.g. section 5 says "Not deployed yet" for the spend fix, which status says is deployed). Pre-existing, outside this slice's change; for the owner or a later pass.
