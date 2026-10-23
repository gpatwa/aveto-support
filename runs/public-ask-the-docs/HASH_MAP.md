# Hash map: branch history rewritten on 2026-10-22 (owner's decision B)

The owner's Azure sign-in email was in an early run record (`runs/public-ask-the-docs/STATE.md`, commit `8d7cf7f`). The branch was rewritten before its first push so that no commit holds it: the only change in any commit is that one string, replaced by `[owner email removed]` in `STATE.md`. The **final tree is byte-identical** to the pre-rewrite tree (`git diff` between the two heads is empty), so no content, figure or result changed. Only the commit hashes did.

Why a table: the records cite old hashes, and **the deployed image tags are the first 12 hex digits of a commit**: the image `aveto-ask:0fa04abda8ad` is built from what is now commit `69d22317dfa9`, and the live image `aveto-ask:879cae23690b` (revision `ca-aveto-ask--0000006`) from what is now commit `8ebf76c6848d`. The code in those two commits is the same as in the table's new hashes; only the commit ids differ.

Commits 1 to 33 of the branch, oldest first (`main` is `2919c87` and did not change). The branch also carries this table's own commit and the commits after it, which exist only under their new hashes.

| # | Old hash (as cited in the records) | New hash (on the pushed branch) | Subject |
|---|---|---|---|
| 1 | `8d7cf7f8a88a` | `f7b09561cfa6` | public-ask-the-docs: intent, plan, Charter approved (APPROVAL_RECORD-1) |
| 2 | `a09db64245a0` | `ebdd48117a92` | public-ask-the-docs: stages 1-7 (scope, PRD, specs, tech spec, AI and compliance review) |
| 3 | `e321d6e30d4b` | `8d9dbb9e11df` | public-ask-the-docs: stage 8 service, limits, logging, kill switch, tests; UX copy amendme |
| 4 | `4af58053163f` | `91c97c99f910` | public-ask-the-docs: stages 9-10 Anthropic judge adapter and the public page |
| 5 | `2719111b2dc9` | `826b6fb56187` | public-ask-the-docs: stage 11 partial (Bicep written; guard blocked three files); SR-1 |
| 6 | `e08befc96d99` | `defe46bf4301` | public-ask-the-docs: stage 11 Dockerfile, Bicep (lint clean, what-if scoped to C8.3), infr |
| 7 | `052b36cba976` | `a6a7a9ed1cc6` | public-ask-the-docs: code-review round 1 fixes (CR-1, CR-2, CR-5, CR-6) |
| 8 | `221985fdb3af` | `66c0061c119f` | public-ask-the-docs: stage 12 review layer recorded |
| 9 | `f84f562cad95` | `3785d8c9bb7b` | public-ask-the-docs: stage 13 QA evidence and browser checks |
| 10 | `8b3c978b5134` | `ba66d29c1a28` | public-ask-the-docs: stage 14 Security Review (adversarial) and required fixes S-R1, S-R2, |
| 11 | `b8601838aaa0` | `c16fa3fb2da0` | public-ask-the-docs: security round 2 (S-A2, S-A4, S-A6, S-A8, telemetry off) |
| 12 | `5f528a5d5441` | `5c4729ffdf3c` | public-ask-the-docs: stage 15 docs and safety words; Charter v2 drafted (two stops from th |
| 13 | `b0cf09d841ea` | `b5a745b055ce` | public-ask-the-docs: Charter v2 approved (APPROVAL_RECORD-2) |
| 14 | `9f40e9a0aaa8` | `005342a56874` | public-ask-the-docs: runbook vault statement and safety-word alignment; final-tree checks |
| 15 | `73363c56d6d3` | `a44eb6a71b82` | public-ask-the-docs: stage 16 Release Gate (GO WITH CONDITIONS), runbook processors and mo |
| 16 | `0fa04abda8ad` | `69d22317dfa9` | public-ask-the-docs: P2 re-check at the commit to be built |
| 17 | `879cae23690b` | `8ebf76c6848d` | public-ask-the-docs: F-LIVE-1 Dockerfile gives uid 10001 read access to index and models |
| 18 | `bbff9a97abbf` | `aca4009d2e6c` | public-ask-the-docs: P2 re-check 2 |
| 19 | `c5d3b72708e8` | `d226b095146e` | public-ask-the-docs: stage 17 deploy with kill switch ON; F-LIVE-1 found and fixed; switch |
| 20 | `85c1039c81ee` | `02d31219dd9b` | public-ask-the-docs: STATE next action |
| 21 | `3f966370be87` | `059b2cc428e2` | public-ask-the-docs: S-C1 step 2 passed (owner's phone vs this Mac, one replica) |
| 22 | `dad648b375c8` | `592982165fbf` | public-ask-the-docs: switch-on conditions C1-C4 saved; Approvals row for kill switch OFF |
| 23 | `25524e1c3ade` | `c2adcb3f8d38` | public-ask-the-docs: switch on, first call judge_error, kill switch ON again (C8.1) |
| 24 | `6ada0a99f618` | `12a6d6d979e6` | public-ask-the-docs: first live call succeeds after key re-store; M3, G5, E3 recorded |
| 25 | `d967deacd270` | `6e7bf5b1bf53` | public-ask-the-docs: STATE after stage 17 |
| 26 | `9ed129cd9138` | `1a057d2f21f9` | public-ask-the-docs: gate set committed after the method freeze (sha256 7eb4f588…064f) and |
| 27 | `160fdd1bd926` | `74b83d32c07b` | public-ask-the-docs: gate batch 1 (p01-p10) scored once: 8/10 answerable |
| 28 | `aceb307bd885` | `179fbfd44fb1` | public-ask-the-docs: gate scored once: Bar 1 10/10, Bar 2 8/10 (both met; exactly at the b |
| 29 | `9034e579e501` | `9ac786a2d2f0` | public-ask-the-docs: production verification (healthy with watch items), recorded figures  |
| 30 | `fff8dd6e5188` | `ae2026088cfc` | public-ask-the-docs: remove the owner's account email from STATE.md (the one earlier commi |
| 31 | `13d259293334` | `6504917b5343` | public-ask-the-docs: lint-only edits to the gate scorer (logic unchanged, report re-run gi |
| 32 | `85614ff6a111` | `1821e1bbbab2` | public-ask-the-docs: stage 19 done: END_REVIEW, trace.json, post-launch learning, final ch |
| 33 | `c840bc6a19b0` | `773095d5b5eb` | public-ask-the-docs: STATE budget line |
