# Docs note: fix-service-accounting (stage 7, Tech Writer, standard)

Files changed: `README.md`, `docs/runbooks/public-ask.md`, `.agentic/CURRENT_MVP_STATUS.md`. Not touched: `.agentic/SAFETY_INVARIANTS.md`, `aveto_support/`, `prompts/`, `.claude/`, code, tests, `docs/ARCHITECTURE.md`, STATE.md. Written from spec 05 (3.3, 1, 2), 08-backend-note, 13-qa-evidence and code-review CR-3.

## Lines changed

| File | Place | Change |
|---|---|---|
| README.md | recorded-figures table, cost row (was l.211) | $0.0079 to $0.0078; "$3 and $15 / 50% high / safe side / $0.2354" removed; counter defaults $2/$10 in this PR, not deployed, live revision 0000006 still on earlier defaults |
| README.md | "Read these plainly" bullet (was l.229-236) | $0.0078; 27/41 and "owner's call" removed; new bullet "How the service counts spend": defaults 2000/10000 with source and date, override stays, retries reserved, one-sentence charging rule, issues #6/#7/#8 closed on merge, daily pause estimate about 33 |
| runbook | status header (l.11) | $0.0078; parenthesis on 50% removed |
| runbook | section 1 notes | added: pass `killSwitch` explicitly on every deploy; shell variables are for humans, the Orchestrator uses literal values; no price parameter (Bicep defaults) |
| runbook | section 4 table, token row | $0.0078; counter at $2/$10 (not deployed yet) |
| runbook | section 5 | reservation and charging rule rewritten (two attempts reserved, unused part returned, each attempt on its own outcome) |
| runbook | section 7 | "about three failed questions" replaced by "about five ... (estimate)"; D4 "about 40" kept as the recorded decision, with about 33 noted |
| runbook | section 8 Cost and capacity | $0.0078 recorded; 1,270 a month labelled estimate; 27/41 replaced by the 33 estimate with its assumption, 41 said plainly not to be what the design gives |
| runbook | section 8 Pricing | "$3 and $15 ... 50% ... owner's call" replaced by defaults 2000/10000, source, date, override, not deployed yet |
| CURRENT_MVP_STATUS | recorded figures | $0.0078; 50% high / 27 / 41 removed; 1,270 labelled estimate |
| CURRENT_MVP_STATUS | new sub-bullet "Spend accounting" | what the branch does, QA's 668 passed, not merged, not deployed, 33 an estimate |
| CURRENT_MVP_STATUS | "Not yet done" | "Open item: set the service's price env values..." removed; replaced by "now 2000/10000 in the branch code; not deployed yet, to be confirmed by the live smoke after the redeploy"; D4 wording |

A grep of the three files for `$3 and $15`, `50% high`, `27 questions`, `0.0079`, `0.2354`, `safe error`, `safe side`, `3000/15000` finds nothing.

## Recorded versus estimate

Recorded (stated as fact): 71,151 input and 1,460 output tokens for 20 gate questions; $0.1569 for 20; the first live question $0.0099; 668 tests passed (QA, three runs); the price $2/$10 read 2026-10-23 (as the spec and code comment state it; the pricing page is unchecked by QA and by me).

Estimate (each says so in the text): about 33 questions a day (assumes about $0.030 per attempt, request of about 10,000 bytes, not measured); about five all-5xx questions pause the day (same assumption); about 1,270 a month (10 / 0.00785, inherited, labelled estimate). Unconfirmed: that the deployed counter charges $2/$10 and the 33; both are marked "to be confirmed by the live smoke after the redeploy". Smoke figures come in an addendum after stage 10.

## Addendum after stage 10

Source: `18-production-verification.md` and the facts the Orchestrator gave (I did not re-open `smoke-result.json`). Every "not deployed yet" and "to be confirmed by the live smoke after the redeploy" line is replaced.

| File | Place | Change |
|---|---|---|
| README.md | recorded-figures cost row | deployed 2026-10-24 as `ca-aveto-ask--0000008`, image `d067b9a95ac6`, 2000/10000 live; gate was scored on `0000006` (kept as history); smoke cost $0.008544 (n = 5, 20,304 in / 211 out), within 15% of $0.0078; counter spend equals token cost at $2/$10 |
| README.md | "How the service counts spend" | heading now "deployed 2026-10-24, revision 0000008"; closing line replaced: 33 stays an estimate; smoke paragraph (g01/g03/g04 answered byte-identical, gu15/gu18 no confident match, no question text in logs, off 71.4 s, on not measured with about 73 s upper bound, rollback not rehearsed) |
| runbook | section 3 `/health` token row | deployed 2026-10-24, 0000008; smoke $0.008544 and spend equal to token cost |
| runbook | section 8 Cost and capacity | "to be confirmed" replaced; new smoke bullet with the same facts |
| runbook | section 8 Pricing | "not deployed yet" replaced by deployed 2026-10-24, 0000008, image `d067b9a95ac6`, smoke confirmation |
| CURRENT_MVP_STATUS | public service line | current revision 0000008 / `d067b9a95ac6`; `0000006` / `879cae23690b` named as the gate's revision |
| CURRENT_MVP_STATUS | "Spend accounting" | deployed, not merged; "runs earlier defaults" removed; smoke facts added; 33 kept as estimate |
| CURRENT_MVP_STATUS | "Not yet done" price line | now live, smoke recorded above |

Kept on purpose: README gate table "Revision `0000006`" and runbook "image `879cae23690b`" (F-LIVE-1) are history of what the gate and that fix used, not current claims. "Not merged" stays true. No release claim made. Not touched: SAFETY_INVARIANTS.md, code, STATE.md. The 33 a day is labelled an estimate. At $0.008544 per question the day pauses near 37 on cost alone (W2), so 33 stays binding.

## For the Orchestrator

1. **$0.0079 versus $0.0078.** The brief said to state $0.0079 "i.e. $0.1569/20". That quotient is $0.007845, which is $0.0078; the spec 3.3 recommends $0.0078 and the intent and Charter say $0.0078, so I wrote $0.0078 everywhere. Other places (earlier run records) may still say $0.0079.
2. No Bash tool, so I could not commit. The files are changed in the worktree and need the commit by the Orchestrator, with trailers `Aveto-Run: fix-service-accounting` and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; stage only the three files plus this note.
3. The runbook still describes the original three-command run (commands 1 to 5) as the deploy; I added the note on explicit `killSwitch` and literal values but did not rewrite the block to spec 7's literal form (the Orchestrator's command sheet is the source for that run).
4. The README says the PR closes #6, #7 and #8 "when merged"; the PR body must carry `Closes #6`, `Closes #7`, `Closes #8` (stage 11).
5. Not documented, by design: `billable_failures`, `NEVER_BILLED`, `MAX_ATTEMPTS` location (internal); the 429-then-success charge change is described only through the general charging rule (Security is still ruling on it, R1).
