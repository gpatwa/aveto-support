# ADR 0008: Answerability is judged by a Haiku-class subagent in the operator's own Claude Code session; the program stays offline and only applies the verdict

> Architecture Decision Record. Owned by the Architect. Never edited after it is accepted. A changed decision gets a new record that supersedes this one.

- **Status:** proposed (2026-10-09). Pending the owner's rule 4 (INV-4/INV-5 words) and rule 5 (judge in a previously deterministic path) approvals: `runs/docs-answerability/02b-approval-packet.md`. If accepted, it stays provisional on the slice's seen-set check (pooled ≥ 16/20 and ≥ 45/56) and the scored fifth set (both bars ≥ 80%). A failure there is recorded by a new ADR, not an edit.
- **Date:** 2026-10-09
- **Slice:** `runs/docs-answerability/`. Full specification: `runs/docs-answerability/02-tech-spec.md`.
- **Relates to:** **ADR 0007** (abstention by a local answerability judge; *rejected*). This record takes over the role ADR 0007 proposed, namely deciding whether to abstain. ADR 0007 is not superseded, because it was never accepted. It stays rejected and **unedited**. Also relates to ADR 0004 (retrieval stopped abstaining) and ADR 0003 (its "decide confidence" permission is kept unchanged).

## Context

`retrieve` never abstains: 0 of 93 seen questions. No score threshold or margin reaches either bar (best 13/20 and 37/56). The local cross-encoder judge of ADR 0007 failed its seen-set check (2/20). Five pilots on the seen sets, in exactly the configuration chosen here (Claude subagents on the subscription reading the shown passages, with fixed prompts written before the runs), met both bars with Opus, Sonnet and Haiku. Haiku scored 20/20 and 47/56 (intent, "Why this").

The owner ruled out a metered API, an API key, `claude -p` and any cloud account (intent decision 1, constraints). The program must stay offline (intent "Done means"; INV-5). The intent's "Done means" lines this serves: the three offline additions; the judge artefact; one word back or nothing; no path presents unjudged output as judged; the safety-control text.

## Decision

1. **The program never calls a model and never opens a socket for judging.** It gains three offline, deterministic pieces (spec 2):
   - `judge-input` prints the judge's payload for one question: the question, plus the full text of the same passages `retrieve` shows, in rank order, with no scores, URLs or labels. It writes the payload's sha256 to stderr.
   - `judge-apply` applies one reply to that same payload. It prints `retrieve`'s output unchanged plus a deciding-signal line (`ANSWERABLE`), or exactly `no confident match` plus that line (`NOT_ANSWERABLE`), or `judge error` with exit 4.
   - `eval --verdicts` reports the two bars from a verdicts file. `eval`'s exit code is unchanged.
2. **The judge runs in the operator's own Claude Code session, only when the operator types `/aveto-judge`.** That product-local command spawns the product-local subagent `aveto-answerability-judge`. The subagent has `model: haiku`, **zero tools** plus a deny-all `PreToolUse` hook, and its body is the pilots' fixed prompt verbatim. That prompt is `prompts/answerability-judge-v1.txt`, sha256 `24b244d230c465505b92fdf6c4be90be8e967897ad3d0aa8aeaf23bf5a159427`: line 104 of the playbook's pilot doc at 00d491a, both quotes removed, one trailing newline (spec 3.2).
3. **Placement:** product-local files (`prompts/`, `.claude/agents/aveto-answerability-judge.md`, `.claude/commands/aveto-judge.md`), not a pack role. The installer forces every generated role to have file tools and the opus/sonnet models, and it never deletes foreign files (spec 3.1). A command is used, not a skill, because a model may invoke a skill on its own.
4. **The verdict only chooses between two program-built outputs.** It never produces, selects, reorders or alters any text shown. The parser accepts exactly one line, `Q1 <TOKEN> [reason]`, keeps only the token, and discards the reason. Anything else fails closed. The verdict is bound to the payload's sha256, so a stale, reused or altered verdict is a judge error (spec 2.2, 4).
5. **No judge output is stored by the product.** The two transport files in `.aveto-judge/` (gitignored) are deleted on every path. Judge reasons live only in a slice's run record, for evaluation.
6. **Attended operation only.** Scheduled or unattended use is not designed and not promised.

**Data processor.** The question and the full text of the shown passages go to the model provider of the operator's Claude Code session: Anthropic, which receives them both in the main session and in the judge subagent. This processor was approved under rule 6 in `runs/docs-answerability/APPROVAL_RECORD-2.md`. The operator's session keeps its own transcript, and the provider's retention follows its terms. Neither is controlled by the product, and the new INV-5 words say so.

## Alternatives considered

- **ADR 0007, a local cross-encoder in `retrieve`.** It kept the program self-contained, but it failed its seen-set check (2/20). Rejected by the owner.
- **A score threshold or margin rule.** Deterministic and free, but its best result (13/20 and 37/56) reaches neither bar.
- **The model called from the program** (Anthropic SDK, metered API, `claude -p`). This would make the judge automatic. It breaks the program's offline guarantee, needs a credential and a per-token bill, and the owner ruled all of these out.
- **A new pack role for the judge.** The installer forces `tools: Read, Write, Edit, Grep, Glob` and opus/sonnet, so a zero-tool Haiku judge cannot be a generated role.
- **A skill instead of a command.** A model may invoke a skill on its own, which would let the step run without the operator asking.
- **Give the judge one Read tool, as in the pilots.** That Read only carried a batch file. With it, an instruction planted in a passage could read local files. Zero tools costs the session having to paste the payload, and the seen-set check measures that path end to end.
- **A larger model first.** Opus and Sonnet passed too, but the cheapest tier did as well (intent decision 2). A larger tier would need a measurement and a new decision.

## Consequences

- **Easier:** abstention exists without a credential, a bill or a network call in the program. A future draft checker (INV-3) can reuse the same contract: payload, one-token verdict, hash binding, fail-closed parser.
- **Harder, and stated:**
  - The program cannot make a session apply the judge, cannot verify that the session spawned the judge rather than writing a reply itself, and cannot verify which prompt or model was used. The deciding-signal line states the contract; it is not a proof. These are residuals, measured by the seen-set tool-use audit and attacked by Security, not claimed away.
  - The session pastes the payload, and a model could truncate it.
  - The judge reads more than the user sees (full passages, not excerpts).
  - Abstention is available only to an operator in an interactive session. `retrieve` itself still never abstains.
  - Each use draws on the operator's subscription usage window.
- **Safety controls changed:** INV-4 gains the judge permission and its limits. INV-5 is scoped to the program's own egress and gains the judge-step sentence. The exact words, and the owner's approval of them, are in the approval packet and its record.
- **Revisit if:**
  - the seen-set check or the scored fifth set misses a bar (a new ADR records it);
  - what the `haiku` alias resolves to changes;
  - the zero-tool form cannot be enforced (open item 8.1);
  - the prompt has to change (that is a new prompt file, a new pilot and a new rule 5 request);
  - unattended use is wanted (a new intent that starts from Anthropic's current terms).
- **Rollback:** spec 7.3. Revert 3b, then 3a, and delete any local `.aveto-judge/`. Restoring the old INV words is a rule 4 request. This record is not edited; a new ADR records the reversal.
