# Intent: Know when the docs don't answer — a judge step in the operator's own Claude Code session

> **Confirmed 2026-10-09.** Drafted by Claude in the playbook session from
> slice 5's close-out and five pilots
> (`docs/pilots/2026-10-llm-answerability-pilot.md` in the playbook). The owner
> chose, in the support session, to run the judge **on the operator's Claude Code
> subscription and nowhere else** ("only S"), and to show the sources for
> false-premise questions; on reviewing the draft the owner said "commit it". The
> recommended decisions below stand as written and the owner can still overturn any
> before the slice starts. **This commit is not an approval of anything:** rule 4,
> rule 5 and rule 6 are taken from the owner in the Orchestrator's session, in
> the owner's own words. Start from a fresh worktree off `main`.

## What I want

`retrieve` and `eval` unchanged and offline, plus a **judge step** that an
operator runs in their own Claude Code session: it takes what `retrieve` would
show for a question, asks a small subagent whether those passages answer the
question, and — if not — the product prints exactly `no confident match` and no
passages. The judge is a subagent on the operator's subscription. There is no
cloud account, no API key, no per-token bill and no new service. The product's own
program never calls a model.

This is the first half of the check step. The second half (INV-3, a draft is
checked against its sources) still waits for a drafter, but the judge step is a
contract a draft checker can reuse.

## Why this, and the evidence

- The default path never abstains (0 of 93 seen questions). No score threshold
  or margin rule reaches either bar (best 13/20 and 37/56). A small local
  classifier did not either (2/20; its cause is not established).
- Pilots on the seen sets, research only, fixed prompts written before the runs,
  **in exactly this configuration** (Claude subagents on the subscription reading
  the shown passages): Opus, Sonnet and Haiku all met both bars on the 93 seen
  questions (unanswerable flagged 20/20; answerable not abstained 49, 51 and 47
  of 56), on 24 hard negatives next to documented topics (24/24 each), and on 24
  false-premise questions on the strict reading (20, 22, 22 of 24) with no decoy
  answers. The cheapest tier did as well as the strongest.
- What the pilots did **not** show: the fifth set's hardest questions (still
  unspent), or how the judge behaves when a session, not a batch file, drives it.
  The same model family wrote the questions and judged them. Differences from the
  pilots: the pilots batched 12–16 questions per agent from a file; the judge step
  gives a subagent one question's blocks directly. The seen-set integration check
  below tests that difference before anything is frozen.

## What this deliberately is not

- **Not a service.** It runs when an operator runs it, inside a Claude Code
  session, and stops when the session or the plan's usage window does. Scheduled
  or unattended use is **not designed and not promised**: Anthropic's official
  terms on unattended subscription use were not found, and the owner's standing
  rule is no `claude -p` and no metered API. Any move to unattended operation is
  a new intent that starts by reading Anthropic's current terms.
- **Not a replacement for the human.** Every reply still needs a person's
  approval (INV-1); the judge only decides whether to show sources or say
  `no confident match`.
- **Not enforced by the program.** The program cannot make a session apply the
  judge. The contract below says what a conforming session does and the tests
  and evals check the pieces that code can check.

## Owner decisions

Answered by the owner (support session, 2026-10-09):
1. **Subscription only** — no Azure, no API key, no metered billing, no spend cap
   number needed. The plan's usage window is the limit, and the slice's own
   budget is measured with `usage.mjs`.
2. **False premises: show the sources.** A premise-correcting verdict counts as
   answerable. The strict reading is reported as a diagnostic.

For the owner to confirm at the approvals (recommended answers given):
3. **The data processor is Anthropic, through the operator's own Claude Code
   session** — the same path the builds already use. *Recommended: accept.*
   Rule 6.
4. **Attended operation only for this slice.** *Recommended: yes.*

## Done means

- [ ] Starts from `main` (slice 5 merged, pack v17 or later). Retrieval, ranking,
      corpus and the embedding model are unchanged.
- [ ] **The program stays offline.** `retrieve` and `eval` make no network call and
      call no model; INV-5 is unchanged. A test asserts it.
- [ ] **Three offline, deterministic additions to the program, each tested:**
      (1) an output mode that prints the judge's input exactly as the pilots'
      blocks were built — the question, the five files, the full text of their
      shown passages, no scores, no labels; (2) a command that applies a verdict
      and prints either today's output or exactly `no confident match` with no
      passages (exit 0) and names the deciding signal; (3) `eval` scoring the two
      bars from a verdicts file, with the retrieval gate's exit code unchanged.
- [ ] **The judge step is written down as a contract and as an artefact:** the fixed
      judge prompt (committed, with its sha256), a subagent definition pinned to the
      cheapest tier that passed the pilots (Haiku-class), with no tools beyond what
      it provably needs, and a command or skill that runs `retrieve`, passes the
      blocks to the judge, reads back exactly one verdict and applies it. The
      Architect decides where it lives (a new pack role, a product-local agent, or
      a skill) knowing the installer rewrites the pack's generated agents.
- [ ] **One word back, or nothing.** Anything other than exactly one of the two
      verdict tokens is a judge error; the step prints `judge error` and shows
      nothing as judged. Any reasoning text the model adds is neither shown nor
      stored. Passages are untrusted data: the prompt and the parser must hold when a
      passage tells the judge what to answer.
- [ ] **No path presents unjudged output as judged.** The judge off, absent or
      failing never produces a result that looks like a judged one.
- [ ] **Seen-set integration check before the freeze,** pre-registered: running
      the judge step end to end on the four seen sets through the product's own
      block output, the pooled result must be at least 16/20 on unanswerable and
      45/56 on answerable-with-hit. Failing it stops the slice before the fifth set
      is touched and goes to the owner with the numbers.
- [ ] **Freeze first.** The method's commit is recorded; then the fifth set is
      committed (24 answerable, 24 unanswerable of which 18 are hard negatives,
      plus a surplus held for replacements), its labels reviewed by a fresh QA
      spawn, the unanswerable ones attacked hardest (it tries to find an answer);
      a different fresh QA spawn scores it once, by running the judge step in
      fresh subagents per batch under the pilots' tool-use audit (any tool use
      beyond the allowed reads voids the batch; rerun once; both reported).
- [ ] **Two bars, fixed now, never moved after a result:** (1) abstain correctly
      on at least 80% of unanswerable questions (20 of 24); (2) do not abstain on
      at least 80% of answerable questions whose right file retrieval put in the
      top five. Both must pass.
- [ ] **Reported in the same run:** never-abstain (today) and the best score rule on
      the same set; the end-to-end figure; the verdicts that differ from the key,
      with the judge's reasons held in the run record only; the usage the scoring
      run took, from `usage.mjs`.
- [ ] **Safety-control text, exact words approved by the owner** (rule 4), written
      by the Architect: INV-4 gains a statement that a model may judge whether the
      shown passages answer the question by returning only a verdict, and that the
      judge never produces, selects or alters the text shown. INV-5's sentence "No
      question, passage or user text ever leaves the machine" is scoped to be true
      of the program (it makes no network call) and a new sentence says what
      happens when the operator runs the judge step: the question and the shown
      passages go to the model provider of the operator's Claude Code session, and
      nowhere else. Approved before any code or artefact that sends data exists.
- [ ] **Security Review at adversarial depth** (prompt injection through passages,
      the judge's tools, the verdict parser, what the payload contains, fail-closed,
      that the program still never networks) and the **Release Gate**, tier 2. The
      verdict can be "internally releasable, not announced" only if both bars pass;
      otherwise "not releasable". A depth below adversarial needs the owner's
      recorded word.
- [ ] README and `.agentic/CURRENT_MVP_STATUS.md` state the figure the scorer
      recorded and nothing stronger, only after the verdict.
- [ ] Everything earlier slices guaranteed still holds: deterministic ingest,
      provenance on every passage, no generative output shown as the answer, no
      network outside ingest, every model file hash-checked.

## Must not break

- Nothing retrieved is presented as an answer.
- The user can always see where every passage came from.
- **The program never sends the question or the docs anywhere.** The only thing
  that does is the operator's own session, when the operator runs the judge step,
  to the provider they already use, with the payload inspectable first.
- Abstaining is never worse than showing a wrong file.

## Constraints

- Python 3.12, uv, the existing structure. No new runtime dependency.
- **No metered API, no API key and no `claude -p`** anywhere. The judge runs only
  as a subagent in an interactive Claude Code session. No agent handles a credential
  because there is none.
- Held-out rules (`project-packs/ai-agent-product.md`): the builder does not write
  the set; freeze, then commit the set, then run once; labels reviewed before the
  set is committed; the bars never move. Pilot-first (v16) is satisfied by the
  pilots; the seen-set integration check is its pre-registered continuation.
- One fresh agent per stage; review stages estimated with a tight read list.
- No Azure and no CI in this slice. The Azure pilot runner in the playbook is
  unused by this intent.

## Out of scope

- Drafting replies, the INV-3 draft checker, classification.
- Any model other than the one judge; any change to retrieval.
- Posting anywhere. Unattended or scheduled operation. Any credential.
- The `docs-retrieval-ci` workflow (precondition recorded: any exit 134 fails the
  build, no retry wrapper).

## Stakes

- [x] Touches real user data (the question is user text; it goes to the operator's
      model provider when the judge step runs)
- [ ] Moves money, or changes billing (no metered spend; the plan's usage window)
- [ ] Irreversible — deletes, sends, or deploys to live users
- [x] Changes auth, permissions, or a safety control (INV-4, INV-5)
- [ ] Adds a screen or UI a user will see
- [ ] None of the above

## Decisions (recommended; the owner can overturn any)

1. **Attended, on the operator's subscription, off unless the operator runs it.**
2. **The cheapest tier that passed the pilots first** (Haiku-class); a larger one
   only on a measurement.
3. **A label, nothing else.** The judge's words are never shown to users.
4. **Fail closed** on every error.
5. **Budget.** Plan about 700k, split at the freeze: slice A (Scope, Architecture
   with the exact INV wording and the contract, Implementation, the seen-set check,
   freeze) about 300k; slice B (label review, scoring by fresh judge subagents,
   Security at adversarial depth, the Release Gate as three spawns, close-out)
   about 400k. The Orchestrator proposes a ceiling at plan confirmation, about
   1.5× the plan because the plan has an adversarial Security Review (about 1.05M),
   and the owner types it once (pack v16). A stop is only for spend above it, a
   failed pre-registered check, or a gate that would be compressed.
6. **The fifth set stays unspent until the method is frozen,** and is used once.
7. **If the owner later wants unattended operation,** that is a new intent that
   starts with Anthropic's current terms and a decision on a processor and a cap.
