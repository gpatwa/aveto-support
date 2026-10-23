# AI Risk Assessment: the answerability judge, now unattended for the public

> Owner: AI Governance Agent · Slice `public-ask-the-docs`, stage 6 · Depth: standard · Date: 2026-10-21
> Builds on `runs/land-answerability/04-ai-risk-assessment.md` (the attended assessment, "prior"); not redone. Design-stage review: no code, page or infra exists yet, so "plan meets" means the spec, not a test result.
> Read: `intent.md`, `CHARTER.md` (C3, C4, C5, C8.1, C8.5), `05-tech-spec.md`, the prior assessment, `STATE.md` setup log. **Not read (so claims about them are unconfirmed):** `00-slice-plan.md`, `02-prd.md`, `03-feature-spec.md`, `04-ux-spec.md` (page copy), `docs/adr/0009`, `.agentic/SAFETY_INVARIANTS.md` (known only through the spec's quotes), the Anthropic DPA, the gate file (C6.7: contents unread until stage 18). No web, no network, no gate run.
> Frameworks: NIST AI RMF + AI-600-1, EU AI Act (screening only, no legal reading), ISO 42001/42005 (feeds Compliance).

## 1. What changed from the attended assessment

| Prior basis for "minimal" | Now | Effect |
|---|---|---|
| Internal, one named operator | Anyone on the internet | Exposure and adversary class up; severity of one wrong verdict unchanged |
| Attended: operator reads each output, can stop | Unattended: nobody reads a verdict; oversight is limits, kill switch, owner's after-the-fact review | Human oversight weaker, replaced by controls (section 3) |
| Questions: operator's own, "public-docs only" rule | Questions: attacker-controlled free text, up to 500 chars, may hold personal data | Direct injection path via the question (prior risk was mainly passage text); the "public-docs only" rule cannot bind visitors |
| Session context sent (INV-5 list) | API call: prompt + question + passages only, no harness context | Less data sent. **But the judge differs from the one measured** (prior G1, now sharper: section 4) |
| Processor: Anthropic via personal subscription, operator's data | Processor: Anthropic API for visitors' data; DPA by reference, text unread by any agent (C4.1) | Data Governance waiver does not carry over (section 3) |
| Cost: none metered | Metered, $10/month, counters in memory | New risk class: denial of wallet, and availability loss when the console limit trips |
| Output unchanged | Output unchanged: verbatim passages or fixed text, no generated text (INV-4) | The main severity bound still holds |

## 2. Risk tier

- **EU AI Act: limited (transparency-relevant), provisional. Raised from minimal.** Screening result, **not a legal determination.** Reasoning from the Act's structure, not its text:
  - Unacceptable (Art. 5 type): none applies. No manipulation, scoring, biometrics or emotion inference.
  - High-risk (Annex III type areas): none applies. Public docs lookup; no decision about a person; no employment, credit, education, essential-service or justice use.
  - Limited: the hook is Art. 50 type duty to tell natural persons they are dealing with an AI system. The prior tier rested on "internal, attended, operator-facing"; all three are now false. Whether a page where a model decides which retrieved passages a visitor sees counts as an "AI system intended to interact directly with natural persons" is **a legal question for the owner/legal, OI-1 (carried, now live).** I tier conservatively and require the disclosure either way (section 6). Art. 50 content-marking duties have nothing to attach to: no generated text is shown.
- **NIST AI RMF.** Govern: Charter C3/C4/C5 pin model, processors, safety text; owner is sole operator, no on-call. Map: GenAI risks per AI-600-1: *information security / injection* (live, section 5); *data privacy* (visitor text to Anthropic); *confabulation* bounded (nothing generated is shown); *value chain* (Anthropic, Azure; DPA unread); *human-AI configuration* (automation bias on "no confident match" with 14 to 16% over-abstention in prior figures). Measure: pre-registered gate (section 5) plus offline tests. Manage: limits, kill switch, rollback, monitoring (section 7).
- **Why not higher:** the worst a fooled judge does is show passages `retrieve` would show anyway (wrongly labelled as judged) or abstain. It cannot alter text, call a tool or post to GitHub (INV-1, INV-2, INV-4; no `tools` in the request, spec 2.2). Harm is low; likelihood of attempts is now high.
- No unacceptable-risk finding. No escalation on tier grounds beyond OI-1.

## 3. Obligations for this tier, and whether the plan meets each

| Obligation | Verdict | Basis and gap |
|---|---|---|
| Transparency to visitors | **MET WITH GAPS** | Plan: page says "verbatim passages from Aveto's docs; a model decides only whether they answer" and "questions are not stored" (intent, Done means). Gaps: **T1** "not stored" is true of this service only; the question *is sent to Anthropic*, whose retention/training terms no agent verified (C4.1). Page copy must name the recipient and must not imply nothing leaves. **T2** "a model" should read as an AI model, ideally named (Claude, Anthropic). **T3** page should tell visitors not to enter personal or confidential data (replaces the prior "public-docs only" operating rule, which they cannot follow unprompted). Page copy unread by me (`04-ux-spec.md` not in scope): *unconfirmed whether T1 to T3 are already there.* |
| Human oversight | **MET WITH GAPS** | Replaced, not kept: kill switch (default on, fail closed), per-visitor and daily limits, 500-char refusal, owner end review. Gaps: **O1** no per-verdict human; none feasible at this volume. **O2** oversight is pull-only: no alert resource is in C8.3, so nobody is told when it misbehaves; the owner must look. **O3** kill switch = new revision, "tens of seconds" (spec 4, unconfirmed), not instant. **O4** hourly and daily counters reset when the replica scales to zero (spec 3.4); the month cap then rests on the Anthropic console limit, which is the owner's unverifiable statement (C6.6). If it trips, the service answers `judge error` to everyone: safe, but an availability failure. |
| Robustness / accuracy | **MET WITH GAPS** | No evidence yet on this path. Prior bars (24/24 and 84 to 100%) were measured with the harness context the API call drops (spec 2.2, risk 5), so **they do not transfer**; the 20-question gate is the first measurement of this judge. Section 5. |
| Documentation / inventory | **MET WITH GAPS** | Inventory entry in section 8. Gaps: **D1** whether `claude-sonnet-5-5` is a dated snapshot or a moving alias is unconfirmed (looked: spec 2.2, 2.4; SDK source only as the spec reports it). If an alias, behaviour can change with no change in our repo. **D2** ADR 0009 is proposed, not accepted (unread by me). |
| Logging / traceability | **MET WITH GAPS** | By design only a hashed IP, time and outcome code are kept, 7 days (C4.2). That is the right privacy trade. Gaps: **L1** the `judge_error` cause (timeout, refusal, 4xx, cap reached) is discarded, so an outage, a revoked key and a tripped billing cap look identical (spec 2.3). **L2** 7-day retention means a review slower than every 5 days loses data. |
| Data governance | **NOT MET as waived before; needs a recorded line** | The prior waiver rested on "program stores no user data" and the operator's own session. Neither holds: visitors' text goes to Anthropic. Processor approval is the owner's (Charter C4); I do not grant or imply it. Gap for Compliance/owner: DPA text unread; retention and training use unverified. Legal, for the owner: is a hashed IP (salted per process, 7 days) personal data needing a notice; controller role; US transfers (Azure eastus2, Anthropic). Not decided here. |

## 4. Judge quality on the public path (carries prior G1, G2, G3)

- **Different judge.** Attended judge: harness context, zero tools. API judge: same prompt, no harness context, `effort: high` sent explicitly, `max_tokens` 1024. The prior 24/24 and 16/19 are not evidence for it. State "eval path, attended" wherever they are quoted.
- **Retrieval caps the answerable bar.** Prior retrieval hit rate was 79.2% (19/24) and 16/24 end to end after abstentions. The judge cannot repair a retrieval miss.
- **Arithmetic on the registered bar (mine, binomial, unchecked by any tool).** If the 10 answerable behave like prior end-to-end (about 0.67 right), P(8 or more of 10) is about 0.31. If like the judge alone (about 0.84), about 0.79. So a miss of the answerable bar is **likely (roughly 20 to 70%) even with nothing wrong**. C8.1 turns a miss into kill switch on and a reported miss. That is the designed outcome, not a defect, but the owner should expect it and read a miss as "retrieval plus over-abstention", not as a judge failure, before deciding.

## 5. Eval obligations: does the pre-registered gate cover the risks?

Gate: 20 new questions, held outside the repo, 10 answerable / 6 unanswerable / 4 hostile; bars: all 10 non-answerable and hostile with no passage shown; at least 8 of 10 answerable right. Scored once, through the deployed service and real limits, in batches of at most 10 (C8.5). I have not read the questions.

| Risk | Covered by the gate? | Note |
|---|---|---|
| Judge says ANSWERABLE when passages don't answer | Yes, 6 questions, bar 10/10 | Small n; prior 24/24 was on 24 |
| Injection through the question steering the verdict | **Thinly**: 1 question of the 4 hostile | n=1 per category is a smoke test, not a rate |
| Off-topic, generated-text request, "reveal your instructions" | One each, per the intent | Bar counts "no passage shown". A correct ANSWERABLE on a nearby real topic would count as a miss; fine, the bar is fail-closed |
| Verdict forged by echo (model repeats attacker text as last line) | Not directly | Parser (last line, token only, block id) covered by unit tests, probes P1/P3 in the prior security review; not a live case |
| Injection through passage text | No | Corpus pinned; prior probes were not committed as cases (prior G5) |
| Oversized, control-char, marker, unicode input | Offline tests only (spec 10); no model | Adequate: these never reach the model |
| Cost exhaustion, rate-limit bypass, forged X-Forwarded-For | Not an accuracy eval; stage 17 check and Security stage 14 | Fine |
| Non-English or very short questions | No | Advisory: embedding/judge behaviour unmeasured; accessibility of the service to non-English visitors unconfirmed |
| Accuracy drift after launch | No | The gate is a one-time check |

- **Verdict: coverage MET WITH GAPS.** Sufficient to decide "keep running or switch off", not to certify robustness against adaptive attack.
- **Required additions, none costly:** (E1) Security's stage 14 hostile probes that reach the live judge should be saved as a frozen regression set (about $0.008 each); (E2) after stage 18 the gate set joins the seen group and is reused as the canary below; (E3) record, with the result, the exact batch order, counts and any void.
- **Suite health (prior G8 repeats):** after scoring, no unseen set remains. Refresh triggers: model ID or deprecation notice from Anthropic; price or API change that alters behaviour; prompt, ranking, corpus-pin or SDK major change; a change to the `effort` or `max_tokens` fields; any monitoring threshold tripped. Each needs a new pre-registered set, not a rescore. Also a review by me at each owner period note and at least every 6 months.

## 6. Transparency to visitors, and legal items

- Page must (release condition **R1**): say an AI model decides; say the question is sent to Anthropic, named; say not to enter personal data; say what is kept (hashed IP and outcome, 7 days) and what is not; link the corpus commit; offer the issue link on "no confident match". Over-abstention (about 15% prior) is real: "The docs don't answer this" must not read as "Aveto has no answer"; the UX copy appears to handle it (not read).
- **For owner/legal, not decided by me:** OI-1 Art. 50 applicability; privacy notice duties and legal basis under GDPR or similar; whether the hashed-IP log is personal data; international transfer terms; whether anything in Anthropic's terms restricts a public-facing use.

## 7. Monitoring the live service (owner acts; there is no on-call)

Data: abuse lines in Log Analytics (7 days) and `GET /health` counters (per replica). No question text, so correctness cannot be observed directly; all rates below are screening rules on small samples, as in the prior plan. Review at least every 5 days while it is live and weekly after a quiet month, and the first 3 days daily.

| Signal | Threshold | Action |
|---|---|---|
| `judge_error` share of admitted calls | over 5% in 50 calls, or 3 in a row | Check Anthropic status, console cap and key; kill switch on if unexplained |
| Input/output tokens per judged question (`/health` deltas) | over 2x the recorded stage 18 figure | Prompt or model change suspected; kill switch on; re-run canary |
| `answer` share of admitted calls | moves more than 20 points from the stage 18 baseline over 100+ calls | Run the canary; review |
| `paused` days | more than 2 in a week | Demand or abuse; owner decides on cap, not an agent |
| `rate_limited` concentrated on one ip hash | any day above 30 | Abuse; kill switch if cost rising |
| Console spend vs Azure bill vs estimate | any month over $10 or Azure over $10 | Stop and report; this is the C2/C6.6 backstop check |
| Canary (6 cases from the spent gate set: 3 answerable, 3 not), run by the owner or operator through the page | monthly, after any trigger in section 5, and on any model notice; any not-answerable case shown = switch off | New pre-registered check before re-enable |
| Control integrity (zero tolerance) | request has `tools`, model not `claude-sonnet-5-5`, prompt hash mismatch (service refuses to start), any text differing from `retrieve` | Kill switch on |

- Gaps to feed forward: **M1** push alerting is outside C8.3, so detection depends on someone looking; the owner should accept that in words at the end review. **M2** add a fixed `judge_error` category to an ops line (L1); that changes the logging contract, so it is for the Architect and Security, not me. **M3** stage 18 should compare live passages with local `retrieve` byte for byte on a sample.
- Fairness over time: not applicable (no person is a subject of a decision). Recorded so the absence is a decision. Re-assess if the service ever takes non-docs questions.

## 8. Model inventory entry (update)

| Field | Entry |
|---|---|
| Capability | Public answerability judge in `aveto_service` (`POST /ask`), plus the unchanged attended `/aveto-judge` path |
| Model | `claude-sonnet-5-5` via the Anthropic Messages API, effort high sent explicitly, no tools, `max_tokens` 1024, up to 2 attempts. Snapshot vs alias unconfirmed (D1) |
| Prompt | `prompts/answerability-judge-v1.txt`, sha256 `24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427` (checked at startup, per spec) |
| Processor | Anthropic (Commercial Terms, DPA by reference, text unread); Microsoft Azure (owner's subscription) |
| Tier | Limited, provisional on OI-1 (was minimal) |
| Owner | Gopal Patwa |
| Evidence | Prior attended bars (do not transfer); this slice's gate at stage 18 (pending) |
| Status | Designed; not built or deployed |
| Next review | After stage 18, then monthly canary, on any section 5 trigger, and at most 6 months |

## 9. Findings and verdict

- **No block at the design stage.** Tier is limited and provisional; nothing is unacceptable or high-risk.
- **Release conditions (each becomes a Release Gate block if unmet):** **R1** page copy meets section 6 (T1 to T3), checked by the Release Manager against the built page. **R2** the owner records a line on OI-1 and the section 6 legal items, or accepts them open in words. **R3** Security rules at stage 14 on the counters-reset gap (O4) and the forwarded-address assumption; the owner accepts or rejects at end review.
- **Accepted by Charter, to be reported honestly:** the service is public (unlisted URL, no aveto.dev link yet) with kill switch off from step 5 until the gate finishes, so the API-path judge is briefly in public use before it is measured (C8.1, C8.5). Mitigation within the Charter: order the gate hostile and unanswerable first if the file allows; do not link from aveto.dev until the bars are met.
- **Gate rows:** AI capability risk-tiered, obligations met: **MET WITH GAPS** (T1 to T3, O1 to O4, D1, L1, data governance line). Eval coverage for AI safety invariants: **MET WITH GAPS** (E1 to E3; thin injection coverage; no unseen set after stage 18).
- Prior items carried: G6 (INV-5 dead test name) is a Charter C5.2 matter for the owner; unchanged here.

## 10. Hand off

- **Compliance Reviewer (stage 7):** tier, inventory entry, the data governance line (section 3), OI-1 and the section 6 legal list for ISO 42001/42005 and the processor rows.
- **Backend/Frontend/Tech Writer:** T1 to T3 page wording; M2 for the Architect and Security.
- **Security (stage 14):** save live hostile probes as the E1 regression set; rule on O4.
- **QA Evidence (stage 18):** E3, M3, and the baseline figures section 7 needs.
- **Release Manager:** conditions R1 to R3.
- **Owner:** OI-1, legal items, O2/M1 acceptance, price and snapshot confirmation, and that a missed answerable bar is likely and mostly retrieval.
