# Stage 13 live record (Orchestrator, 2026-10-26; times UTC)

Service: `https://ca-aveto-ask.salmonsmoke-fa1fa863.eastus2.azurecontainerapps.io`. Image tag `ffc2e2e5f39a`; previous image `d067b9a95ac6`. Python could not verify the platform certificate chain ("self-signed certificate in certificate chain"; `curl` could), so `live.py` was run unedited through a scratch wrapper that only sets `SSL_CERT_FILE=/etc/ssl/cert.pem`. Verification stayed on.

| What | Record | Result |
|---|---|---|
| `check new` on revision 0000009 | `check-new.json` | ok (page, four suggestions, skip link, `/scorecard` 200, headers equal the literal set, `/warm` ready) |
| 7 live questions (C3.1) | `ask-result.json` | all 7 as expected (5 answer, 2 `no_confident_match`); passages byte-equal to local `retrieve` on every answered one incl. the form path; index sha256 `f36ef5d4…a756` equals the build's; counts delta +7 asked; spend $0.059978 for 7 (about $0.0086 a question); warm requests 2 to 7: median 1.36 s, slowest 1.59 s; request 1: 1.56 s |
| Log tables | `log-abuse.txt`, `log-search.txt` | 7 abuse lines `{"t","ip":"<16 hex>","o"}`, none shaped like request data; search for six question phrases: no rows |
| Rollback rehearsal (deployment 2, image `d067b9a95ac6`) | `check-old.json`, `watch-old-1.json`, `rehearsal-timing.json`, `../12-deploy/after-2.txt` | previous page served (no skip link, `/scorecard` 404), `/health` 200, revision 0000010 at 100 Healthy, env unchanged; command to first confirmed poll about 65 s (70 s to three polls); limit 600 s: PASS |
| Roll forward (deployment 3) | `check-new-after-forward.json`, `watch-new-1.json`, `../12-deploy/after-3.txt` | revision 0000011 at 100 Healthy, image `ffc2e2e5f39a`, env unchanged; about 65 s (70 s to three polls): PASS |
| Cold start | `cold.json` | **25.8 s** to the first `/health` 200, then `GET /` 0.31 s. Method as the earlier 30.8 s record, but the replica had been idle about 7 minutes (replica count read as 0), not more than an hour |

Not tested live: the kill switch (C8.3 allows a toggle only if C8.1 requires one). Rollback time is the watcher's first of three consecutive polls minus the gap between watcher start and the logged create time; resolution about 1 to 2 s. Deployment run times (ARM): 40.7, 40.1 and 40.4 s.
