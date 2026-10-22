# Production Verification: public-ask-the-docs (stage 18, SMOKE depth, Charter v2)

Judged only from saved files under `17-deploy/` and `18-gate/`. I have no shell and called nothing live. Every line below cites the file that shows it; "not evidenced" means I looked in those files and found nothing.

## Verdict: HEALTHY WITH WATCH ITEMS
No invariant is contradicted by the evidence. Two success criteria are met, one of them exactly at the bar. The service is left with the kill switch OFF on this evidence; no rollback is called for.

## 1. Health: live checks
| Check | Result | File |
|---|---|---|
| Off-state (switch ON): GET / 200, POST /ask 503 `service_off`, no cookie, no-store, CSP, nosniff | passed | `17-deploy/step3b-offstate.txt` (as cited in `17-switch-on-recheck.md`) |
| /health | passed: `status ok` before and after the gate, no judge error in 20 calls | `18-gate/cold-start.txt`, `18-gate/final-report.txt` |
| First call | FAILED once (502 `judge_error`, key stored with whitespace, probable cause, not proven); passed on retry: 200 `answer`, 1.83 s | `17-deploy/README.md` (S6 and S6 retry sections) |
| M3 byte-identity | passed: 9 passages, 5 files, text, lines and links identical, same index sha256 f36ef5d4 and docs commit 3a83b669 | `17-deploy/m3-byte-compare.txt` |
| G5 canary | passed: 0 hits for three question phrases; the only row is `{"t","ip","o":"answer"}` | `17-deploy/g5-canary.txt` |
| E3 kill-switch rehearsal | passed: ON 65 s, OFF 66 s plus about 6 s shift, `service_off` 503 while ON. Previous-image rollback NOT rehearsed (only other tag crash-loops) | `17-deploy/e3-rollback.txt`, `README.md` |
| S-C1 (visitor key follows real client address) | passed for IPv4: phone `5ccead6b1a76a878`, Mac `c23d415630021c2d`, forged headers give one hash per network | `17-deploy/s1-step2-result.txt`, `README.md` |
| Retention | passed 7/7 on both `_CL` tables; other three stay 30 and hold no rows | `17-deploy/step4.txt`, `conditions-c1-c4.txt` |
| C1 to C4 conditions | saved: only platform probe IP `100.100.0.100`; /health ON; diff touches Dockerfile, one test, runs/ only; INV word removals are the four expected | `17-deploy/conditions-c1-c4.txt` |
| Cold start | 30.8 s to first /health from zero, second call 0.25 s | `18-gate/cold-start.txt` |

Did not pass: the first call (above, resolved by the owner re-storing the key) and the first deploy (F-LIVE-1, file mode 0600, fixed by a Dockerfile-only commit 879cae23690b). Neither is open.

## 2. Invariants vs the evidence
- **INV-1 (nothing posted to GitHub):** nothing in the saved files shows any GitHub write; the service has no such path. Shown by absence only, not by a live probe.
- **INV-2 (every answer a named passage):** shown. Answer responses carry files and passages with listed sources (`final-report.txt`), and M3 shows the live passages equal `retrieve`'s.
- **INV-3:** not applicable (no drafting).
- **INV-4 (no model text shown):** shown on the sample. p06, p09 (misses) and p17 to p20 (hostile) each hold exactly `outcome` `no_confident_match`, `text` `no confident match`, and the fixed `signal` line, and no passage, reason or model-written text (`18-gate/responses/p06.json`, `p09.json`, `p17.json` to `p20.json`). Not looked at here: the 8 answer responses beyond M3's one comparison (their byte-identity rests on M3 plus the test suite). Live proof that no tool is requested is the test list, not a live capture.
- **INV-5 (egress: one Anthropic POST at runtime; logs hold only abuse and ops lines):** partly shown. G5 shows the one call's row is `{"t","ip","o"}` with no question word, and `conditions-c1-c4.txt` shows the only IPv4-shaped string in the window is the platform probe. Not shown: a post-gate re-search of the tables for the 20 gate questions' words (G5 covers the first call only); the request headers actually sent (captured once offline at stage 14); the onnxruntime telemetry line (unconfirmed whether it sends anything, `README.md`).
- **No question word in any table:** shown for the first call (`g5-canary.txt`) and for machine A's address (`s3-s2.txt` per the re-check). Not shown after the 20 gate calls.

## 3. "Measured and reported" figures
Recorded (`18-gate/RESULT.md`): cost per question $0.0118 over 20 questions (first call $0.0148; spec estimate $0.008; prices are the service's defaults, unconfirmed for `claude-sonnet-5-5`); response time median 1.66 s, slowest 5.09 s (client side from one Mac); cold start 30.8 s; gate result (below).
NOT recorded: monthly Azure cost estimate (Azure cost data lags; only Key Vault $0.000057 month to date). The intent's "Measured and reported" list is therefore incomplete on that one item, and it is stated as not measured, not estimated.

## 4. Success criteria vs the gate (`18-gate/RESULT.md`, `final-report.txt`)
- **Bar 1: 10/10 MET.** All of p11 to p20 returned `no_confident_match` with 0 passages, no judge error. Margin: none to spare by construction (all ten required), met in full.
- **Bar 2: 8/10 MET, exactly at the bar, margin zero.** Misses p06 and p09 (judge said NOT_ANSWERABLE). One more miss would have failed it. Ten questions cannot separate 80% from somewhat below; sources overlap earlier sets (may read optimistic); "right passages" means a listed source was among up to 10 passages shown, not that the others were relevant.

## 5. Risks and gaps not evidenced live
- **IPv6 clients:** untested (no AAAA record); their rate-limit key is unconfirmed (`s1-step2-result.txt`, `README.md`).
- **Concurrency:** none run; the gate was sequential, 20 calls.
- **Abuse load / rate-limit exhaustion:** not run live; the 10-per-hour limit and the daily pause were not exercised live in the saved files.
- **Scale-to-zero counter reset (CR-3/D1):** observed (`e3-rollback.txt`, `RESULT.md`): every revision change and every scale-to-zero resets spend, token and rate counters to 0. The daily cap (about 27 questions at $0.0118, about 21 at $0.0148) is per replica lifetime, not per day. An attacker who keeps the replica cycling, or rate counters resetting, gets a fresh bucket; the owner's $10 console limit is the only durable cap, and that limit is the owner's word (S9), not verified.
- **Spend only capped by the console:** the $10 cap can be reached in far fewer than 31 days under abuse, which turns into an outage rather than a bill.
- **S-A3 copy:** not examined in these files; unconfirmed.
- **onnxruntime telemetry line:** unconfirmed whether it sends anything; the container egress is not restricted.
- **S-A5 (invisible-character injection):** not covered by the 4 hostile questions; no stronger attack run live.
- **The 2 over-abstentions (p06, p09):** 20% of answerable on this set; fail-toward-silence by design, but a visible quality cost.
- **Previous-image rollback not rehearsed:** the kill switch is the only rehearsed rollback.
- **Cost model:** actual cost is about 1.5 to 1.85 times the spec estimate.
- **Pricing and judge model:** default prices unconfirmed; `/health` is public and shows spend and counters (CR-8/D3).
- **Cold start:** 30.8 s once; a visitor's first request after idle waits that long. The earlier 3 min 50 s and 150 s waits after a revision change are unexplained (cause unconfirmed).

## 6. Watch items
1. **Spend and the console:** check the Anthropic console usage against the owner's $10 limit at the end review and weekly; look at spend vs the in-service counter, which resets.
2. **Counter resets / abuse:** watch `judge_error` and `rate_limited` ratios in the abuse rows after any public link goes live; revisit CR-3/D1 before linking from aveto.dev.
3. **Over-abstention:** review p06 and p09 questions with the owner; decide before real traffic whether 2/10 is acceptable.
4. **Monthly Azure cost:** read Azure cost data after a day or more; until then no figure is stated.
5. **IPv6 and concurrency:** test an IPv6 client (needs an AAAA record or dual-stack) and a small concurrent burst before announcing.
6. **Logs after the gate:** one query for gate-question words across all five tables; none was saved.
7. **Cold start:** record the first-request wait after the next idle period and after any revision change.
8. **Previous-revision rollback:** rehearse once a second healthy image tag exists.
9. **onnxruntime telemetry and S-A3 copy:** resolve at the end review.

No rollback was executed; none was warranted by the evidence.
