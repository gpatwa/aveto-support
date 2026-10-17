# Vendor Risk Assessment — Anthropic (Claude model service, reached only through the operator's own Claude Code session)

> Owner: Compliance Reviewer (with Security & Privacy). Stage 11b, slice docs-answerability-2, depth standard, 2026-10-16.
> **Updated 2026-10-17 (slice `land-answerability`, item T3, Compliance Reviewer, standard depth)** from the owner's statement in the approved Charter C4.1 (`runs/land-answerability/CHARTER.md`, sha256 `5cb44338417a13038e29d6bf9f12320c9367f5199847ccb6680385d31cc976fb`, approved by Gopal Patwa in `runs/land-answerability/APPROVAL_RECORD-1.md`). Only the fields C4.1 states were changed; every other field is still UNKNOWN. Slice 7's original text is kept below, with updates marked "**[Updated, Charter C4.1]**".
> Status: **DPA not in place. Recorded as an owner-accepted limitation, not as MET. The owner proceeds under the adopted operating rule "public-docs questions only until a DPA is in place" (Charter C4.1). Vendor-risk fields beyond C4.1 remain UNKNOWN.** No new rule 6 approval is made by this document; records 3, 6 and 8 of slice 7 stand unchanged.
> Triggers: `docs/HUMAN_APPROVAL_RULES.md` rule 6 (new data processor; "expanding what an existing processor receives").
> Ordered by APPROVAL_RECORD-9 (C1): "record Anthropic's vendor-risk and DPA status from what we know (unknowns stated as unknown, nothing invented)."

## Update from the Charter (T3), read this first

What the owner stated, in Charter C4.1 (the words as the Charter has them): "Terms status as stated by the owner: personal subscription, no DPA in place; retention and training use per that plan's public terms, not verified by an agent. Recorded in `11b-vendor-risk.md`. Operating rule **adopted**: public-docs questions only until a DPA is in place." The Charter also records, in C8.5, "Data Governance waived".

| Field | State now | Source |
|---|---|---|
| Account type | **Personal subscription** (the plan tier by name is not stated in the Charter and is not recorded here) | Charter C4.1 |
| DPA in place | **NOT in place** | Charter C4.1 |
| Vendor retention of prompts and replies | **Per the plan's public terms, not verified.** No agent has read those terms for this record; no retention period is stated here. | Charter C4.1 |
| Use of prompts for training or improvement | **Per the plan's public terms, not verified.** No agent has read those terms for this record; no position is stated here. | Charter C4.1 |
| Operating rule "public-docs questions only until a DPA is in place" | **ADOPTED** by the owner, Gopal Patwa | Charter C4.1, APPROVAL_RECORD-1 |
| Data Governance review | **Waived.** Reason: the program stores no user data; the operator's session is covered by approval records 3 and 6 of slice 7. | Charter C8.5; intent, Done means (T10) |
| RoPA / processor-inventory entry | **None kept in any artefact. The Charter does not say one is kept.** Owner's one-line to be given if wanted (condition 5 below). | Searched the worktree for "RoPA" and "processor inventory": no entry exists; Charter silent |

**Gate status recorded for "DPA in place": NOT in place; owner proceeds under the adopted operating rule.** This is an owner-accepted limitation, not MET and not a waiver of the DPA item. The checklist (`13-release-checklist-tier3.md` section 4) said that proceeding with the fields UNKNOWN needs the owner's recorded sentence; the sentence that exists is Charter C4.1 (DPA not in place, rule adopted) approved by hash in APPROVAL_RECORD-1. The Charter does **not** contain a separate sentence in which the owner says "I accept the residual risk"; this record therefore does not claim one (see "Risk rating"). The Release Manager reads whether the Charter approval is enough for the "owner-accepted limitation" row.

What the rule does and does not do: it is a policy control on what the operator types. The repo has no redaction and no classifier (condition 3 below), so nothing technical stops a non-public question. It does not reduce what the harness attaches to every request (personal email, git user name, local username, organisation ID, git lines, environment lines): that stays as records 3, 6 and 8 name it, and is within no DPA.

## How to read this document

- **Established** means a repo artefact or an owner record says so, and the source is cited.
- **UNKNOWN — owner to state** means no artefact in this slice establishes it. I have not filled any such field from memory of Anthropic's public policies, a web search, or a guess. Where a field is UNKNOWN the owner states it, in their own words, in the driving session; a later session records it. Until then it stays UNKNOWN.
- This is not the rule 6 approval. Rule 6 approvals already exist (APPROVAL_RECORD-3 and -6, see "Existing approvals"). This document is the vendor-risk and DPA-status record that rule 6 says should accompany them, and which the Release Manager (`09-release-checklist.md`, C5c) found was never written.

## Vendor & service

- **Vendor:** Anthropic.
- **Service:** the model provider behind the operator's own Claude Code session. The judge is the Claude Code subagent `aveto-answerability-judge`, pinned to the full model ID `claude-sonnet-5-5` (APPROVAL_RECORD-2; INV-4).
- **Channel (established):** the operator's own Claude Code session, on the operator's subscription, **attended only**, typed by the operator (`/aveto-judge` has `disable-model-invocation: true`). No API key, no metered API, no `claude -p`, nothing unattended, no scheduled use, no credentials (intent, Constraints; INV-5; `09-release-checklist.md`). The program (`python -m aveto_support`) has no model client and sends nothing (INV-5; `test_program_offline_no_model`).
- **Need it serves (established):** an answerability judge, so the product prints `no confident match` instead of showing passages that do not answer the question (intent, "What I want"). Why a third party and not a local model: the intent chose a Sonnet-class judge on a measurement (slice 6 pilots: Haiku 47/56, Sonnet 5.5 51/56, Opus 49/56) and kept the program offline by running the judge in the operator's existing session. A local-model alternative was not assessed in this slice.
- **Is this a new vendor for the owner?** The intent says the session "was already sending to the same provider". Whether the owner's Anthropic account predates this slice is not in any artefact. **[Updated, Charter C4.1]** The terms it runs under are now stated by the owner: personal subscription, no DPA (see "Contractual / DPA").

## Existing approvals (what the owner has already ruled; these are not re-opened here)

| Record | Date | Owner's words (short) | What it covers |
|---|---|---|---|
| APPROVAL_RECORD-3 | 2026-10-12 | "Rule 6: Anthropic as data processor through my own session, attended only." | The processor, the channel, attended only. |
| APPROVAL_RECORD-6 | 2026-10-12 | "record 3 is reaffirmed and extended to name the session context exactly as listed in the INV-5 block ... to Anthropic only, attended only." | The session-context items named in INV-5, including the main conversation's copy of the payload and reply. |
| APPROVAL_RECORD-8 | 2026-10-13 | Rule 4 edit to INV-5's environment list | Added OS version and the git-repository/worktree flags (found sent but unnamed at the smoke, `05a-smoke.md`). This is a safety-text edit, not a rule 6 record, but it widens the named list. |
| APPROVAL_RECORD-9 | 2026-10-16 | Release tier ruled 3; asks for this record | Orders this document. Approves no processor change. |

None of these states a DPA position, a data classification, or a vendor-risk rating. That is the gap this document records.

## Data shared

What leaves the machine when the operator runs the judge step. Source for every row is the approved INV-5 text (`.agentic/SAFETY_INVARIANTS.md`), as measured in `01-measurement.md` (2026-10-12) and re-measured at the smoke (`05a-smoke.md`). The actual values of personal items are **not** recorded in any artefact, and I did not look for them; classification below is by kind of data.

| Element | Classification (my assignment; owner to confirm) | PII/PHI/PCI | Necessary? |
|---|---|---|---|
| The question | **User text.** In the slice's runs: public eval-set questions only (records 4, and the held-out and seen sets). In internal use after release: whatever the operator types, which the intent itself classes as "real user data" (Stakes box 1). | Possible PII, depending on what the operator types. None flagged in the eval sets. | Yes: the judge cannot judge without it. |
| The payload (passages `retrieve` would show, with file paths, headings, line ranges; the base-directory line the harness adds) | Public. Source is the configured docs, `gpatwa/agentic-sdlc-playbook` at a pinned commit (`docs-source.toml`), fetched by `ingest` with no credentials. User documentation only (intent Decision 2; maintainer material is excluded). | None | Yes: the passages are what is judged. Operator can inspect first with `judge-input`. |
| The judge's fixed system prompt (`answerability-judge-v1`, sha256 `24b244d2...`) | Public (in the repo). | None | Yes. |
| Project instruction files `CLAUDE.md` and `AGENTS.md`, read from the main checkout's path | Internal. Repo text about the Aveto run method; contains no credentials (Security `08` section 6 secret scan). | None found | **No.** Harness-attached; no setting that removes it was found (`01-measurement.md`; INV-5). |
| **The user's email address** | **Personal data of the owner.** | **PII (personal email)** | **No.** Harness-attached to every fork. Not reducible by this repo as far as the artefacts show. |
| Git branch, git user name, working-tree status, five recent commit subjects | Internal; the git user name is **PII (owner's name)**. Commit subjects in this slice are run-management text (for example "docs-answerability-2: owner rules release tier 3 (APPROVAL_RECORD-9)"). | Name: PII. Status and subjects: none expected, but not scanned for each future session. | **No.** Harness-attached. |
| Environment lines: working directory (contains the local username), platform, OS version, shell, scratchpad path, git-repository or worktree flag, model ID, date, **organisation ID** | Internal. Local username and organisation ID are account identifiers. | Account identifiers; not credentials | **No.** Harness-attached. |
| The main conversation's copy of the question, payload and the judge's reply | Same classes as above; the reply is model-generated text, including its reason. | As the question | Not necessary for the judge; a consequence of running the step in a session. |
| `/aveto-judge-seen` (eval-only): same kinds, for a question its key lists, plus a line naming the skill's local directory path | Eval data | None | Not to be used again until S5 is fixed (APPROVAL_RECORD-9, C3). |
| Whatever else the operator's session carries | **Unbounded by this repo.** INV-5: "whatever the operator's session carries goes with it." About 2.7k of the 14.2k measured first-request tokens were never itemised; the harness's own traffic was not measured. | Unknown | n/a |

**Minimisation:** the repo cannot remove the harness-attached items (email, git lines, instruction files, environment lines): `01-measurement.md` found no setting that does, and "whether one exists is an open question, not a finding." Removing the tool schemas (D1, record 7) reduced the first request, not the session context. What the operator can control: which question they type, and the payload, by inspecting `judge-input` first. Whether to run this step from a checkout or account that carries less (for example a different git user email) is the owner's call and is not assessed here.

**Not sent (established):** credentials, API keys (none exist), customer data (none was used in any run of this slice; every question in the stage 1, 5 and 7 runs is an eval-set question), the held-out set labels (the judge receives question and passages only; `judge-input` has no scores, URLs or labels, `test_judge_input_has_no_scores_urls_labels`).

## Subprocessor chain

- Does the vendor use its own subprocessors for our data? **UNKNOWN — owner to state.** Nothing in the artefacts lists Anthropic's subprocessors or the cloud/infrastructure providers behind the model service.
- Disclosed and auditable? **UNKNOWN — owner to state.**

## Security posture

- Certifications (SOC 2 Type II, ISO 27001, ISO 42001, other, with dates): **UNKNOWN — owner to state.** No attestation, report or certificate for Anthropic is in the repo or in any run artefact. I have not asserted any.
- Recent penetration test or audit: **UNKNOWN — owner to state.**
- Status page and uptime history: **UNKNOWN — owner to state** (no link recorded). The slice's operational record is its own: 96 judge spawns across stages 5 and 7 with 0 judge errors and 0 tool uses (`05-seen-check.md`, `07-gate-scoring.md`). That is evidence about this slice's runs, not about the vendor's uptime.

## Contractual / DPA

- **DPA in place: NOT in place. [Updated, Charter C4.1]** Owner's statement. Recorded as an owner-accepted limitation under the adopted operating rule, not as MET. The DPA item remains open as a gate: it closes only if a DPA is put in place. The Release Manager's gap (C5c, "DPA status was never stated in any artefact") is closed as to *status*; it is not closed as to *having a DPA*.
- Which Anthropic terms and plan the owner's account is under: **Personal subscription. [Updated, Charter C4.1]** The Charter does not name the plan tier, and no artefact quotes or cites the terms; whether the terms were reviewed for this slice is not recorded. Not team, not enterprise, per the owner's statement.
- **Data retention by the vendor for this account** (how long prompts and replies are kept): **per the plan's public terms, not verified. [Updated, Charter C4.1]** No agent has read those terms for this record. No period is stated here.
- **Use of this account's prompts for model training or improvement:** **per the plan's public terms, not verified. [Updated, Charter C4.1]** No agent has read those terms for this record. No position is stated here.
- **Data-handling terms acceptable: not assessable.** The two lines above point to the plan's public terms and no agent has verified them, so no judgement is made. The operating rule (public-docs questions only) is the owner's chosen control while that stays unverified.
- Liability and breach-notification SLA: **UNKNOWN — owner to state.**
- Whether the terms permit the use made here (an eval harness driving a subagent in an interactive session): **UNKNOWN — owner to state.** This is a contractual reading; I do not interpret contract clauses (escalate to the owner or legal).
- Is the owner's account a personal one or a company's? **Personal subscription. [Updated, Charter C4.1]** Reading kept from slice 7: if the data subject (the email, name) and the account holder are the same person, the personal-data exposure is the owner's own; if any other person's data were ever typed as a question, that person's data would go to Anthropic under whatever terms apply.

## Data residency

- Where is the data stored or processed: **UNKNOWN — owner to state.**
- Cross-border transfer and legal basis (SCCs, adequacy, n/a): **UNKNOWN — owner to state.** Not assessable from the artefacts. Relevant only if non-public personal data of EU/UK persons is ever typed as a question; no run in this slice did that.

## Access scope

- Least privilege honoured? **For the judge:** yes, as built and as measured: no `tools` entry, `disallowedTools` includes the seven harness tools and ends in `mcp__*`, a hook that refuses every tool call; 0 tools offered and 0 `tool_use` in all 96 stage 5 and 7 spawns plus the smoke (`09-release-checklist.md`; APPROVAL_RECORD-7). Not shown by any test: that Claude Code runs the hook, and the harness's own traffic (INV-4, INV-5, Security section 9).
- **For the session as a whole:** the operator's main conversation has the operator's own tools under their own permission prompts (INV-5). Two open Security findings bear on it: **S6** (a local permission rule in the gitignored `.claude/settings.local.json` removes the prompt for `python ... seen_payload.py ...`, so the INV-5 session exception is weaker than its words assume until the owner deletes, narrows or accepts it) and **S5** (quote breakout in `/aveto-judge-seen`; the skill is not used again, APPROVAL_RECORD-9 C3). Both are the owner's decisions and neither is actioned in any artefact I read.
- **Any model in a session here can spawn the judge** with a `model` override (S4, F12). On the operator path the "judged" label proves the prompt, not the model. Data still goes to the same provider.
- Can the owner revoke access immediately? Yes in the sense that matters for this slice: nothing runs unless the operator types `/aveto-judge`; stopping is not typing it; `git rm -r .claude/skills/aveto-judge/` disables the path (spec section 13, rollback step 2). Revoking the account-level relationship with Anthropic is outside the repo: **UNKNOWN — owner to state** if relevant.

## Exit & portability

- Data export on termination: **UNKNOWN — owner to state** (no product data is held by the vendor by design of this repo; whatever the account retains is covered by the retention line above).
- Deletion on termination and proof: **UNKNOWN — owner to state.**
- **What persists locally and is the owner's to manage (established):** Claude Code transcripts in `~/.claude/projects/` hold the full payloads and replies (INV-4 parenthesis; F7; Security section 5). No rollback removes them. `.aveto-judge/` (question and reply) is gitignored and deleted on every `judge-apply`. `diffs.md` files committed under `runs/` hold reply text for differing eval rows only (eval-set questions).

## Compliance mapping (additive to the Security review)

| Control | Where this slice touches it | Evidence | State |
|---|---|---|---|
| GDPR Art. 28 (processor terms), Art. 30 (record of processing / RoPA entry) | New third-party flow; the owner's session context includes personal data (email, name) | Records 3, 6; INV-5; this file | **Open.** There is no RoPA or processor-inventory entry in the artefacts. **[Updated, Charter C4.1]** The DPA statement now exists: no DPA, personal subscription; Data Governance waived by the Charter (C8.5). Whether Art. 28 even applies depends on whether the owner acts as a controller for anyone's data here (UNKNOWN). Not asserted either way. The operating rule limits what is typed to public-docs questions; it does not touch the harness-attached personal data. |
| GDPR Art. 5(1)(c) (minimisation), Art. 13/14 (transparency) | Harness-attached items not necessary for the judge | `01-measurement.md`; INV-5 | **Partly met:** the necessary data is inspectable; the unnecessary items cannot be removed from this repo; disclosure exists in INV-5. |
| SOC 2 CC9.2 (vendor and business-partner risk), ISO 27001 A.5.19 to A.5.22 (supplier relationships) | Anthropic as a supplier | This file | **Open.** **[Updated, Charter C4.1]** DPA: not in place (owner-accepted limitation). Retention and training: per the plan's public terms, not verified. Certifications and subprocessors: still UNKNOWN. |
| ISO 27001 A.5.34 (privacy and PII protection) | Personal email and name sent to a processor | Records 3, 6, 8 | Approved by the owner; assurance fields open. |
| EU AI Act Art. 50 (transparency), ISO 42001 | Real model is called in a rule 5 path | This slice's judge output is a verdict token that the operator reads; the user-visible output is either unchanged retrieved passages or `no confident match` plus a `Deciding signal` line naming the judge verdict. The product generates no content. | The `Deciding signal` line discloses model involvement in the decision. Whether any further Art. 50 duty (disclosure to end users, provenance marking) applies to an internal, attended, operator-facing tool with no generated content is a **legal reading I do not make**; flagged for the owner. The product is not offered to end users in this slice. |

## Risk rating (my assessment, for the owner to accept or reject)

- **Inherent risk: low to medium.**
  - Low drivers: the payload and the questions used in every run of this slice are public documentation text and public eval-set questions; no credentials, no customer data, no regulated data class (PHI/PCI) are involved; the channel is attended and operator-typed; the judge has no tools; 0 anomalies in 97 audited spawns; the program stays offline.
  - Medium drivers: a **personal email address, the owner's name, a local username, an organisation ID and git subjects ride along on every request and cannot be removed from this repo**; the session carries more than was itemised (2.7k tokens unitemised; harness traffic unmeasured); transcripts persist locally; and **internal use after release changes the question from eval text to whatever the operator types**, which the intent itself classes as real user data.
- **Residual risk after controls: low for the slice as run (eval, public text); medium-unknown for open-ended internal use until the DPA, retention and training fields above are stated.** I cannot rate the residual lower, because the controls that would lower it (a DPA, retention terms, no-training terms) are unknown, not absent.
- **[Updated, Charter C4.1] Residual risk that remains with no DPA:** (a) the vendor's retention and training handling of the owner's prompts rests on the personal plan's public terms, which no agent has verified; (b) there is no contractual breach-notification, liability or subprocessor commitment (all UNKNOWN); (c) the personal email, git user name, local username and organisation ID that ride on every request are within no DPA; (d) the operating rule is a policy control with no technical enforcement, so a non-public question typed by mistake would go to Anthropic under the personal plan's terms; (e) local transcripts persist as before. The rating above is unchanged: residual low for the slice as run (public text), medium-unknown for open-ended internal use, which the adopted rule is meant to keep out of scope.
- **Residual risk accepted by:** the owner **proceeds** under the adopted operating rule (Charter C4.1), approved by Gopal Patwa in APPROVAL_RECORD-1. What the Charter and the record support is: DPA not in place, retention and training per the plan's public terms and unverified, operating rule adopted, run to proceed. **Neither contains a sentence in which the owner states a risk rating or says in terms that the residual risk is accepted.** This file therefore records an owner-accepted *limitation* (the DPA is absent and the owner goes ahead under the rule), not a stated risk acceptance. If the owner wants a named risk acceptance, it is one sentence in the driving session and a later session records it.

## Recommended disposition (slice 7's text; status of each condition added 2026-10-17)

**Approve with conditions** (recommended in slice 7). **[Updated, Charter C4.1]** The owner did not tick a box in this file. What the Charter records against the conditions is shown on each line. Conditions:

1. **Fill the UNKNOWN fields above** with the owner's own statement. **[Updated, Charter C4.1] Partly done:** account = personal subscription; DPA = none; retention and training = per the plan's public terms, not verified. Still UNKNOWN: everything listed in "Remaining UNKNOWN" below.
2. **Keep the scope as approved:** attended only, operator-typed, the owner's own session, no API key, no `claude -p`, nothing scheduled. Any change, including a different account, a shared or company account, a second operator, unattended use, or sending anything beyond INV-5's list, is a new rule 6 decision starting from Anthropic's then-current terms (intent Decisions 5).
3. **Questions for internal use are public-docs questions only** until the DPA and retention fields are stated. Do not type a customer's text, a name, an order number or any non-public data as a question. This is the owner's operating rule to adopt; the repo has no mechanism that enforces it (no redaction, no classifier), so it is a policy control, not a technical one. **[Updated, Charter C4.1] ADOPTED** by the owner (Gopal Patwa), until a DPA is in place.
4. **Decide S6** (delete or narrow the local permission rule) and keep C3 (no `/aveto-judge-seen`) so that the permission prompts INV-5 relies on exist for the session that does the sending. **[Updated, Charter C8.5]** S6 rule deleted, as the owner said on 2026-10-16 (T9a); S5 fixed, not retired (T8). This file does not verify either; the Security re-check and the Release Gate do.
5. **Processor inventory / RoPA entry:** the repo holds none. If the owner keeps one, the entry is: Anthropic; purpose: answerability judge; data: as the Data shared table; channel: owner's attended session; basis and retention: from the owner's statement. If none is kept, say so, in one line, rather than leave it implied. **[Updated, Charter C4.1] Status: none kept in any artefact; the Charter is silent. Owner's one-line to be given if wanted.** Data Governance is waived (Charter C8.5) because the program stores no user data and the operator's session is covered by approval records 3 and 6 of slice 7.
6. **Reconsider before any wider use** (more operators, a team, announced use): a SOC 2 or ISO 27001 report request, the subprocessor list, and data-residency confirmation, because the current assessment rests on a single-operator, public-data, attended scope.

If the owner rejects the disposition, the alternative is to stop using the judge step in sessions that carry personal context (the product continues to work without it: `retrieve` is unchanged and never abstains).

## Remaining UNKNOWN (after the Charter C4.1 update)

Nothing below is filled from memory of Anthropic's public policies, a web search or a guess.

- Anthropic's subprocessors, and whether they are disclosed and auditable.
- Certifications (SOC 2 Type II, ISO 27001, ISO 42001, other, with dates); recent penetration test or audit; status page link.
- Liability and breach-notification SLA.
- Whether the plan's terms permit this use (an eval harness driving a subagent in an interactive session). A contract reading; not made here.
- The plan tier by name (the Charter says "personal subscription" only).
- The actual retention period and the actual training-use position (the Charter points to the plan's public terms; not verified).
- Data residency; cross-border transfer and legal basis.
- Export and deletion on termination, and proof; account-level revocation.
- Whether GDPR Art. 28 applies at all (depends on whether the owner acts as controller for anyone's data).
- Whether any EU AI Act Art. 50 duty applies to this internal, attended, operator-facing tool (a legal reading; flagged for the owner, not made).
- The harness's own traffic and the roughly 2.7k first-request tokens never itemised (INV-5).

## Decision

- [ ] **Approve** — proceed; recorded in the processor inventory / RoPA. **Not ticked:** no inventory entry exists.
- [ ] **Approve with conditions** — recommended in slice 7. **Not ticked.** The owner approved the Charter, which records the account status and adopts the operating rule (condition 3). That is not the same as ticking this box, and this file does not tick it for them.
- [ ] **Reject** — <reason>. Not ticked.

**Human approver (rule 6):** Records 3 and 6 of slice 7 (Gopal Patwa) cover the processor and the channel and are unchanged. Charter C4.1 (APPROVAL_RECORD-1, Gopal Patwa, 2026-10-17, time not given) states the terms status and adopts the operating rule. No new rule 6 approval is made by this update, and what Anthropic receives is unchanged.

## What this document is not

- It is not an approval of a push, merge, deploy or announcement.
- It is not a legal reading of any Anthropic term, any GDPR article's applicability, or the EU AI Act. Those are escalated to the owner or legal.
- It does not restate Anthropic's public policies. If the owner wants those assessed, they supply the current document and the terms they are under, and a later session reads them.

## Hand off

- **To the owner:** the "Remaining UNKNOWN" list; whether to give a RoPA one-line; whether to state a risk acceptance in terms.
- **To Data Governance (RoPA / inventory entry):** waived by the Charter (C8.5); the entry in condition 5 is the owner's to keep or decline.
- **To the Release Manager:** **[Updated, Charter C4.1]** T3 is recorded as: DPA in place = NOT in place; owner proceeds under the adopted operating rule; an owner-accepted limitation, **not MET**. The gate row "New subprocessor risk-assessed + DPA in place" must say that, not "MET". The Release Manager decides whether APPROVAL_RECORD-1 is enough as the owner's recorded sentence for proceeding with fields not in place or UNKNOWN; this file does not decide it. See `11c-change-request.md` and `runs/land-answerability/03-vendor-risk-note.md`.
