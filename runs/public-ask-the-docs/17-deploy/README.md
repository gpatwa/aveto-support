# Stage 17: deploy with the kill switch ON (Orchestrator's session, Charter v2 C8.3)

All commands ran from the worktree root, in tech spec §7 order. No command printed a secret; every saved output was searched for `sk-ant` and key-shaped strings (0 hits). The Azure subscription IDs are masked in the saved files.

| Step | UTC | Result | File |
|---|---|---|---|
| 1 what-if, create (no app) | 05:35 to 05:38 | Only C8.3 types; identity, registry, workspace, environment, both role assignments created; vault "Ignore" | step1-whatif.txt, step1-create.txt |
| 2 `az acr build`, tag `0fa04abda8ad` | 05:38 to 05:40 | built, pushed; ingest index sha256 f36ef5d4…a756 = the local index (S4 match) | step2-build.log |
| 3 what-if, create (app, switch ON) | 05:40 to 05:42 | created; **first start failed**: `startup_failed` category `index`, CrashLoopBackOff (F-LIVE-1: ingest writes files mode 0600; the runtime uid 10001 could not read them) | step3-*.txt, step3-offstate.txt |
| D4 hand-back | | Dockerfile fix by the Backend (`--chown=root:10001` plus `chmod`), new commit 879cae23690b, P2 re-run (637 passed), checklist reopened | 17-p2-recheck-2.txt, 11c-infra-checks.md |
| 2b rebuild, tag `879cae23690b` | 05:48 to 05:51 | built, pushed; same index sha256 f36ef5d4…a756; base digests as pinned | step2b-build.log |
| 3b what-if, create (app, switch ON) | 05:51 to 05:53 | revision `ca-aveto-ask--0000001` Healthy, `startup_ok` 05:52:49 | step3b-*.txt |
| D3 off-state | 05:55 | GET / 200 "The service is off", POST /ask 503 `service_off` (JSON and form), /health `kill_switch":"on"`, no Set-Cookie, no-store, CSP, nosniff, no-referrer | step3b-offstate.txt, served-index-off.html |
| 4 retention | 05:56 to 05:57 | `ContainerAppConsoleLogs_CL` and `ContainerAppSystemLogs_CL` read back 7 / 7 (S-C2 met); the three other ContainerApp tables stay 30 and hold no rows | step4.txt, s3-s2.txt |

## Switch-on gate (release checklist 9B), where it stands
- **S1 (S-C1): PARTLY MET, step 2 not run.** Step 1 passed: 10 requests with different forged `X-Forwarded-For` values (empty, public, private, IPv6, garbage, multi-entry) all logged the same `ip` `f0dc6b0b54a5e4b4`. Step 2 (a request from a different public network must log a different `ip`) could not be run: this machine has one public network. The IPv6 attempt was not independent: the service has no AAAA record, so `curl -6` connected to the IPv4-mapped address and the three IPv6-labelled requests hit the same hash (an invalid test, not a pass or a fail). Until step 2 runs, the ingress's behaviour is unconfirmed, the kill switch stays ON, and the service shares at most one bucket if the ingress hands every visitor the same address (fail-closed, and what the unproven `peer` fallback would also do).
- **S2: MET** (7/7). **S3: MET** for machine A (0 hits for the raw address in any table; only the two `_CL` tables hold data). **S4: MET** (hash match, digests recorded). **S5: PARTLY**: both ON revisions verified; from the second deploy command (05:51:51) to the first 200 from `/health` took about 3 min 50 s, but the previous revision was crash-looping, so this is not the time for a healthy-to-healthy kill-switch change (E3 measures that). **S8: MET** (the five strings are in the served page). **S9:** owner's statement only. **S6, S7: not yet** (they run after the switch is turned off).

## Other findings
- First request after a deploy waited 150 s with no response twice (the first deploy was crash-looping; the second revision was Healthy at 05:52:49 yet the public URL answered only at about 05:55:40). Cause unconfirmed (ingress propagation after a revision change is the likely one); recorded for the cold-start figure at stage 18.
- onnxruntime logs one warning line at startup (`telemetry.cc ... Failed to persist telemetry device ID; using an in-memory identifier`). It carries no visitor data; it is ONNX Runtime's own telemetry setting (unconfirmed whether it sends anything: the container's egress is not restricted, and the INV-5 words promise only the Anthropic POST at runtime). Carried to the end review for Security.
