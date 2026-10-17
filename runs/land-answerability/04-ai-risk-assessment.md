# AI Risk Assessment — answerability judge step (`aveto-answerability-judge`, `/aveto-judge`)

> Owner: AI Governance Agent  ·  Slice: `land-answerability`, stage 4 (T10)  ·  Depth: standard  ·  Date: 2026-10-17
> Status: **pass with named gaps** (verdicts in section 9). Approves nothing, commits nothing to the product, edits no invariant or method file.
> Frameworks used: NIST AI RMF (+ GenAI Profile AI-600-1) · EU AI Act (screening only, see section 2) · ISO 42001 / ISO 42005 (feeds the Compliance Reviewer; no certification claim).
> Source model card: none. The model is a hosted third-party model (`claude-sonnet-5-5`) used through the operator's own Claude Code session. The design documents are `runs/docs-answerability-2/02-tech-spec.md` and `.agentic/SAFETY_INVARIANTS.md` INV-4 and INV-5.
> Read for this review: `intent.md`, `CHARTER.md`, `.agentic/SAFETY_INVARIANTS.md`; from slice 7 (`runs/docs-answerability-2/`) `02-tech-spec.md` (method, bars R3, INV-4/INV-5 content), `05-seen-check.md` and `07-gate-scoring.md` (figure lines only), `08-security-review.md`, `11-monitoring-plan.md`, `11b-vendor-risk.md` (Art. 50 row), `13-release-checklist-tier3.md` (sections 5, 8, 9); `runs/land-answerability/01-s5-fix.md`; test names in `tests/`.
> **Not opened, by the brief:** `evals/retrieval-heldout-5*.toml` and the `judge-check/` labels. **Not done:** no gate re-run, no judge spawn, no network. Every figure below is copied from the scorers' recorded lines, not recomputed.

## 1. Capability

- **What it does:** after `retrieve` has found the passages it would show for a question, an attended zero-tool judge (agent `aveto-answerability-judge`, pinned to `claude-sonnet-5-5`, fixed prompt `answerability-judge-v1`) is shown those passages and the question and returns a single verdict, `ANSWERABLE` or `NOT_ANSWERABLE`. The program reads only that token (from the last non-empty line) and prints either `retrieve`'s own unchanged output plus a `Deciding signal:` line, or exactly `no confident match` plus a `Deciding signal:` line. The judge never produces text that is shown; on any unusable reply the program prints `judge error` and shows nothing (INV-4 (a) to (d)).
- **Intended use:** an operator who answers docs questions types `/aveto-judge` in their own Claude Code session. The verdict decides whether the shown passages are printed or withheld. It informs one decision: "is there a documentation match worth reading for this question". It is a gate on retrieval output, not a source of answers. It is not the drafting step and carries no INV-3 check (out of scope for this run).
- **Users / subjects affected:** the operator (one named person today, Gopal Patwa per Charter C8.5). The questions are public-docs questions; the operating rule "public-docs questions only until a DPA is in place" is adopted (Charter C4.1). No end user sees the output, nobody is a subject of a decision, and no vulnerable or protected group is involved. The corpus is the configured public docs at a pinned 40-hex commit.

## 2. Risk tier

- **EU AI Act tier:** **minimal**, as a screening result for the capability as scoped, **not a legal determination**. Reasoning, using the Act's structure and not a reading of its text:
  - *Unacceptable (Art. 5 type practices):* none applies. The step does no manipulation, social scoring, biometric work or emotion inference.
  - *High-risk (Annex III type areas):* none applies. It is not used for employment, education, credit, essential services, law enforcement, migration or justice. It makes no decision about a person.
  - *Limited (transparency duties):* the open question. See "Art. 50" below.
  - The step is internal, attended, operator-facing, and produces no generated content.
- **Art. 50 (transparency) question, flagged for the owner or legal. This is not a legal reading made by me.** `11b-vendor-risk.md` (EU AI Act row) already records that the `Deciding signal` line discloses model involvement in the decision and that whether any further Art. 50 duty (disclosure, provenance marking) applies to an internal, attended tool with no generated content is a legal reading that was not made. I agree with that framing and add nothing to it as law. What I can say as governance: (a) the facts that bear on the question are stable and listed in this file (internal; attended; one operator; no generated text; model involvement disclosed on every judged output); (b) if the product is ever offered to anyone other than the operator, or begins to produce text (drafting, INV-3), the tier and this question must be re-assessed before that change ships, not after. **Open item OI-1: the owner or legal decides whether Art. 50 applies; until then the tier above is provisional.**
- **NIST AI RMF framing:**
  - *Govern:* one named owner and operator; Charter C3.1 pins the model; rule 5 and 6 approvals exist (slice 7 records 2, 3, 6, 8); INV-4 and INV-5 carry the controls; the DPA gap is recorded (`11b`) and the operating rule adopted.
  - *Map:* context is a single attended session reading a pinned public corpus. Mapped GenAI risks (AI-600-1): *confabulation* is bounded because the judge produces no shown text; *information security / prompt injection* is live through passage text and the question (S3), bounded by zero tools and the verdict-only channel; *data privacy* through the session context the harness attaches (named in INV-5, not removable from the repo); *human-AI configuration* (automation bias on `no confident match`, over-abstention 14 to 16%); *value chain / third party* (Anthropic as processor, no DPA in place).
  - *Measure:* two pre-registered bars on two sets (section 5), a per-spawn audit with void rules, and INV-4/INV-5 pinned by named tests.
  - *Manage:* attended-only use, `retrieve`-alone fallback, the adopted monitoring plan (Charter C8.5), and a tested rollback (T4, `02-rollback-rehearsal.md`).
- **Rationale for minimal rather than limited:** the capability cannot change what a person sees beyond choosing between two outputs the program composes itself; no verdict byte, reply byte or reason reaches stdout. A forged or steered verdict can at worst show what `retrieve` would show anyway (labelled judged) or abstain (`08-security-review.md` section 1, "Why a forged or steered verdict cannot hurt INV-4"). Nothing generated is shown, so the Art. 50 content duties have nothing to attach to, subject to OI-1.

No unacceptable-risk finding. Nothing to escalate on tier grounds beyond OI-1.

## 3. Obligations for this tier

At minimal tier the Act imposes none of the high-risk obligations; the rows below are the template's, applied as good practice at the level this capability warrants. "Required" means required by me for release as an internal tool, not required by law.

| Obligation | Required at this tier? | Met? | Evidence |
|------------|------------------------|------|----------|
| Transparency / disclosure to users | Yes, as practice (OI-1 open for the legal question) | **Yes** (internal operator) | Every judged output ends with `Deciding signal: answerability judge verdict <TOKEN> (prompt answerability-judge-v1, sha256 24b244d2…a159427)`; `retrieve` and `eval` without `--verdicts` never print it (`test_unjudged_outputs_never_look_judged`); INV-5 names every item the session sends; the operator can read the payload first with `judge-input`. README states the limits (Charter C8.5 T7). |
| Human oversight | Yes | **Yes, with one gap** | Attended only. `/aveto-judge` has `disable-model-invocation: true` (typed by the operator). The verdict chooses between two program-composed outputs (INV-4). Standing mitigation "stop typing `/aveto-judge`, use `retrieve` alone" adopted (Charter C8.5). Gap: `/aveto-judge-seen` is model-invocable by design, and any model in the session can spawn the judge with a `model` override (S4); the judged label proves the prompt, not the model, on the operator path. |
| Robustness / accuracy threshold | Yes | **Yes, with gaps** (section 6) | Bar 1 (abstain on unanswerable) and bar 2 (answerable, right file in top 5, not abstained), both fixed before any result (spec R3), both MET at both stages (section 5). Gaps: operator path unmeasured; bar 2 margin one question; retrieval limit 79.2%. |
| Documentation / model card | Yes | **Yes, with gaps** | No model card exists or is possible for a hosted model. Substitutes: the tech spec (registered method, frozen at `bca0e40`), INV-4/INV-5 (approved words), the prompt file pinned by hash, the inventory entry in section 7, `11b` vendor risk. Gaps: ADR 0008 is Proposed; the inventory entry did not exist before this file. |
| Logging / traceability | Yes | **Yes, by design, with a stated limit** | Per-output `Deciding signal` line; `input sha256:` on `judge-input`'s stderr; `judge error` with one fixed category on stderr and exit 4; eval path: `tools/judge_run.py` audit voids a batch on any tool use, wrong model, or payload not matching a key question. The program stores no question or reply (INV-4); `.aveto-judge/` is gitignored and deleted on every `judge-apply` path. Limit: on the operator path nothing binds the verdict to what the judge was shown or to which model produced it; the session transcript is the only record and is the session's, not the program's (`08` section 1, "Hash binding"). |

## 4. Data Governance: waived, reason recorded

Data Governance is **waived** for this slice, as ruled in Charter C8.5 (T10: "Data Governance waived, AI Governance at standard"). Reason, as the Charter and intent state it: **the program stores no user data** (it keeps only the verdict token in memory, prints only its own two outputs, deletes `.aveto-judge/` on every path, and has no network call or model client), and **the operator's session is covered by records 3 and 6 of slice 7** (rule 6 approvals for Anthropic as processor through the operator's own session; record 8 added the two missing context items, per Charter C4.1).

What the waiver does not say, so it is not read wider than it is:
- It does not say the operator's session sends nothing personal. INV-5 names the user's email, git user name and similar harness-attached context. That is covered by the approvals above, not by this waiver.
- It does not assert a DPA exists. Terms status as the owner stated it in the Charter: personal subscription, no DPA, retention and training use per the plan's public terms, not verified by an agent (C4.1, `11b-vendor-risk.md`). The operating rule "public-docs questions only until a DPA is in place" is adopted and is the mitigation.
- It does not cover committed eval material: `stage5/diffs.md` and `stage7/diffs.md` hold full reply text for differing rows (eval questions, not user data; scanned for secrets in `08` section 5).
- I record the waiver; I do not grant it. The owner granted it in the Charter.

## 5. Evidence on file (figures copied, not re-derived)

| Measure | Stage 5 (seen-set sample, 48 spawns) | Stage 7 (fifth set, scored once, 48 spawns) |
|---|---|---|
| Bar 1: unanswerable abstained | 20/20, registered at least 16: MET | 24/24 (100.0%), registered at least 20: MET |
| Bar 2: answerable, right file in top 5, not abstained | 24/28 (85.7%), registered at least 23: MET, **one question of margin** | 16/19 (84.2%), registered 80%: MET, **one question of margin** (15 would have failed) |
| Judge errors | 0 | 0 |
| Never abstain (today's `retrieve`) | not printed | bar 1 0/24, bar 2 19/19 |
| Best-score rule (`top1 < 0.67`) | bar 1 13/20, bar 2 17/28: NOT MET both | bar 1 10/24, bar 2 13/19: NOT MET both |
| Over-abstention | 4/28 (14.3%) | 3/19 (15.8%): g09, g10, g24 |
| Record valid | offered tools 0, `tool_use` 0, model `claude-sonnet-5-5` | same, no anomaly |
| **Retrieval gate on this set** | exit 0 (28/28) | **19/24 = 79.2%, under its 80% bar, exit 1.** Not a registered judge bar. End to end: **16/24** answerable questions end with the right file shown after judging (19 with the file in the top 5, minus 3 abstained) |

Bars were fixed before any result (spec R3, `bar_met`: `count * 5 >= total * 4`). The fifth set was scored once.

## 6. Eval coverage

Does the suite cover the capability's safety invariants and failure modes?

### 6.1 Covered

| Invariant clause | Covered by | Kind |
|---|---|---|
| INV-4: `retrieve` returns only verbatim passages, never abstains, never prints a verdict or `no confident match` | `test_result_invariant_enforced`, `test_retrieved_text_is_verbatim_slice_of_file`, `test_hybrid_hits_are_verbatim_passages`, `test_unjudged_outputs_never_look_judged` | unit, runs in the default suite |
| INV-4: the judge sees what `retrieve` would show; the program keeps only the token | `test_judge_input_matches_retrieve_selection`, `test_judge_input_full_text_not_excerpt`, `test_parse_verdict_table`, `test_verdict_carries_only_the_token`, `test_reason_never_leaves_parser`; security probe P1 (38 hostile replies, all fail closed) | unit + adversarial probe |
| INV-4: `judge-apply` prints exactly one of (a) to (d); every unusable reply gives `judge error`, exit 4 | `test_apply_answerable_is_retrieve_plus_signal`, `test_apply_not_answerable_exact`, `test_apply_judge_error_shows_nothing`, `test_apply_missing_verdict_file`, `test_apply_hash_mismatch`, `test_apply_after_reingest_is_refused`, `test_apply_outside_transport_dir_untouched`, `test_apply_deletion_failure_is_judge_error`, `test_apply_deletes_transport_files_every_path`; probe P3 | unit + adversarial probe |
| INV-4: judge is zero-tool, pinned model, deny list ending in `mcp__*`, hook refusing every call | `test_agent_definition`, `test_deny_hook_refuses_every_input`, `test_prompt_file_hash_pinned`; live: offered tools 0 and `tool_use` 0 on the smoke and on all 96 batch spawns, the audit voiding a batch on any tool use or other model | unit + live audit |
| INV-4: judge answers the question correctly enough | bars 1 and 2 at stage 5 and stage 7 (section 5) | pre-registered, scored |
| INV-5: program makes no network call, starts no process, calls no generative model; sends no user text | `test_program_offline_no_model`, `test_judge_modules_import_allow_list`, `test_retrieve_is_offline_with_cached_model`, the autouse network block; plus the ingest download tests listed in INV-5 for (a) and (b) | unit |
| INV-5: payload layout contains no scores, URLs, labels | `test_judge_input_layout_exact`, `test_judge_input_has_no_scores_urls_labels` | unit |
| INV-5: eval-only skill sends only for a key-listed run id, takes no caller text in its shell line (S5 fix, this run) | `test_ids_match_key`, `test_refuses_bad_ids`, `test_refuses_missing_symlink_and_binary_id_file`, `test_argv_is_refused_and_runs_nothing`, `test_shell_line_has_no_caller_text` (hostile values run under `/bin/sh` with a stub `uv`; one fixed call logged), `test_refuses_id_not_in_key`, `test_refuses_any_argument`, `test_skill_frontmatter_and_body`; `01-s5-fix.md`: 428 passed, 12 deselected, mypy and ruff clean | unit, hostile-input |

### 6.2 Gaps (named; none is closed by this file)

| # | Gap | Why it matters | Severity |
|---|---|---|---|
| **G1** | **The operator path is unmeasured.** Both bars were scored on the eval path (a fixed payload injected by the harness per run id). On `/aveto-judge` the main conversation retypes the payload into the judge prompt (spec 14.1). `judge-apply`'s input hash binds the verdict to the payload the program rebuilt, not to what the judge saw. The recorded accuracy figures describe the eval path only. The monitoring plan marks this "cannot be observed". | Every quoted figure must say "eval path". Real use may differ in either direction. | **Required disclosure** (README and status must say it; the Charter's T7 text covers the retrieval limit but not this). Not a block. |
| **G2** | **Bar 2 passes by one question at both stages** (24/28 needing 23; 16/19 needing 15). The fifth set's source-file overlap with earlier sets (D4) already flatters bar 2. | A single question's difference would have failed the bar; the margin is within sampling noise. Over-abstention (14 to 16%) is the stable number. | Advisory, carried (R-B, stated and not accepted in slice 7). Do not describe 84.2% as a precise rate. |
| **G3** | **Retrieval limit: 19/24 = 79.2% on the fifth set, under its 80% bar; 16/24 end to end.** The judge cannot repair a retrieval miss; 5 answerable questions had no right file in the top 5 (g05, g06, g18, g19, g22), and the judge said ANSWERABLE on one of them (g19), i.e. it can show a wrong file as judged in that case. | Honest capability statement is "abstains when the shown passages do not answer", not "answers questions". | Accepted and to be stated plainly by the owner (Charter C8.5, T7). Monitoring signal 11 watches it. Not a block. |
| **G4** | **The deny hook never fired.** With 0 offered tools there was no live tool call; whether Claude Code runs the hook for the judge is not shown by any test (disclosed in INV-4 and INV-5). A future harness tool would be offered unless the deny list is updated; the hook is then the only layer on the operator path (no audit there). | Layer 2 of the zero-tool control is untested live. | Advisory, disclosed. Monitoring signals 4 and 5 are zero-tolerance. |
| **G5** | **No adversarial or fairness cases in the suite.** Prompt-injection steering of the verdict through passage text (S3) was probed in the security review but the probes are not committed cases in the golden set or regression suite, and the held-out sets do not include hostile passages. Fairness over time is not applicable (no protected-group subject, docs questions only). | The one live GenAI risk (injection steering the verdict) is bounded by design but not regression-tested as an eval. | Advisory. Proposed: add a small frozen hostile-passage case set at the next eval refresh (section 6.3). |
| **G6** | **Stale test name inside INV-5's enforcement list.** INV-5 names `test_refuses_wrong_argument_count`. After the S5 fix that test no longer exists (`grep` finds the name only in `.agentic/SAFETY_INVARIANTS.md`); its job is done by `test_refuses_any_argument` and `test_argv_is_refused_and_runs_nothing`. The invariant's behaviour is covered; the cited name is dead. | A safety-control text citing a test that does not exist is a traceability defect and would fail a future "every named test exists" check (the check `08` section 7 ran). | **Required-fix, owner's call.** Charter C5.2 says no word of INV-5 changes in this run, and a safety-control text change is rule 4, so I change nothing. Options for the owner: amend the sentence in a later slice with their own words, or record in the end review that the name is superseded. The Security re-check (stage 8) should note it. |
| **G7** | **The S5 fix is proven for the program and the rendered line, not for the harness.** Whether Claude Code runs a skill's `!` line exactly as the stub does, and whether it prompts on the allowed command, is unverified offline (as `08` said of S5). | Residual only: the fix removes the interpolation, so there is nothing to break out of. | Advisory. |
| **G8** | **Eval-suite maintenance.** The fifth set is spent: it was scored once and cannot be rescored or called unseen again. The four earlier sets are seen. The suite therefore has no unseen set, and it is only frozen data plus the audit. | Any future change to model, prompt, corpus pin, ranking, harness or INV text makes the old figures unevidenced (monitoring plan section 3), and nothing is ready to test it. | Advisory now; becomes a blocker for any change listed in section 3 of the monitoring plan. |

### 6.3 Golden set and refresh

- **Golden set:** the fifth held-out set, 48 questions scored (24 unanswerable, 24 answerable of which 19 had the right file in the top 5), plus the 48-question seen-set sample (20 unanswerable, 28 answerable) drawn deterministically from the four seen sets. Frozen at the method freeze `bca0e403a69a5cda7826ea36897734bc63dc7b87`, key hash prefix recorded in the monitoring plan (signal 14). Regression for the program is the default pytest suite (428 passed, 12 deselected at `01-s5-fix.md`).
- **Mapping to invariants:** section 6.1. The held-out bars map to INV-4's "decide confidence, return only a verdict" claim; the tests map to its "no model ever produces or alters shown text" claim.
- **Refresh status:** **current for the measured configuration, not refreshable now.** There is no drift signal, and no unseen set exists to refresh against. The monitoring plan (adopted, Charter C8.5) makes any model, prompt, corpus, ranking, dependency, harness-version or invariant change a trigger for a new pre-registered check on a **new** held-out set, not a reuse of the old result.
- **Refresh cadence I propose (owner to confirm; it is a proposal, not a registered rule):** event-driven on the monitoring plan's section 3 triggers; plus a review by me whenever the owner shares a four-weekly period note (so a quiet suite is looked at, not left to rot), with a written "no refresh needed" or "refresh needed" line; and a minimum of one review every six months while the step is in use. At the next refresh: add a new unseen held-out set with its own labels, add the G5 hostile-passage cases, and retire the fifth set to the seen group.

## 7. Model inventory entry

| Field | Entry |
|---|---|
| Capability | Answerability judge step (`/aveto-judge`, `judge-input`, `judge-apply`, `eval --verdicts`) |
| Model | `claude-sonnet-5-5`, hosted, accessed only through the operator's own Claude Code session; zero tools; no API key; not called by the program |
| Prompt / version | `prompts/answerability-judge-v1.txt`, sha256 `24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427`; agent file `.claude/agents/aveto-answerability-judge.md` (D1 deny-list change applied under slice 7 record 7) |
| Method freeze | `bca0e403a69a5cda7826ea36897734bc63dc7b87`. This run changes one method-adjacent file (`.claude/skills/aveto-judge-seen/`, Charter C5.3: S5 fix) and no gate result; `/aveto-judge` and every other method file stay byte-identical |
| Provider / processor | Anthropic via the operator's personal subscription; no DPA; operating rule "public-docs questions only until a DPA is in place" adopted (Charter C4.1; `11b-vendor-risk.md`) |
| Owner / operator | Gopal Patwa (Charter C8.5, T11) |
| Risk tier | Minimal, provisional on OI-1 (section 2) |
| Status | Internal candidate; landing by pull request into `main` is the owner's act. Not an autonomous product |
| Evidence | Section 5; `05-seen-check.md`, `07-gate-scoring.md`, `08-security-review.md` |
| Last reviewed | 2026-10-17 (this review, standard depth) |
| Next review | On a monitoring-plan trigger, on receipt of a four-weekly period note, and at most six months from the last review (proposal, section 6.3) |

## 8. Post-deployment monitoring

Adopted as written by the owner (Charter C8.5, T5): `runs/docs-answerability-2/11-monitoring-plan.md`, with sections 2 and 5 copied to `docs/runbooks/answerability-judge.md` by the Tech Writer stage of this run. I have not re-derived the thresholds. For AI Governance's purposes the load-bearing signals are:

- **Behavioural drift:** judge error rate (stop at 2 in the last 10 uses); ANSWERABLE on a question the shown passages do not answer (stop at 2 in the last 20; this is the failure that matters most, because it shows a wrong file labelled judged); over-abstention on known-answerable questions (watch 4 of last 10, stop 5 of last 10, baseline 14 to 16%); retrieval hit rate on `evals/retrieval.toml` (baseline 19/24, stop below); prompt hash and pinned files unchanged.
- **Control integrity (zero tolerance):** offered tools must be 0, `tool_use` 0, model `claude-sonnet-5-5` (signals 4, 5, 7).
- **Context drift:** base-dir line form and per-spawn peak (signals 6, 9, 10) as the offline proxy for the harness changing what it attaches.
- **Fairness over time:** not applicable. The subjects are docs questions, nobody is a subject of a decision. Recorded so its absence is a decision and not an omission. Re-assess if the question mix changes (monitoring plan section 3).
- **Owner in production:** the owner reads the four-weekly note; the operator keeps the tally and applies the stop rules. There is no SRE on-call and no service. The plan itself says a quiet period proves nothing, and that signals 2 and 3 are screening rules on a small sample, not measurements. I add one thing the plan does not: the tally is the only instrument for G1 (operator-path accuracy), so the owner should treat the first months of tally as the first measurement of that path, not as confirmation of the bars.

## 9. Findings and verdict

| Finding | Severity (blocker / required-fix / advisory) |
|---|---|
| OI-1: EU AI Act Art. 50 applicability is a legal question for the owner or legal; I made no reading. Tier is provisional until then | required-fix **for the owner to note** (a recorded line, not an artefact from me); not a blocker for an internal, attended, no-generated-content release |
| G1: operator path unmeasured; figures are eval-path figures | required-fix: say so wherever the figures are quoted (README, status). Not a block |
| G6: INV-5 cites `test_refuses_wrong_argument_count`, which no longer exists | required-fix, owner's call (rule 4 text; Charter C5.2) |
| G2: bar 2 one-question margin at both stages | advisory (R-B carried) |
| G3: retrieval 79.2% / 16 of 24 end to end | accepted by Charter C8.5 (T7); must be stated plainly, as already planned |
| G4: hook never fired live | advisory, disclosed |
| G5: no hostile-passage or adversarial cases in the suite | advisory, add at next refresh |
| G7: S5 fix not shown against the live harness | advisory |
| G8: no unseen held-out set remains | advisory now; blocking for any trigger change |
| S1 to S4, S7, S8 from `08-security-review.md` (S4 matters here: any model can spawn the judge on the operator path, so the judged label proves the prompt, not the model) | advisory, carried |

### Verdicts for the release gate rows

| Gate row (`RELEASE_GATES.md`, enterprise and governance) | Verdict | Basis |
|---|---|---|
| **AI capability risk-tiered; obligations met** (AI Governance) | **MET WITH GAPS** | Tier assigned (minimal, provisional) with a named-framework rationale; each template obligation is met with evidence pointers (section 3) and the gaps are named (G1, G2, G3, G6). The previous walk (`13-release-checklist-tier3.md` section 5) said NOT MET because no assessment existed; this file is that assessment. The Art. 50 question (OI-1) is open for the owner or legal and is not decided here. |
| **Eval coverage for AI safety invariants** (AI Governance) | **MET WITH GAPS** | INV-4 and INV-5 each map to named tests and to the pre-registered bars and per-spawn audit (section 6.1). Gaps: G1, G2, G3, G4, G5, G6, G8. None is a blocker for an internal, attended release at this tier. |

Neither row is NOT MET. I recommend **pass with the gaps named and carried**, not a block, on these conditions that belong to others:

1. The owner records a line on OI-1 (Art. 50: applies, does not apply, or ask legal) before the end review is closed, or accepts the open item in words.
2. README and `CURRENT_MVP_STATUS.md` (Tech Writer stage) say that the bars were measured on the eval path only (G1), alongside the retrieval limit already planned.
3. The owner decides G6 (leave the dead test name with a note in the end review, or amend INV-5 in a later slice with their own words).

Unacceptable-risk and high-risk obligations do not arise. No escalation under the brief's block rule.

## 10. Hand off

- **To the Compliance Reviewer:** tier, rationale, obligations table and the inventory entry feed the ISO 42001 / 42005 mapping and `11b`'s Art. 50 row. The Art. 50 flag is carried as an open item, not resolved.
- **To the Release Manager:** the two rows above are MET WITH GAPS with the three conditions in section 9. Data Governance is recorded as waived under Charter C8.5 (section 4).
- **To the Tech Writer:** state G1 (eval path only) next to the retrieval limit.
- **To the Security reviewer (stage 8):** note G6 and G7 in the re-check of the S5 fix.
- **To the owner:** OI-1, G6, and the refresh cadence proposal in section 6.3.
