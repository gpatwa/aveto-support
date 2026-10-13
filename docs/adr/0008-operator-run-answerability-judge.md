# ADR 0008: Abstention by an operator-run Sonnet answerability judge, with the method registered before it runs

> Architecture Decision Record. Owned by the Architect. Never edited after it is accepted. A changed decision gets a new record that supersedes this one.

- **Status:** **proposed** (2026-10-12). It becomes accepted only if all of these hold: the owner approves the INV-4 and INV-5 words (rule 4, `runs/docs-answerability-2/02b-approval-packet.md`); the seen-set sample check (stage 5) meets both bars; the frozen method then meets both bars on the fifth gate set (stage 7); and slice `docs-answerability-2` passes its Release Gate. If stage 5 or stage 7 fails, this record is marked rejected with the recorded figures, as ADR 0007 was. **No result of this slice exists as this record is written.**
- **Date:** 2026-10-12
- **Slice:** `runs/docs-answerability-2/`. Full specification: `runs/docs-answerability-2/02-tech-spec.md` (section 1 is the registered method).
- **Relates to:** ADR 0007 (a local judge, rejected); ADR 0004 (retrieval stopped abstaining); ADR 0006 (default ranking `file-rrf-v1`, which the judge path uses). Slice 6 (`docs-answerability`, closed not releasable) built the same mechanism with a Haiku judge; its code came to this branch by files (commit `5eb2a8a`), its INV words and run records did not.

## Context

`retrieve` never abstains, and no score threshold over its output reaches the owner's bars on the seen sets (ADR 0007, Context: the best pooled min(Bar 1, Bar 2) was 0.650). The intent asks that, when the docs do not answer, the product says `no confident match` and shows no passages, while the program stays offline: no cloud account, no API key, no `claude -p`, nothing unattended (`intent.md`, "What I want", Constraints).

Two earlier attempts set the evidence:

- **A local non-generative judge** (ADR 0007, `cross-encoder/qnli-electra-base`) failed its pre-registered seen-set condition: pooled Bar 1 2/20 against a required 16/20. Rejected 2026-10-09.
- **An operator-run Haiku 5.5 judge** (slice 6) scored Bar 1 20/20 and Bar 2 44/56 against a threshold of 45 on the pooled seen sets, with 1 judge error. It over-abstained on answerable questions (intent, "Why, and the evidence"). That slice also had to re-register its method mid-run after seeing failures (payload retyped by a model, 141 offered tools, a verdict grammar that rejected a trailing colon; `docs/LESSONS.md` L36 to L39 as cited by the intent).

The bars are fixed (at least 80% of unanswerable abstained; at least 80% of answerable-with-right-file-in-top-5 not abstained) and are not this record's to move.

## Decision

1. **Abstention is decided by a generative judge that runs in the operator's own Claude Code session, never by the program.** The program builds the payload (`judge-input`: the question and the passages `retrieve` would show at the default ranking, full text, with path, heading and line range, and the payload's sha256) and applies a one-token verdict (`judge-apply`). It contains no model client, opens no socket and starts no process on these paths. The operator starts the step by typing `/aveto-judge <question>`; the skill cannot be invoked by a model.
2. **The judge is the product-local agent `aveto-answerability-judge`, pinned to `claude-sonnet-5-5` by full ID** (rule 5, `runs/docs-answerability-2/APPROVAL_RECORD-2.md`), with the fixed prompt `prompts/answerability-judge-v1.txt` (hash-pinned), no `tools` entry, a deny list ending in `mcp__*`, and a `PreToolUse` hook that refuses every tool call. Anthropic is the data processor through the operator's session, attended only (rule 6, APPROVAL_RECORD-3).
3. **The judge returns only a verdict.** The program reads the last non-empty line of the reply, keeps the token `ANSWERABLE` or `NOT_ANSWERABLE`, and never prints or stores the reason or earlier lines. On `ANSWERABLE` it prints `retrieve`'s output unchanged plus one deciding-signal line; on `NOT_ANSWERABLE` exactly `no confident match` and the deciding-signal line; on any unusable reply `judge error`, exit 4. The judge never produces, selects among or alters shown text. A judge error is never an abstention presented as a judgment and never a pass-through.
4. **The method is registered before any counted spawn and not changed after a result** (tech spec section 1, R1 to R8): the payload is injected by the harness through a forked skill (`/aveto-judge-seen <run id>`) and never retyped by a model, with the layout "harness base-dir line, then payload" checked by form on every spawn; the verdict grammar is the one `judge.parse_verdict` implements; the thresholds, the 48-question seen-set sample rule, the judge-error counting and the batch void and rerun rules are fixed; and the method's files are frozen by commit before the fifth gate set is handed over.
5. **Scoring stays on the product's own path.** Eval replies become tokens through the product's `judge-apply`, and the product's `eval --verdicts` scores the two bars. An eval-only tool (`tools/judge_run.py`, outside the package) derives the sample, audits the forked transcripts deterministically (any tool use, a wrong model or an unexpected offered-tool list voids the batch) and adds the diagnostics the product does not print.

## Alternatives considered

- **Haiku 5.5 again.** Cheaper per spawn. Slice 6 is evidence for the model choice only, not a reason to move a bar: on the pooled seen sets Haiku over-abstained (Bar 2 44/56, one short of the threshold) and the slice 6 pilots had Haiku at 47/56 against Sonnet 5.5 at 51/56. The intent's earlier condition, "a larger model only on a measurement", is met by that measurement. Rejected for this slice.
- **Opus 5.5.** The pilots had it at 49/56 on the same sets, below Sonnet, with Sonnet matching it on hard negatives and false premises; it costs more in the usage window. Kept as the next step only on a further measurement (intent decision 1), which would be a new rule 5 approval and a new registered check.
- **A local model** (ADR 0007, `cross-encoder/qnli-electra-base`): offline and free per question, but it failed its pre-registered condition at Bar 1 2/20. Rejected there; not reconsidered without a new candidate and a new pilot.
- **A score threshold, no model.** No threshold, margin or combination reached the bars (ADR 0007, Context). Reported in every scoring run as the "best score rule" diagnostic, not used to decide.
- **A metered API call from the program, or `claude -p`.** Would put a model client, a credential and network egress into the program and allow unattended use. Excluded by the intent's constraints.
- **All 93 seen questions for the integration check instead of a 48-question sample.** About 1.3M more by the intent's estimate; the code path was proven end to end by slice 6's 93 spawns, so what is left to test is the model, which a registered sample tests (intent decision 2).

## Consequences

- **Easier:** the program stays offline and keyless, with its network surface unchanged; a new judge model is a one-line pin plus a rule 5 approval and a registered check; the operator can inspect the exact payload before it is sent (`judge-input`), and every judged result names the prompt by id and sha256.
- **Harder: data leaves the machine through the session.** When the operator runs the step, the question, the passages, the judge's reply and the session context the harness attaches (project instruction files from the main checkout's path, the operator's email, git branch, user, status and recent commit subjects, environment lines, not claimed complete) go to the session's model provider. The program cannot narrow that; INV-5's words state it as measured (rule 4 packet).
- **Harder: the control rests partly on the harness.** The hook's live effect, what the harness attaches and its transcript format are harness behaviour, not testable in this repo. The eval audit reads harness-internal transcripts and fails closed on an unknown shape; an app update can stop it.
- **Harder: attended only.** Every judged answer costs a spawn in the operator's usage window (about 14k tokens peak per spawn as measured at stage 1), and nothing can run on a schedule. Unattended operation would be a new intent starting from Anthropic's current terms.
- **Known weak point, open for Security:** on the operator path (`/aveto-judge`), the main session passes the payload to the judge as the Agent prompt, so a model copies the payload; the hash binds the verdict to the payload the program built, not to what the judge saw. The eval path avoids this (harness injection); the operator path does not, and is not measured by stages 5 or 7.
- **The prompt is part of the safety text.** Its sha256 is pinned by tests and printed in every deciding-signal line; changing it changes INV-4's words.
- **Revisit if:** stage 5 or stage 7 misses a bar (this record is then rejected with the figures); the harness changes what a forked subagent receives or how its deny list and hooks behave; Anthropic's terms change for attended subscription use; or a measurement shows another model clearing both bars by a clear margin.
