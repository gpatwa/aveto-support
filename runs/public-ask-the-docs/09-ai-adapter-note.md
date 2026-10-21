# AI adapter note: public-ask-the-docs, stage 9 (AI Engineer, depth standard)

Status: done. `uv run mypy` clean, `ruff check` clean, `pytest` 559 passed, 12 deselected (whole suite, incl. the Frontend's work-in-progress files). Nothing committed. No live call made, no key used.

## Built
`aveto_service/anthropic_judge.py`: `AnthropicJudgeClient(api_key, *, client=None, sleep=time.sleep)` implementing `JudgeClient`; `build_request()`, `extract_reply()`, `prompt_matches_pin()`.
- Request exactly `model=claude-sonnet-5-5, max_tokens=1024, system=<prompt>, messages=[user: payload], output_config={"effort":"high"}`. No tools, tool_choice, metadata, temperature, headers.
- `anthropic.Anthropic(api_key, max_retries=0, timeout=20.0)`. At most 2 attempts, 1.0 s injectable backoff, retry only on RateLimit, 5xx (InternalServerError) and non-timeout connection errors. `attempts=2` set on `JudgeCall` and on `JudgeTransportError` when a retry happened.
- Fixed categories: `timeout, connection, status_4xx, status_5xx, stop_reason, tool_use, prompt_hash, other`. Errors raised `from None`; no exception text, request or response kept.
- Prompt hash: sha256 of the `system_prompt` passed in is compared with `judge.PROMPT_SHA256` on every call; mismatch -> `JudgeTransportError("prompt_hash", attempts=0)` before any request.
- Key: passed in by the caller (`main.py` reads `ANTHROPIC_API_KEY`); the module reads no environment, never logs, empty key -> `ValueError` with no key text.
- Effort: SDK 1.7.0 `messages.create` has `output_config` (test checks the signature), so it is expressible; no STOP.

## Tests (`tests/test_anthropic_judge.py`, 24)
no tools; body keys exact, system == prompt bytes, one user message == payload, no key in body; model/effort/max_tokens pinned; SDK signature has the fields; success maps usage; text-only extraction, thinking dropped, tool_use -> error; six non-end_turn stop reasons; 4xx/timeout/other mapping with canary text absent from repr/str/args and no `__cause__`; retry once for 429/500/529/connection, attempts=2, backoff 1.0; no retry on timeout/4xx; attempts=2 on stop_reason after retry; prompt hash mismatch fails closed with zero requests; empty key; real SDK client offline (socket block) with DEBUG logging: no key or payload in logs/stdout/stderr/error; client config (max_retries 0, timeout 20); no print/environ in source; import allow-list; SDK loggers muted.

## Deviations / findings
1. Found: with root logging at DEBUG, the SDK's `anthropic` logger printed the request options (payload and system prompt; not the key). The spec relies on `configure_logging()` silencing it. I added defence in depth: the adapter's constructor sets the `anthropic, httpx, httpx2, httpcore, httpcore2` loggers above CRITICAL and `propagate=False`. Adds `logging` to the module's imports (stdlib), and an allow-list test.
2. The import allow-list is my own (stdlib `hashlib, logging, time, collections, typing`; `anthropic`; `aveto_service.judge_port`; `aveto_support.judge`); the spec names none for this module.
3. The adapter has no startup hash check of its own; the service's `load_runtime` does that at start, the adapter re-checks per call (cheap).
4. The mapping treats HTTP 429 as `status_4xx` (retried once); categories are never shown.

## Unconfirmed
- (U) `claude-sonnet-5-5` accepts `output_config.effort` and the model id: no live call; stage 17.
- (U) `x-stainless-*` header set and that no extra header carries visitor data: not inspected; stage 14.
- (U) whether the model emits thinking at high effort inside the 1024-token cap (a `max_tokens` stop -> `judge_error`): stage 17.
- Looked at: `anthropic` 1.7.0 installed source (`messages.create` signature, exception classes), tests run against fakes only.
