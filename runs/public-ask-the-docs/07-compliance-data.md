# Compliance and data governance review: public-ask-the-docs (stage 7, Compliance Reviewer with Data Governance folded in, depth standard, 2026-10-21)

Sources read: `intent.md`, `CHARTER.md` (C3.1, C4.1, C4.2, C5.2, C8.3), `05-tech-spec.md` (all), `06-ai-risk-assessment.md` (sections 2, 3, 6), `04-ux-spec.md` (section 2 copy), `aveto_support/judge.py` `format_judge_input` (what the payload holds), `runs/land-answerability/03-vendor-risk-note.md`, `runs/docs-answerability-2/11b-vendor-risk.md`. **(U)** = not confirmed; each says where I looked. No web access and no Anthropic or Azure document read in this stage. The repo commits to no certification (searched `.agentic/`, `docs/`, ADRs, stage 1-4 artefacts for SOC 2, ISO 27001, GDPR, certif: none), so the framework IDs below are reference points an auditor would use, not a claimed scope. Control IDs are from memory of the frameworks, not re-read.

## 1. Verdict

**PASS WITH REQUIRED FIXES at design stage. No STOP.** Each fix in section 7 is a Release Gate block if unmet. One judgement call on C4.1 for the Orchestrator is in section 2 (transport metadata). Top gap: **the page copy (UX section 2) does not yet say what the AI risk review requires (R1) and what this data map needs**: "Questions are not stored or logged" sits next to a question sent to a processor whose retention is unknown, and nothing tells visitors not to type personal data. Second: **whether the platform writes the raw visitor IP anywhere in the workspace is unknown (U)**; the page's "scrambled form of your address" would be false if it does.

## 2. Processors and exactly what each receives (checked line by line against C4)

### Anthropic (C4.1) - the spec sends, per question, in one POST to `api.anthropic.com/v1/messages` (spec 2.2)

| Sent | Source in spec | C4.1 names it? |
|---|---|---|
| `system`: `answerability-judge-v1`, byte-exact, hash-checked at start | 2.2, 1.2 step 3 | Yes ("the fixed judge prompt") |
| one user message = `format_judge_input(result)`: block id, `Question: <normalised question>` (at most 500 chars, checked before any call), per passage `File n: <path>`, `heading`, `lines a-b`, the passage text | 2.2; `judge.py` lines 112-134 (read) | Yes (question; passages with paths, headings, line ranges). Passage text is the passages themselves. No scores, URLs or labels (read in `judge.py`). |
| `model: claude-sonnet-5-5`, `output_config.effort: high` | 2.2 | Named by C3.1, not C4.1: protocol fields, no data |
| `max_tokens: 1024` | 2.2 | Not named anywhere in the Charter: a numeric protocol limit, no data |
| `x-api-key` | 2.2 | Named by C5.2 (the key) |
| `user-agent`, `anthropic-version`, `x-stainless-*` (OS, arch, runtime, package version of the **container**) | 2.2 (spec marks the exact set (U)) | **Not named by C4.1.** Facts about our container, none about a visitor. |
| Not sent: `metadata`, `tools`, `temperature`, any visitor IP, header, hashed key, user agent | 2.2 "Never sent"; adapter signature has no such parameter; `test_request_body_only_c41_data` | C4.1: "No IP address, visitor identifier or visitor request header" - **consistent** |

- **Judgement call (not a STOP in my reading, flagged because the instruction is strict):** `max_tokens` and the SDK's own `user-agent` / `x-stainless-*` headers are not named in C4.1. They are inherent to making the Charter-approved API call, they carry nothing about a visitor, and Security is already asked to rule on them (spec 11, stage 14). If the Orchestrator reads C4.1 as closed to even these, the remedy is a one-line owner acknowledgment at the end review, not a code change. I make no new field a requirement and I do not widen C4.1 myself.
- Anthropic also sees, by the nature of the connection, the **Azure outbound address** (not the visitor's) and the owner's API key identity. Neither is visitor data.
- **Unknown, not guessed:** whether the exact SDK header set holds anything else (spec 2.2 says not read); I did not read the SDK source myself.

### Microsoft Azure (C4.2) - against C8.3's resource list, `rg-aveto-ask`, eastus2

| Receives | In C4.2? | Note |
|---|---|---|
| Container image (code, pinned index and models, public docs text) | Yes | `.dockerignore` excludes `.git`, `runs/`, `.claude/`, `.env*` (spec 6): the run artefacts that name the owner stay out. Whether `az acr build` honours it when it uploads the context: (U), not tested. |
| Key Vault secret `anthropic-api-key` | Yes | A credential, not personal data |
| Visitor HTTPS request in transit through ingress | Yes | **Contains the visitor's raw IP and the question in the POST body.** Azure is a processor of both in transit. |
| Log Analytics: abuse lines and ops lines (stdout) and revision events (`ContainerAppSystemLogs_CL`) | Yes ("only the service's abuse log lines ... and platform logs that carry no question text") | C4.2 does **not** say the platform logs carry no IP, only no question text. See section 4, row "platform logs". |
| Azure Monitor platform metrics (request counts, replicas, restarts), Azure Activity Log (control-plane operations, deployment parameters), ACR build logs | Not named | Azure-generated about our resources; no visitor data. Noted so the processor record is complete. Deployment parameters hold no secret (spec 7). |

**Verdict on C4 line by line: no field carries visitor data to a processor that C4 does not name.** The IP reaches only Azure ingress (in transit) and the service's memory; the question reaches only Azure in transit and Anthropic. Nothing else is named, so the C4 text and the spec agree.

## 3. Terms status (what is known, what is UNKNOWN)

| Item | State | Source |
|---|---|---|
| Anthropic account and terms | Metered API under the **Commercial Terms**, which incorporate the **Data Processing Addendum by reference**; the owner read the terms 2026-10-20 | `intent.md` lines 29-30; `CHARTER.md` C4.1 |
| DPA text | **Not read by anyone recorded.** The owner's statement is that the DPA is incorporated by reference; no agent has seen the clause, the date or the version | `intent.md` ("the DPA text itself not yet read"); C4.1 |
| Change since the earlier notes | Both earlier notes (personal subscription, **no DPA**, rule "public-docs questions only") are superseded for this service: the account, the terms and the channel all differ. Their "DPA in place" row read NOT in place. For this slice the row is **"in place by reference, per the owner's statement; text unread; not verified"**, not MET. The earlier operating rule cannot work here: no one types for a public visitor, so the page must carry the warning (section 6) | the two earlier notes, read |
| Vendor retention of prompts and replies | **UNKNOWN** (no period stated by any artefact) | C4.1 "not verified by an agent" |
| Training or improvement use of API inputs | **UNKNOWN** | same |
| Subprocessors and disclosure | **UNKNOWN** | no artefact |
| Data residency; transfer basis (visitor to eastus2 Azure, then Anthropic) | **UNKNOWN**. Azure region is eastus2 (US, C8.3); Anthropic's processing location not stated anywhere. Any EU or UK visitor's question and IP leave their region; a named legal basis (adequacy, SCCs, other) is not recorded | no artefact |
| Breach-notification and liability terms; certifications (SOC 2, ISO 27001, ISO 42001); status page | **UNKNOWN** | carried from the earlier note |
| Whether the terms and usage policy permit a public, unauthenticated, consumer-facing use, and any required disclosures | **UNKNOWN**; a contract reading, escalated to the owner | not made |
| Azure terms | The owner's Visual Studio Enterprise subscription terms (C4.2). Whether that offer's terms permit production hosting of a public service: **UNKNOWN**, a contract reading for the owner | C4.2; C6.4 |
| GDPR Art. 28 | Visitors' questions are data the owner chooses to send, so Art. 28 (processor terms) probably applies to Anthropic and to Azure **(U): a legal reading I do not make** | |

## 4. Data map (classification, lineage, residency, retention, enforcement)

Classification scale: public / internal / confidential / restricted. No PHI or PCI is collected by design; a visitor can still type anything into the box (section 6).

| Element | Class | Origin and flow | Where it lives | How long | Enforced by (evidence) |
|---|---|---|---|---|---|
| Raw visitor IP (and `X-Forwarded-For`) | **Personal data** (confidential) | visitor -> Azure ingress -> container; the rightmost entry is read (spec 3) | Ingress in transit; the service's request object in memory; **not written** by the service | Request lifetime | Spec 3, 5: only the HMAC reaches state or logs; `test_client_key_rightmost_xff`, `test_abuse_line_shape_exact`. Whether ingress persists it anywhere: **(U)**, see "platform logs" |
| Hashed IP key (HMAC-SHA256, per-process random 32-byte salt, IPv6 as /64) | Personal data **question open** (section 5); confidential | derived in the service | **Memory** (rate-limit table, at most 50,000 keys, swept after 1 h idle) | Until the replica stops (scale to zero about 300 s idle (U)) or 1 h idle | `limits.py` per spec; `test_client_key_store_full_fails_closed` |
| Abuse line `{t, ip(16 hex of the HMAC), o(outcome code)}` and ops lines | Internal; the `ip` field is the hashed key above | stdout -> Container Apps -> `ContainerAppConsoleLogs_CL` | Log Analytics `log-aveto-ask` | **7 days** by table setting; workspace default 30 | Spec 5: `retentionInDays: 7` and `totalRetentionInDays: 7` on the two tables, applied at step 4 before the kill switch goes off. Evidence at stage 17: `az monitor log-analytics workspace table show ... --query "{r:retentionInDays,t:totalRetentionInDays}"` prints 7 and 7. **(U)** that a table can be set below 30 days (spec says from memory 4 to 730); **(U)** that expiry deletes promptly (Azure documents purge timing; not read) |
| Visitor question | **Personal-data risk** (free text); confidential | visitor -> ingress -> service memory -> Anthropic | Service memory for the request; Anthropic per its terms; **never** a log, a URL, the result store, a cookie | Request lifetime here; **Anthropic: UNKNOWN** | `test_question_never_logged`, `test_result_store_holds_no_question`, `test_question_never_in_url_or_title`, no-cookie test (spec 10); `uvicorn --no-access-log --log-level critical`; library loggers silenced |
| Retrieved passages and result store (token, outcome, passages) | Public (public docs) | memory | Memory, 10 minutes, at most 1,000 entries | 10 min | `result_store.py` per spec |
| Judge reply (reason line) | Internal | Anthropic -> parser | Parser only; dropped | Instant | `test_reason_never_leaves_parser_service` |
| Platform logs (`ContainerAppSystemLogs_CL`, any ingress or request record) | Possibly personal if they hold the client address | Azure | Log Analytics | Table setting 7 days if the two named tables; **any other table keeps the workspace default of 30** | **(U)**: spec 5 says it did not read whether ingress writes per-request records; I found nothing in the Charter or spec that rules a raw IP out, and C4.2 says only "no question text". Stage 17 must list the workspace tables after the first requests and search them for the visitor's own address (section 7, G3) |
| Anthropic API key | Restricted (secret) | owner -> Key Vault -> Container Apps secret reference -> env | Key Vault; container env | Until rotated | Key Vault reference only; no literal in Bicep or image (`test_bicep_no_secret_literals`, `test_dockerfile_static`); the value was never read by an agent (C6.5) |
| Gate and verification questions (stage 17/18) | Internal; written by the support session | operator -> service -> Anthropic | Same path as a visitor's | Same | No personal data by design; hostile questions contain no real person's data (not read: **unconfirmed**, the file is unread before stage 18 by C6.7) |

- **Residency:** Azure eastus2 (US) for compute and logs. Anthropic location UNKNOWN. A visitor outside the US is therefore subject to a cross-border transfer of IP (in transit) and the question (to Anthropic). **No legal basis is recorded; this is the owner's/legal's, not assumed here.**
- **Lineage is traceable for the abuse log only**: visitor IP -> HMAC in memory -> stdout -> Log Analytics -> expiry at 7 days. There is no export path: the logs are readable in Log Analytics by the owner for 7 days only, and no one reviews them automatically (O2/M1 in `06`).
- **Append-only / audit export:** the service has no audit trail beyond these lines and `GET /health` counters, and no audit-export obligation exists in the Charter or repo (searched `.agentic/`, Charter). Not applicable; stated so the absence is a decision. The 7-day window means an investigation older than a week has no log: accepted by C4.2.

## 5. Is a hashed IP still personal data? (the question, for the owner/legal, not decided here)

Facts that bear on it, so the owner can ask the right question:
1. The service **does process the raw IP** (it reads it to compute the hash and apply the limit). Processing an IP address is itself processing, whatever is stored afterwards. Azure ingress also carries it.
2. The stored value is a keyed hash (HMAC-SHA256) whose key is a random 32-byte salt held only in process memory and never logged. Without the salt the 16-hex value (64 bits) cannot be turned back to an address, and the small IPv4 space does not help an attacker who lacks the salt.
3. **But the value is linkable**: within one replica's life, the same visitor yields the same value on every line, so a visitor can be singled out and their activity followed. After the replica stops, the salt is gone and the old lines can no longer be linked to new ones or to an address.
4. Pseudonymised data that can still single out a person is generally treated as personal data in the GDPR sense (recital 26 reasoning, from memory, not re-read). Whether this one counts, under which law, with what legal basis for the abuse-prevention purpose (legitimate interest is the usual candidate: my note, not a ruling), whether a notice is due, whether Art. 30 (record of processing) bites for a small operator, and whether the owner is the controller: **all legal judgements for the owner**. The recommendation here is the cautious one: treat it as personal data for the retention and notice work below, and say so in the end review.
5. The page already says "scrambled form of your address", which is accurate for the stored value but incomplete (it omits that the address is read to do the scrambling and travels via Azure).

## 6. What the page must tell visitors (release condition; the built page is checked, not the spec)

Current copy (`04-ux-spec.md` section 2) already names Anthropic, the 500/10-an-hour limits and the 7-day hashed-IP note. It lacks, and must gain before the deploy (these extend `06` R1/T1-T3 with the data map):
1. **Say an AI model decides**, using "AI model" or the model's name, not only "a model" (EU AI Act Art. 50(1)-type disclosure, see section 8).
2. **Do not enter personal or confidential data.** (absent: searched the UX spec for "personal" and "confidential": no match.)
3. **Qualify "Questions are not stored or logged."** It is true of this service only. Add that the question is sent to Anthropic (named) and **its handling there is under Anthropic's terms, not this page's control**. Do not write that nothing is kept, or that anything is deleted, anywhere beyond this service.
4. State that **the address is read to apply the limit** and that the hash plus time and outcome are kept 7 days.
5. State that the service is hosted in the **US** (Azure eastus2) and that data is processed there and by Anthropic.
6. Link a contact for the owner (issue link exists) and a short privacy notice; whether a fuller notice is needed is the owner's legal call.
Wording is the Frontend's and Tech Writer's; I fix the facts, not the sentence.

## 7. Required fixes and controls the Release Gate (tier 3) checks

Each is a block if unmet. Evidence must be an artefact, not a statement.

| # | Control the gate checks | Evidence that satisfies it |
|---|---|---|
| G1 | Page copy has items 1 to 5 of section 6 (and `06` R1) | Release Manager reads the built page's rendered HTML or `test_every_state_renders` output against section 6; plus a test that the page contains "Anthropic" and the not-personal-data sentence |
| G2 | 7-day retention is **set before any visitor request is served** and read back | Stage 17 output of the `table show` command for both tables: 7 and 7; deploy order step 4 before step 5 (spec 7) |
| G3 | No raw visitor address in any workspace table | Stage 17: list tables (`az monitor log-analytics workspace table list`), query each non-empty table for the tester's own public address after a few empty-question requests; result recorded. Any hit, or any extra table with the default 30-day retention holding it, is a block and a report to the owner (C4.2 would then be wider than its words) |
| G4 | The XFF assumption (rightmost entry is the client) | Stage 17 forged-header check (spec 3): different forged values from one machine log the same `ip` hash; else `ASK_CLIENT_KEY=peer` (fails closed) |
| G5 | Question never leaves the allowed path | `test_question_never_logged`, `test_request_body_only_c41_data`, `test_request_has_no_tools`, `test_result_store_holds_no_question`, `test_question_never_in_url_or_title` green; plus at stage 17 one canary question through the live service and a search of the workspace tables for it: zero hits |
| G6 | Key never in image, repo or logs | `test_dockerfile_static`, `test_bicep_no_secret_literals`; Security's secret scan at 14 |
| G7 | Processor record exists (section 9) before step 5 | The entry is in the runbook (`docs/runbooks/public-ask.md`) in the same slice; Release Manager sees it |
| G8 | Owner records, in his own words in `END_REVIEW.md`, a line on the open legal items: hashed-IP status, controller role, transfer basis, notice (section 5), whether Anthropic's and Azure's terms permit a public service, and the unread DPA text (`06` R2) | A sentence in `END_REVIEW.md`, not a verbal statement. Until then these stay **open, not accepted** |
| G9 | The vendor "DPA" row is written as "in place by reference per the owner's statement; text unread", never MET | Release checklist text |
| G10 | The Anthropic console cap is set (C6.6) | The owner's statement in session (unverifiable by an agent: labelled so) |

## 8. Control mapping (reference frameworks; no certification is claimed)

| Thing touched | Control(s) | Evidence | Shared-control note |
|---|---|---|---|
| New processor Anthropic; Azure as host | GDPR Art. 28; SOC 2 CC9.2; ISO 27001 A.5.19-A.5.22 | Section 2 and 3; G7, G8, G9 | One processor record serves all three |
| Record of processing | GDPR Art. 30; ISO 27001 A.5.34 | Section 9 entry | |
| Minimisation: no question stored, no IP stored raw, no visitor identifier to Anthropic | GDPR Art. 5(1)(c), 25; ISO 27001 A.5.34 | Section 4 tests (G5) | Also satisfies SOC 2 Privacy P3-P4 in spirit (from memory) |
| Retention: 7-day logs | GDPR Art. 5(1)(e); ISO 27001 A.8.10 (deletion), A.8.15 (logging); SOC 2 CC7.2 | G2 read-back | One config value is the evidence for all |
| Transparency to visitors | GDPR Art. 13; EU AI Act Art. 50(1)-type duty | G1 | |
| Cross-border transfer | GDPR Ch. V (Art. 44-46) | Basis not recorded: G8 | Escalated |
| Secret handling | ISO 27001 A.5.17, A.8.24; SOC 2 CC6.1 | G6 | Security owns the vulnerability review |
| Kill switch, limits, 7-day monitoring | SOC 2 CC7.2-CC7.4; ISO 27001 A.5.24-A.5.26 | `06` section 7; tests | No push alerting (M1/O2) is a monitoring gap the owner accepts in words |
| AI governance of the judge | ISO 42001 (A.5 impact, A.6 lifecycle, A.8 information to interested parties, A.10 third parties; IDs from memory) | `06` inventory entry, section 8 | |

**AI obligations.** Tier: **limited, provisional** on OI-1 (`06` section 2). This is a **real model call** in a rule-5 path, so Art. 50 is a precondition, not an advisory: (a) **Disclosure to users that they interact with AI: required and not yet in the copy** ("a model", not "AI model", and the not-personal-data line is missing). It becomes satisfied when G1 passes; if the built page lacks it, the slice **fails**. (b) **Provenance (watermark or metadata) on generated or altered content: nothing is generated or altered.** Every shown character is copied from the docs and checked byte-identical (`test_service_passages_byte_identical_to_retrieve`); the model output is a verdict token that is parsed and dropped. So there is no content to mark. This is my reading of `06`'s screening, not a legal ruling; if the owner/legal reads "selecting the passages shown" as altering, the fix is a metadata field and I would block. For API consumers the JSON `signal` line already names the model's verdict. **GPAI duties** sit with Anthropic as the model provider; the owner is a downstream deployer. Anthropic's GPAI Code of Practice status: **UNKNOWN** (no web). `claude-sonnet-5-5` snapshot vs alias unconfirmed (`06` D1).

## 9. Processor inventory and RoPA delta (none exists in the repo; this is the entry)

| Field | Anthropic | Microsoft Azure |
|---|---|---|
| Purpose | Decide whether retrieved docs passages answer a visitor's question | Host the service; platform logs for 7 days |
| Data subjects / data | Visitors; the question, public passages | Visitors; raw IP and request in transit; hashed IP, time and outcome in logs |
| Channel | HTTPS to `api.anthropic.com`, metered API, key from Key Vault | Container Apps, `rg-aveto-ask`, eastus2 |
| Terms | Commercial Terms with DPA by reference (owner, 2026-10-20; DPA text unread) | Owner's Azure subscription terms (unread by an agent) |
| Retention | **UNKNOWN** | 7 days for the two named tables; others UNKNOWN until G3 |
| Residency / transfer | **UNKNOWN** | US (eastus2); basis not recorded |
| Subprocessors | **UNKNOWN** | UNKNOWN |
| Approver | Gopal Patwa, Charter C4 (APPROVAL_RECORD-1) | same |

**Named compliance approver:** none yet. The brief wants one named human; the Charter approver is Gopal Patwa. I do not record him as approver of this review: the Release Manager asks him at the end review.

## 10. Hand off

- **Orchestrator:** no STOP. One judgement call (section 2, transport metadata under C4.1).
- **Frontend and Tech Writer:** section 6 facts, section 9 entry into `docs/runbooks/public-ask.md`.
- **Cloud Deployment (stage 17) and Security (14):** G2, G3, G4, G5 evidence.
- **Release Manager:** G1-G10; do not mark the DPA row MET; the owner's `END_REVIEW.md` sentence (G8).
- **Owner:** hashed IP, controller role, transfer basis, Anthropic retention and training use, whether public use is permitted by both sets of terms, the unread DPA text.
