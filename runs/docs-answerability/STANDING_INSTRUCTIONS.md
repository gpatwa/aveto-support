# Standing owner instructions — docs-answerability

Not an approval of any rule 1-6 action. Recorded so a cold session follows it.

## SI-1 (owner, typed in the driving session, 2026-10-10T05:42:09Z)

> From now on, for any design question that has a recommended default, and that is not a rule 1–6 approval, a budget change, a credential, or a push, merge or deploy, proceed on the recommended default and list what you decided in your next digest. I’ll veto by exception. Rule 1–6 approvals, budget changes, lowering any named depth, and anything that changes a safety control’s wording still need my own typed word every time.

**How the Orchestrator applies it:** decide on the recommended default, list each such decision in the next digest ("Decided on default"), and keep a running table below. Still stop for: rules 1-6, budget/ceiling changes, lowering any named depth (Security adversarial, Release Gate not compressed), any change to safety-control wording, credentials, push/merge/deploy. A decision that a stage's own stop condition names (e.g. a failed pre-registered check, APPROVAL_RECORD-5's refusal condition) is not a design question and still stops.

## Decided on default (running list)
| # | When | Decision | Default from |
|---|------|----------|--------------|
| 1 | 2026-10-10 | Seen-set check driven from the top-level session (QA has no Agent tool; no general-purpose driver, which would lose least-privilege) | 02c section 4 / spec 5.2 |
| 2 | 2026-10-10 | Mixed-in doc facts (02d): outcome of the SubagentHandback/EndConversation wrinkle goes into the probe's criteria rather than back to the owner, unless the probe fails | 02d |
| 3 | 2026-10-10 | INV-5 cites `test_command_definition`; 3b's test was `test_skill_definition`. Renamed the test (docstring notes the skill form); approved words unchanged. Alternative (new rule 4 request to cite the skill name) not taken. | recommended default; no wording change |
