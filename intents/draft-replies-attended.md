# Intent: Draft a grounded reply, checked by a different model, in the operator's own session

> **Draft, not confirmed.** Drafted 2026-10-17 by Claude in the playbook session.
> A run under Process v2: the owner approves one Charter at the start and reviews
> the result at the end. Nothing here is an approval. This is **step 1 of the
> support agent**; running by itself on a server (a runtime model client, GitHub
> intake, an Azure deploy) is a later, separate intent. The reasons for staging it
> are under "Why this step".

## What I want

Given a question and the docs passages `retrieve` finds, the operator runs a
**draft step** in their own Claude Code session: one subagent drafts a reply
that uses only the shown passages and names them; a **different model**
checks every claim in the draft against those passages; a claim the passages do
not support is removed, or the question is escalated to a person. The program
prints the draft with its sources and the words **not posted**. The operator
reads it and, if they choose, posts it themselves. **Nothing in this step posts
anywhere.**

## Why this step, and not the whole agent

- It is the part of the product that is both new and risky (INV-2 and INV-3),
  and it can be built and gated on the owner's subscription, with no API key,
  no server and no Azure.
- It uses what already passed a gate: `retrieve` plus the judge step decide
  whether the docs answer; only then is a draft written. A question the judge
  says is unanswered gets `no confident match`, never a draft.
- Everything after it (a runtime client, issue intake, a deploy) needs decisions
  the owner has not made: an API key and its spend cap, a data-processing
  agreement, Azure. Those wait for this step's evidence.

## Who it's for

The operator who answers questions about Aveto on GitHub and wants a fast,
grounded first draft they can trust enough to read quickly, and a clear signal
when the docs do not support an answer.

## Done means

- [ ] Starts from `main` (judge step merged, pack v24). Retrieval, ranking, the
      judge and the corpus are unchanged.
- [ ] **The program stays offline.** `draft-input` and `draft-apply` (names for the
      Architect to confirm) make no network call and call no model; a test says so.
- [ ] **Two agents, two models, no tools.** Drafter `claude-sonnet-5-5`; checker
      `claude-opus-5-5`; each a product-local subagent with a deny list covering
      every built-in tool, the harness tools and `mcp__*`, and the match-all
      deny hook, the same pattern as the judge. Each is pinned by a test.
- [ ] **INV-2 and INV-3 are enforced by the program:** a draft with no passage
      citation, or citing a passage id that was not shown, is refused; a claim the
      checker marks unsupported never reaches the printed draft; if the checker
      removes the substance, the output is `escalate: not answerable from the docs`.
- [ ] **INV-1 holds by construction:** no command posts to GitHub; the output says
      `NOT POSTED`. The Charter's end action is a pull request, never a post.
- [ ] **Verdict-style parsing, fail closed:** the drafter returns one reply block
      and the checker one line per claim (`supported` or `unsupported`, with the
      passage id); anything else is `draft error` and shows nothing as checked.
- [ ] **A gate, pre-registered before it is run:** a held-out set of at least 20
      realistic questions (answerable and not), written by the support session,
      not the builder, committed after the method freezes, scored once. Bars,
      fixed now: **no unsupported claim survives into any printed draft**, and at
      least 80% of the answerable questions get a draft the key marks fully
      supported and useful. The Architect pre-registers the exact scoring.
- [ ] **Reported in the same run:** drafts the checker changed; unsupported claims
      the checker caught; drafts escalated; the end-to-end figure; spend per draft.
- [ ] **Code review layer (pack v24):** `code-review.md`, tier High for the agent
      and deny-list files; the Release Manager checks every finding.
- [ ] **Security Review at adversarial depth** (a hostile question or passage trying
      to steer the drafter or checker; the parser; what each agent receives), and
      the **Release Gate at tier 3**. Landing: a pull request the owner merges.
- [ ] README and `.agentic/CURRENT_MVP_STATUS.md` state only recorded figures.

## Must not break

INV-1 to INV-5 as approved. Nothing is posted. The user can see where every
passage came from. The program makes no network call outside `ingest`.

## Constraints

Python 3.12, uv, no new runtime dependency. Subscription only: no API key, no
`claude -p`, no terminal client, no Azure. Attended: the operator runs it. One
session runs the slice (pack v24); the owner starts no other session.

## Out of scope

Posting, GitHub intake, scheduling, a runtime model client, any deploy, changing
retrieval or the judge, multi-turn conversations.

## Stakes

- [x] Touches real user data (a question and passages go to Anthropic through the
      operator's session; **public GitHub text only** until a DPA exists)
- [ ] Moves money, or changes billing
- [ ] Irreversible (the run ends in a pull request; the owner merges)
- [x] Changes auth, permissions, or a safety control (INV-2, INV-3 wording)
- [ ] Adds a screen or UI
- [ ] None of the above

## For the Charter (recommended answers; the owner changes any before approving)

| Charter section | Recommended line |
|---|---|
| C2 budget | plan 1.2M; ceiling 1.6M; hard cap 2.0M (a new method, a gate set, tier 3 reviews) |
| C3 models | drafter `claude-sonnet-5-5`; checker `claude-opus-5-5`; the operator's session only, zero tools |
| C4 processors | Anthropic through the operator's session, as before; **DPA: none, so public text only** (the owner restates this) |
| C5 safety controls | INV-2 and INV-3 may gain the exact enforcement wording drafted by the Architect, reviewed by a different-model adversarial reviewer against these bounds; INV-1, INV-4, INV-5 unchanged except a named list of what the draft agents receive |
| C6 prerequisites | C6.P permission rules in the local settings file; pack v24; dry run of each |
| C7 depth | Security adversarial; Release Gate tier 3 |
| C8.1 | on a failed gate: close as not releasable and stop |
| C8.2 | push the branch and open a pull request; never merge, deploy, post or send |
| C8.4 | review |
