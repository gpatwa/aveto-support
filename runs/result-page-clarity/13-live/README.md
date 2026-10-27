# Stage 9/10 live record (Orchestrator, 2026-10-27; times UTC)

Service: `https://ca-aveto-ask.salmonsmoke-fa1fa863.eastus2.azurecontainerapps.io`. New image `aveto-ask:16f9bda31836` (HEAD `16f9bda31836`, built by `az acr build`, run ch5, 2m20s, log `../12-deploy/acr-build.log`). Previous (rollback target) image `ffc2e2e5f39a`, revision `ca-aveto-ask--0000011`. What-if ruling: `../12-deploy/whatif-1-ruling.md`. Python needed the platform CA bundle as in the last slice: a scratch wrapper in the session scratchpad sets `SSL_CERT_FILE=/etc/ssl/cert.pem` and nothing else; `live.py` itself unedited; verification on. (`live.py` writes into the last slice's folder; its output was copied here and the old files restored with `git checkout`.)

| What | Record | Result |
|---|---|---|
| Deployment 1: new image | `../12-deploy/d1-*.txt`, `after-1.txt` | Succeeded in 66 s (06:45:02 to 06:46:08); revision `0000012` at 100, image `16f9bda31836`; env identical (kill switch off, prices 2000/10000, cap 10, client key xff_last) |
| `live.py check new` on the new revision | `check-new.json` | ok, all nine checks true (page, four suggestions, skip link, `/scorecard` 200, headers equal the literal set, `/warm` ready) |
| Live heading position, JavaScript swap, 1280×800 (2 live questions, C3.1) | this table | answered **16.1 px** (2.0%), refused **16.1 px**; focus on `#result`; DOM order `H1,P,ask-form,ready,result,H2,UL,H2,sugg-hint,suggestions`; the answer took 2.3 s; the script served live contains `preventScroll` |
| Live heading position at 375×667 | this table | the two stored result pages reopened at `#result` (the load path, not the swap path): answered **17.6 px** (2.6%), refused **15.6 px** (2.3%); focus on `#result`; scrollWidth 375. The questions were sent once each (at 1280×800); the 375 px figures are the server-rendered path |
| Judge outcomes | this table | question 1 (suggestion 1) answered with 10 passages; question 4 (suggestion 4) refused with "The docs don't answer this"; as labelled. Byte comparison with local `retrieve` was not run (`live.py ask` sends 7 questions; C3.1 allows 2) |
| Deployment 2: rollback rehearsal, `imageTag=ffc2e2e5f39a` | `../12-deploy/d2-*.txt`, `after-2.txt`, `rehearsal-polls.txt` | Succeeded in **65 s** (06:48:03 to 06:49:08); revision `0000013` at 100 Healthy, image `ffc2e2e5f39a`, env unchanged; `/health` 200, home 200, and the served `enhance.js` has no `preventScroll` (the previous page) at 06:53:19, 06:53:23, 06:53:27 |
| Deployment 3: roll forward, `imageTag=16f9bda31836` | `../12-deploy/d3-*.txt`, `after-3.txt`, `forward-polls.txt` | Succeeded in 65 s (06:53:47 to 06:54:52); revision `0000014` at 100 Healthy, image `16f9bda31836`, env unchanged; first poll with `/health` 200 and the new script: **67 s** after the command (poll every 2 s) |
| After the roll forward: `check new` | `check-new-after-forward.json` | ok, all nine true |
| After the roll forward: heading position (an empty-question error page, a native form post, no model call; the live questions were spent) | this table | 1280×800 **16.1 px**, 375×667 **15.6 px**, focus on `#result` |
| Log tables | `log-abuse.txt`, `log-search.txt` | abuse lines are `{"t","ip":"<16 hex>","o":"answer"|"no_confident_match"|"bad_request"}`; a search of all tables since 06:36Z for three question phrases returned no rows |

## Gaps, stated plainly
- **Rollback timing not polled.** After deployment 2 my poll loop used `live.py check old`, which tests for the page before the last slice (no skip link, `/scorecard` 404), so it could not pass on the previous image (`ffc2e2e5f39a`, the last slice's page). The loop ran blind until 06:53; the first recorded `/health` 200 on the previous image is 06:53:19. What is measured for the rollback is the deployment's own completion (65 s, revision Healthy at 100 afterwards); a time from command to first healthy `/health` poll was not measured. The roll forward was polled properly (67 s). The Charter allowed three deployments, so the rehearsal was not repeated.
- The 375×667 live figures are the page-load path, not the JavaScript swap; the swap at 375 px is the local figure (15.6 px) from `08-browser-checks.md`.
- The post-roll-forward heading check used an error page, not an answer or a refusal.
- No byte comparison of the live passages with local `retrieve`; no cold-start or warm timing was taken (not a Charter bar for this slice).
- The kill switch was not toggled (C8.3 allows it only if C8.1 requires one).
