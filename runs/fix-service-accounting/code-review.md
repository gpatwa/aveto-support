5 findings (0 Important, 3 Nit, 1 Pre-existing, 1 behaviour note routed to Docs).

# Code review — fix-service-accounting

- **Reviewer:** the local `/code-review` skill at `high` effort, run by the Orchestrator (`claude-opus-5-5`), which did not write the change. Rules: `REVIEW.md`. Base: `main` (87178bd). Head reviewed: 5f86fd3.
- **Scored:** no. The review is `unscored` (Charter C3.R: no rescore since 2026-10-17).
- **Tier: High.** Set by `aveto_service/pipeline.py`, `aveto_service/limits.py` behaviour (spend reservation and the day's cap), `aveto_service/judge_port.py`, `aveto_service/anthropic_judge.py` (the runtime model adapter's billing count), `aveto_service/settings.py` and `infra/main.bicep` (price that drives the cap). The intent also names High. Human review at the end: the owner reads the change itself; rollback (previous revision) is the C8.1 plan.

## Round 1

| id | severity | file:line | what and what triggers it | how to reproduce | disposition |
|---|---|---|---|---|---|
| CR-1 | Nit | tests/test_service_limits.py:159 | `test_retry_never_settles_above_cap` on head never sends a request: with cap = one reservation the new admission refuses (PAUSED), so `spent <= cap` holds trivially. The retry-within-cap case is covered only by `test_retry_settles_within_both_reserved_attempts` (:170). | read the asserts at :164-166 | intentional: it is the intent's own scenario ("a cap equal to one reservation"), it failed first on 87178bd with the reviewer's figure, and :170 covers a retry that does run |
| CR-2 | Nit | aveto_service/pipeline.py:276 | a non-`JudgeTransportError` exception from the adapter is charged one attempt though two were reserved | a fake adapter that raises `RuntimeError` after a billed 503 | intentional: unreachable with the real adapter (its `except Exception` maps every failure to `JudgeTransportError` with `billable_failures`); same charge as before the change |
| CR-3 | Nit (behaviour note) | aveto_service/limits.py:184 (via pipeline.py:254) | reserving two attempts makes `reserve` close the day when settled spend + 2R exceeds the cap, so the pause comes at about 33 questions a day by the spec's estimate, not the intent's "about 41" | spec 05 §3, cost estimate | intentional (tech spec §2, option a); routed to stage 7: docs must quote the spec's labelled estimate, not 41 |
| CR-4 | Pre-existing | aveto_service/limits.py:204 | `settle` adds the actual cost unclamped; if real input tokens exceed the byte-based estimate (framing over `FRAMING_TOKENS`), settled spend can pass the reservation | not reproduced; the estimate assumes ≥ 1 byte per token | reported, not blocking; not in this slice's scope |
| CR-5 | Nit | aveto_service/judge_port.py:36 | the port's default `billable_failures` repeats the `NEVER_BILLED` rule the adapter applies per attempt | read both | intentional: the default keeps every existing test fake's charge unchanged (spec §3.2); the adapter always passes an explicit count |

No Important finding; no fix round needed. Security (stage 6) is asked to rule on CR-3's capacity effect together with the 429-then-success charge change.
