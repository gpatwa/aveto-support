# Tech spec: public-ask-the-docs (stage 5, Software Architect, depth standard)

Sources read: `intent.md`, `CHARTER.md` (sha256 d0acc534…fa74c, every line), `00-slice-plan.md`, `01-scope.md`, `02-prd.md`, `03-feature-spec.md`, `04-ux-spec.md`, `.agentic/SAFETY_INVARIANTS.md` (INV-4, INV-5), `.agentic/LOCAL_COMMANDS.md`, `docs/ARCHITECTURE.md`, ADR 0001, and the code: `aveto_support/{search,judge,judge_eval,__main__,index}.py`, `prompts/answerability-judge-v1.txt`, `.claude/agents/aveto-answerability-judge.md`, `.claude/skills/aveto-judge/SKILL.md`, `pyproject.toml`, `tests/conftest.py`, `tests/test_judge.py` (import allow-list). **(U)** marks a line I could not confirm; each says where I looked. No web access in this stage.

## 0. Summary and traceability ("Done means" → design)

A new top-level package `aveto_service/` (FastAPI) wraps the **unchanged** `aveto_support` functions. Per question it runs the gates in a fixed fail-closed order, then `judge.retrieve_for_judge` → `judge.format_judge_input` → one Anthropic Messages call → `judge.parse_verdict`, and maps the result to JSON or HTML. Nothing in `aveto_support/`, `prompts/`, `.claude/` changes.

| Done means | Satisfied by |
|---|---|
| 1 Starts from main; core unchanged | §1.1 (no edit to `aveto_support/`, `prompts/`, `docs-source.toml`); test `test_core_files_unchanged` (§10) |
| 2 `POST /ask`, `GET /health`; JSON = judge-apply's (a)/(b)/(c); passages byte-identical | §1.3, §1.4; `test_service_passages_byte_identical_to_retrieve` |
| 3 Anthropic API, `claude-sonnet-5-5`, no tools, same prompt + parser, only question + passages sent | §2; `test_request_has_no_tools`, `test_request_body_only_c41_data` |
| 4 Limits fail closed (10/h, daily spend, 500 chars, kill switch, console backstop) | §3, §4 |
| 5 No visitor data kept; 7-day abuse log; question never in a log line | §5 |
| 6 Container Apps, scale to zero, image with pinned models, IaC | §6, §7 |
| 7 Public page served by the service | §1.5 |
| 8 Gate scored through the deployed service | stage 18; §3 notes the shared quota |
| 9 Measured figures | §8 (estimates now; `GET /health` exposes token counters for the measurement) |
| 10 Security adversarial, tier 3 | §10, §11 give Security its checks |
| 11 Docs state recorded figures | Tech Writer, stage 15; §11 |

## 1. Module layout, service surface, routes

### 1.1 Files (all new unless stated)

| Path | Purpose | Owner (§12) |
|---|---|---|
| `aveto_service/__init__.py` | empty, docstring only | Backend |
| `aveto_service/settings.py` | reads env once at startup into a frozen `Settings`; any unparsable value → kill switch **on** | Backend |
| `aveto_service/judge_port.py` | `JudgeCall` dataclass, `JudgeClient` Protocol, `PlaceholderJudgeClient`, `JudgeTransportError` (§2.1) | Backend |
| `aveto_service/limits.py` | `client_key()`, `validate_question()`, `RateLimiter`, `SpendCounter`, `utc_day()` (§3) | Backend |
| `aveto_service/abuse_log.py` | `Outcome` enum, `abuse_line()`, `configure_logging()` with the allow-list filter (§5) | Backend |
| `aveto_service/pipeline.py` | `AskService.ask(raw: str, client_ip: str) -> AskResult` — gates, retrieve, judge, mapping | Backend |
| `aveto_service/html_port.py` | `HtmlRenderer` Protocol: `page(state) -> Response`, `form_outcome(result, raw) -> Response`, `result_page(token) -> Response`, `static(name) -> Response` | Backend |
| `aveto_service/app.py` | `load_runtime(settings)` (§1.2) and `create_app(runtime, judge, settings, html: HtmlRenderer \| None) -> FastAPI`: `POST /ask` (JSON and form), `GET /health`, and, when `html` is given, `GET /`, `GET /result/{token}`, `GET /static/{name}`; body cap, security headers, catch-all handler. With `html=None`, `GET /` is 404 and a form post is `bad_request` | Backend |
| `aveto_service/main.py` | composition root, uvicorn target `aveto_service.main:app`, exactly: `settings = Settings.from_env()`; `runtime = load_runtime(settings)`; `judge = AnthropicJudgeClient(settings.api_key) if settings.api_key else PlaceholderJudgeClient()`; `app = create_app(runtime, judge, settings, html=HtmlPages(runtime))` | Frontend (last code stage; content fixed here) |
| `aveto_service/anthropic_judge.py` | `AnthropicJudgeClient`, `build_request()`, `extract_reply()` (§2) | AI Engineer |
| `aveto_service/pages.py` | `HtmlPages` implementing `HtmlRenderer` | Frontend |
| `aveto_service/render.py` | HTML from `string.Template` + `html.escape` (no Jinja2); every UX state | Frontend |
| `aveto_service/result_store.py` | PRG token store (§1.5) | Frontend |
| `aveto_service/static/enhance.js`, `aveto_service/static/style.css` | UX spec §11 items 4, 8, 9; tokens §8 | Frontend |
| `Dockerfile`, `.dockerignore`, `infra/main.bicep`, `infra/main.parameters.json` | §6, §7 | Cloud Deployment |
| `pyproject.toml`, `uv.lock` (edited) | add the three deps (§9); mypy `files` += `"aveto_service"`; `[[tool.mypy.overrides]]` unchanged | Backend |

**Why a separate top-level package, not `aveto_support/service/`:** INV-5 defines "the program" as `python -m aveto_support`, and C5.2 grants the API egress "for the service alone". Keeping the service outside `aveto_support/` keeps INV-5's existing sentences true word for word, keeps `test_judge_modules_import_allow_list` green unchanged, and lets one AST test prove `aveto_support/` never imports `anthropic`, `fastapi`, `starlette`, `uvicorn`, `httpx`, `httpx2` or `aveto_service` (§10). ADR 0001 says routes "call the same service functions the CLI calls"; this does.

**Reuse without change (C1.3, C5.4).** The service imports and calls, never copies or edits: `judge.normalise_question`, `judge.retrieve_for_judge`, `judge.format_judge_input`, `judge.parse_verdict`, `judge.signal_line`, `judge.BLOCK_ID`, `judge.PROMPT_ID`, `judge.PROMPT_SHA256`, `judge.JudgeError`, `judge.QuestionFormatError`, `judge.PayloadMarkerError`; `search.Searcher`; `index.load_index`; `embed.OnnxEmbedder`. It does **not** use `judge.render_applied` (CLI text) or the transport-file functions (no files in the service path). Ranking is the default `file-rrf-v1` (no reranker loaded), the one the judge was measured on.

### 1.2 Startup (`load_runtime`), fail closed

1. Set `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS` = `1` before numpy import (as `__main__._limit_threads`; also set in the Dockerfile `ENV`).
2. `configure_logging()` (§5) before anything can log.
3. Read `prompts/answerability-judge-v1.txt` as bytes; sha256 must equal `judge.PROMPT_SHA256`; decode UTF-8 → `system_prompt` (kept byte-exact, trailing `\n` included).
4. `load_index(Path(ASK_INDEX))`, `OnnxEmbedder.load(Path(ASK_MODELS), index.params.embedding)` (re-hashes model files), `Searcher(index, embedder)`.
5. (`main.py`) Build `AnthropicJudgeClient` only if `ANTHROPIC_API_KEY` is non-empty; else `PlaceholderJudgeClient` (every ask → `judge_error`, no network).
6. Any failure in 3–4 → log the fixed ops line `{"t":…,"ops":"startup_failed","c":"<category>"}` (category ∈ `prompt_hash`, `index`, `model`) and exit non-zero. The container restarts; `/health` never answers; nothing is shown.

### 1.3 `POST /ask` (JSON for the API and the JS path; form for the no-JS page)

**`POST /ask` is the only route that can reach the judge** (so INV-4's new words, C5.1, name one service caller truthfully). It accepts two request types and dispatches on `Content-Type` after the kill-switch check: `application/json` with body `{"question": "<string>"}` and no other key → JSON below; `application/x-www-form-urlencoded` with exactly one field `question` (parsed with `urllib.parse.parse_qs(body, keep_blank_values=True, strict_parsing=True, max_num_fields=1)`; no `python-multipart`) → `html.form_outcome(...)` (§1.5). Anything else → `bad_request`. Body cap 16 KiB (§3). JSON responses carry `Cache-Control: no-store`. Mapping to `judge-apply` (INV-4):

| INV-4 output | `outcome` | HTTP | Body (exactly these keys) |
|---|---|---|---|
| (a) `ANSWERABLE` | `answer` | 200 | `outcome`, `docs` {`repo`, `commit`}, `files` [{`rank`, `path`, `url`, `passages` [{`heading`, `line_start`, `line_end`, `url`, `text`}]}], `signal` |
| (b) `NOT_ANSWERABLE` | `no_confident_match` | 200 | `outcome`, `text`: `"no confident match"`, `signal` |
| (c) any unusable reply or call failure | `judge_error` | 502 | `outcome`, `text`: `"judge error"` |
| (d) input error (empty, control/format char, no searchable words) | `empty_question` / `unusable_question` | 400 | `outcome` |
| limit: > 500 chars | `too_long` | 400 | `outcome`, `length`, `limit`: 500 |
| limit: body over cap / not JSON / wrong shape | `body_too_large` (413) / `bad_request` (400) | | `outcome` |
| limit: 11th in an hour | `rate_limited` | 429 | `outcome` |
| limit: day's spend share | `paused` | 503 | `outcome` |
| kill switch on | `service_off` | 503 | `outcome` |

- `files`/`passages` come from the **same** `RetrievalResult` object whose `format_judge_input` was sent: same order, `rank`, `path`, `FileHit.url`, and per passage `heading` = `" > ".join(heading_path)` or `"(top of file)"` (the CLI's rule), `line_start`, `line_end`, `PassageMatch.url` (pinned-commit permalink), `text` = `Passage.text` unchanged. No scores, no `top_score`, no `reference`.
- **Difference from the CLI, stated for Security and the Tech Writer:** `judge-apply` prints `retrieve`'s CLI text, which shows a 3-line excerpt per passage plus scores. The service returns the same passages in the same order with their **full** verbatim text and no scores, i.e. exactly the text the judge read. Nothing is added, reworded or selected by a model.
- `signal` = `judge.signal_line(verdict)` verbatim. The page does not display it (UX §5.6); it is in the JSON for traceability.
- No `Retry-After` header on 429/503 (the copy promises no reset time).

### 1.4 `GET /health`

200 JSON, `Cache-Control: no-store`, never calls a model, writes no abuse line: `{"status":"ok","kill_switch":"on"|"off","day":"YYYY-MM-DD","judged_today":int,"input_tokens_today":int,"output_tokens_today":int,"spend_today_usd":"0.000000","daily_cap_usd":"0.322580"}`. Counters are per replica lifetime (§3.4). Stage 18 measures cost per question from the token deltas across a batch, so the figure holds at any price.

### 1.5 HTML routes (Frontend), no cookies, question never in a URL

- `GET /` → the page; result region empty, or pre-filled with the **Service off** state when the kill switch is on (answer to UX §12: **the page loads with the kill switch on** and says so before anyone types).
- Form post to `POST /ask` (no JS; the UX's `action="/ask#result"` stands) → the same `AskService.ask`, then `html.form_outcome`:
  - **No model call happened** (`empty_question`, `unusable_question`, `too_long`, `rate_limited`, `paused`, `service_off`, `bad_request`, `body_too_large`; the last without echoing the text): render the page directly with that state and the visitor's text back in the textarea (HTML-escaped). A reload re-posts only after the browser's own resend prompt, and these states cost nothing.
  - **The request was admitted to the model call** (`answer`, `no_confident_match`, `judge_error`): store the outcome and, for `answer`, its files and passages exactly as in the JSON (public doc text, in order) under `secrets.token_urlsafe(16)` with an expiry, and answer **303** to `/result/<token>#result`. Reload or Back re-renders the stored result and never re-asks. The textarea is empty there; the store holds **no question text** (`AskResult` has no question field).
- `GET /result/{token}` → the stored result, valid 10 minutes, at most 1,000 entries (oldest evicted); unknown or expired → the `GET /` page with an empty result region. The token is random and carries nothing about the question; `Referrer-Policy: no-referrer` keeps it out of GitHub's logs.
- JS (`enhance.js`) intercepts submit and calls `POST /ask` with JSON; without JS the browser posts the form to the same URL.
- Headers on every HTML response: `Cache-Control: no-store`, `Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'`, `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`. No `Set-Cookie` anywhere (test). Static files are read once at startup into memory; only `enhance.js` and `style.css` are served.
- Issue link: `https://github.com/{index.repo}/issues/new?title=Docs+question+not+answered` (never the question). Docs link: `https://github.com/{index.repo}/tree/{index.commit}`.

## 2. Anthropic adapter (AI Engineer; the only generative-model boundary)

### 2.1 Port (Backend writes `judge_port.py` at stage 8, exactly this)

```python
@dataclass(frozen=True)
class JudgeCall:
    reply: str              # concatenated text blocks only; never logged, never returned past the parser
    input_tokens: int | None   # from response usage; None when no response arrived
    output_tokens: int | None

class JudgeTransportError(Exception):
    """The call produced no usable response. `category` is a fixed string; no message text."""

class JudgeClient(Protocol):
    def judge(self, system_prompt: str, payload: str) -> JudgeCall: ...

class PlaceholderJudgeClient:   # default; raises "answerability judge LLM adapter is not configured in this build."
```

The pipeline is the only caller. It passes `reply` straight to `judge.parse_verdict(reply, judge.BLOCK_ID)` and drops the `JudgeCall` (and with it the reason line) before returning. **The reason line never leaves the parser through the service:** `AskResult`, the JSON, the HTML, the result store and the logs carry only the verdict token's consequence.

### 2.2 The request (`build_request(system_prompt, payload) -> dict`, a pure function)

`POST https://api.anthropic.com/v1/messages` via `anthropic.Anthropic(api_key=…, max_retries=0, timeout=20.0)` (a float; the SDK's retries off, ours below), `client.messages.create(**build_request(...))`. The body is exactly:

```json
{"model": "claude-sonnet-5-5",
 "max_tokens": 1024,
 "system": "<prompts/answerability-judge-v1.txt, byte-exact, hash-checked at startup>",
 "messages": [{"role": "user", "content": "<judge.format_judge_input(result), verbatim>"}],
 "output_config": {"effort": "high"}}
```

- This is the attended path's split: the agent file's body is the same prompt text, and `/aveto-judge` passes `judge-input`'s stdout "as its entire prompt, verbatim" (SKILL.md step 3, rule 3). The API call drops the harness context the attended judge also received (INV-5's measured list); the gate measures the judge as called here.
- **Never sent:** `tools`, `tool_choice`, `metadata` (would be a visitor identifier), `temperature`, `top_p`, `top_k`, `stop_sequences`, `thinking`, `stream`, `cache_control`, `service_tier`, `inference_geo`, `container`, `extra_headers` with any visitor value. The visitor's IP, headers and hashed key never reach the adapter (its signature has no such parameter).
- Headers are the SDK's own: `x-api-key`, `anthropic-version`, `content-type`, `user-agent` and the SDK's `x-stainless-*` platform headers (OS, arch, runtime, package version: facts about the container, not the visitor). Security checks these at stage 14 against C4.1's "no visitor request header". (U) exact `x-stainless-*` set: not read in the SDK source.
- **Effort.** Charter C3.1 requires high. I could not confirm the API default for `claude-sonnet-5-5` (looked: the `anthropic` 1.7.0 package source in a local venv, `types/output_config_param.py`, `types/effort_capability.py`, `resources/messages/messages.py`; no default stated), so the request **sends `"effort": "high"` explicitly**. `output_config.effort` with `Literal["low","medium","high","xhigh","max"]` is a typed, non-beta field of `MessageCreateParams` in `anthropic` 1.7.0 (confirmed in that source). (U) that `claude-sonnet-5-5` accepts it: not in 1.7.0's model literal list (`claude-sonnet-5` is; `ModelParam` also accepts any `str`). A rejection shows as `judge_error` on every question at the stage 17 check, before the gate.
- **max_tokens 1024.** One line of ≤ 12 words needs ~25. The headroom covers any internal reasoning the high effort level may add (U: whether this model emits thinking without a `thinking` field). `stop_reason == "max_tokens"` → `judge_error`.
- **Timeout and retries.** 20 s per attempt. The adapter retries **once**, after 1.0 s, only on `anthropic.RateLimitError`, `anthropic.InternalServerError` (5xx incl. 529) and `anthropic.APIConnectionError` that is not `APITimeoutError`. Never on a timeout, 400, 401, 403, 404 or 413. Worst case ≈ 41 s (inside the UX's "up to a minute"). Every attempt is charged to the spend counter (§3, steps 8 and 9). The backoff sleep is injectable so tests never wait.

### 2.3 Response → reply (`extract_reply(message) -> str`) and error mapping

- `stop_reason` must be `"end_turn"`; anything else (`max_tokens`, `refusal`, `tool_use`, `pause_turn`, `stop_sequence`, absent) → `JudgeTransportError("stop_reason")`.
- Any content block of type `tool_use`/`server_tool_use` → `JudgeTransportError("tool_use")`. Blocks of type `thinking`/`redacted_thinking` are discarded unread. Reply = the `text` blocks' text joined with `""`; no text block → `""` (the parser then raises `EMPTY`).
- Usage = `message.usage.input_tokens`, `message.usage.output_tokens`.
- Every SDK exception (`anthropic.APIError` and subclasses, `httpx`/`httpx2` errors, anything else) → `JudgeTransportError` with a fixed category (`timeout`, `connection`, `status_4xx`, `status_5xx`, `stop_reason`, `tool_use`, `other`). The exception's message, request and response objects are dropped (they can hold the payload). The category is never shown or logged; the outcome is `judge_error`.
- Pipeline: `JudgeTransportError` or `judge.JudgeError` → outcome `judge_error` (INV-4 (c)). Verdict `ANSWERABLE` → (a); `NOT_ANSWERABLE` → (b).
- Logging inside the SDK: `configure_logging()` sets `anthropic`, `httpx`, `httpx2`, `httpcore` loggers to `CRITICAL` and the allow-list filter drops them anyway; `ANTHROPIC_LOG` is never set (the SDK's debug logging prints request options, which hold the payload).

### 2.4 SDK pin

`anthropic==1.7.0`. Confirmed to exist only as an installed distribution (`/Users/gopalpatwa/opt/hr-timeoff-agent/.venv/…/anthropic-1.7.0.dist-info`, which declares `anyio, docstring-parser, httpx2, jiter, pydantic, sniffio, typing-extensions`). (U) that 1.7.0 is the newest release or still on PyPI: no index access; `uv lock` at stage 8 settles it, and if it fails the Backend Architect pins the version `uv` resolves for `anthropic>=1.7,<2`, records it, and AI Engineer re-checks `output_config` in that version's source.

## 3. Limits, in fail-closed order (Backend, `limits.py` + `pipeline.py`)

Every step before 8 makes **no model call**. Every refusal writes one abuse line (§5) and returns the outcome in §1.3. Any exception inside a check is the refusal of that check, never a pass.

| # | Check | Refuses with | Consumes allowance? |
|---|---|---|---|
| 1 | Kill switch: `settings.kill_switch == "on"` (read before the body) | `service_off` | no |
| 2 | Body: `Content-Length` > 16,384, or more than 16,384 bytes read from the stream → stop reading; not JSON / not form / wrong keys / non-string | `body_too_large` / `bad_request` | no |
| 3 | Question: `raw.replace("\r\n","\n").strip()`; empty → `empty_question`; `len()` in code points > 500 → `too_long` (the client counts the same way, UX §7); `judge.normalise_question` raises → `unusable_question` | as named | no |
| 4 | Per visitor, peek: ≥ 10 admitted questions for this key in the last 3,600 s (monotonic clock) | `rate_limited` | no |
| 5 | Spend, peek: the UTC day is closed, or `spent + in_flight + R_floor > cap` | `paused` | no |
| 6 | Local work: `judge.retrieve_for_judge` → `judge.format_judge_input` (serialised by a `threading.Lock`; the ONNX session is used by one thread at a time). `QuestionFormatError` → `unusable_question`; `PayloadMarkerError` or any other error → `judge_error` | as named | no |
| 7 | **Admission, atomic** under one `threading.Lock`: re-check 4; compute `R` for this payload; if `spent + in_flight + R > cap` → `paused` **and close the day**; else append the visitor's timestamp and add `R` to `in_flight` | `rate_limited` / `paused` | **yes, from here** |
| 8 | Model call (§2), at most 2 attempts; before attempt 2, reserve another `R` atomically or stop with `judge_error` | — | — |
| 9 | Settle: a successful attempt's `R` is replaced by its actual cost from `usage`; a failed attempt keeps its full `R` (it may have been billed) | — | — |

- **Does a judge error count against the hourly allowance? Yes.** The model was called and charged; counting it also stops a hostile visitor from forcing free retries. Refusals at steps 1–7 do not count.
- **Reservation `R`** (integer nano-dollars, no floats): `(utf8_bytes(system_prompt) + utf8_bytes(payload) + 64) × P_in + 1024 × P_out`. A token never covers less than one byte, so the input part is an upper bound; `max_tokens` bounds the output. `R_floor` is the same with an empty payload (≈ $0.0175 at the prices below).
- **Prices** (env, defaults in code): `ASK_PRICE_IN_NANO_PER_TOKEN=3000` ($3/MTok), `ASK_PRICE_OUT_NANO_PER_TOKEN=15000` ($15/MTok). **(U)** These are the Sonnet-class list prices I recall for earlier Sonnet models; the price of `claude-sonnet-5-5` is not in the repo or the SDK source (looked: repo grep for "price", `anthropic` 1.7.0 `types/`). The owner confirms the price at the end review; a correction is a parameter change (§7). The token counters in `/health` keep the measurement valid at any price.
- **Daily cap**: `ASK_MONTHLY_CAP_USD=10` → `cap = 10 × 10⁹ // 31 = 322,580,645` nano-dollars ($0.3226; the longest month, so 31 days never exceed $10). **Reset at 00:00:00 UTC**; a closed day reopens then. The page copy promises no reset time (UX §4), so the zone is stated only in the runbook.
- **Client key**: Container Apps ingress appends the connecting address to `X-Forwarded-For`. Use the **rightmost** entry only (`ipaddress.ip_address`; invalid → the ASGI peer address). Never the leftmost entry, `X-Real-IP`, `Forwarded` or `X-Envoy-*`. uvicorn runs with `--no-proxy-headers`, so nothing rewrites `request.client`. IPv6 is keyed by its /64 (one host controls a /64); IPv4-mapped IPv6 → the IPv4 address. Key = `hmac(SALT, key_bytes, sha256)` with `SALT = secrets.token_bytes(32)` per process, in memory only, never logged; the log carries the first 16 hex characters. **(U)** that the ingress appends rather than passes the client's header unchanged, and that the rightmost entry is the client: Envoy's behaviour from memory, no Container Apps docs read. Stage 17 checks it with empty-question requests (no model call): requests with different forged `X-Forwarded-For` values from one machine must log the same `ip` hash. If they do not, set `ASK_CLIENT_KEY=peer` (§7 parameter): every visitor then shares one bucket, which fails closed.
- **Memory bounds**: at most 50,000 visitor keys (entries idle > 1 h are swept first); a new key beyond that → `rate_limited`. Timestamps are monotonic floats; no IP, no question.

### 3.4 Replicas, scale to zero, and what the counters can promise

`maxReplicas: 1` (Bicep) and `uvicorn --workers 1` put every counter in one process. That makes them exact **within one replica's lifetime** and race-free (one lock). They are **not** durable: the replica stops after the scale-to-zero cooldown (platform default 300 s, (U), not read in docs), on a kill-switch change (new revision), a crash or a platform move, and a new replica starts at zero. So the 10-an-hour limit and the daily share hold per replica lifetime; a visitor who waits out an idle cooldown gets a fresh count, and so does the day's spend. The month's money cap still holds through the owner's $10 console limit (C6.6): beyond it Anthropic refuses calls, which the service shows as `judge_error` with no passage.

A counter that survives restarts needs one of: a storage account (not in C8.3), a role letting the identity query Log Analytics (C8.3 names two roles only), or `minReplicas: 1` (C8.3 says "scale to zero"). **None is in the Charter, so this spec does not use one.** This is the one place where "Done means" line 4 is met only per replica lifetime. It is an owner decision at the end review and a Security item at stage 14, not a reason to act outside the Charter.

## 4. Kill switch

**Mechanism: the Container App environment variable `ASK_KILL_SWITCH`, set from the Bicep parameter `killSwitch` (`allowed: ['on','off']`, default `'on'`), applied with `az deployment group create` (§7).** The service reads it once at startup; any value other than exactly `off` (missing, empty, misspelt) means **on**.

- Uses only C8.3 resources and C8.3's own words ("deploy the Bicep in the repo with `az deployment group create`; set the kill switch on or off"). No CLI extension, no Key Vault write, no new resource. Runnable by an agent on C8.1's failure path.
- **What "without a redeploy" means here, stated plainly:** no image build and no code change; the same image digest. Container Apps does create a **new revision** for an env change and replaces the replica (about tens of seconds, (U), measured at stage 17). If the owner reads "without a redeploy" as "without a new revision", no in-Charter mechanism I could confirm meets it: a Container Apps secret plus a revision restart needs `az rest` calls C8.3 does not name, and an ingress IP restriction blanks the page. Recorded for the end review; not a STOP.
- **On**: `GET /` loads and shows "The service is off" before anyone types; `POST /ask` (JSON or form) answers `service_off` before reading the body; `GET /health` reports `"kill_switch":"on"`. No retrieval, no model call.
- Default `'on'` means a deploy that forgets the parameter comes up off (fail closed). Stage 17 deploys with `on`, checks the off state, then deploys `off`, so both directions are exercised before the gate.

## 5. Logging contract (Backend, `abuse_log.py`) — the service's only events

There is no database and no other audit store; these lines are the slice's audit, usage and abuse events.

- **Abuse line**, one per `POST /ask` request (JSON or form), on stdout, exactly: `{"t":"2026-10-21T07:00:00Z","ip":"<16 lowercase hex>","o":"<code>"}`. Built only by `abuse_line(ip16: str, outcome: Outcome, now: datetime) -> str`, which takes no other argument. `Outcome` codes: `answer`, `no_confident_match`, `judge_error`, `empty_question`, `too_long`, `unusable_question`, `body_too_large`, `bad_request`, `rate_limited`, `paused`, `service_off`. Time to the second, UTC. Never the question, passages, payload, reply, headers, URL, user agent or request body.
- **Ops line**, fixed codes only: `{"t":…,"ops":"startup_ok"}`, `{"t":…,"ops":"startup_failed","c":"prompt_hash|index|model"}`, `{"t":…,"ops":"unhandled"}`. No variable text.
- **Usage** is not logged (C4.2 lists only abuse lines and platform logs); it is exposed as counters in `GET /health` (§1.4).
- **Everything else is silenced.** `configure_logging()`: root logger → one stdout handler with a filter that passes only `aveto_service.abuse` and `aveto_service.ops`; the `uvicorn`, `uvicorn.error`, `uvicorn.access`, `anthropic`, `httpx`, `httpx2`, `httpcore`, `fastapi`, `starlette` loggers get their handlers removed, `propagate=False`, `disabled=True`; `sys.excepthook` and `threading.excepthook` write the `unhandled` ops line only. uvicorn runs with `--no-access-log --log-level critical --no-proxy-headers --no-server-header --no-date-header --workers 1`. Route functions catch every exception themselves (Starlette's server-error middleware re-raises to uvicorn, which would print a traceback that can hold request bytes); the catch-all handler is a second line of defence.
- **Platform logs.** Container Apps sends the container's stdout/stderr to `ContainerAppConsoleLogs_CL` and revision events to `ContainerAppSystemLogs_CL` (log-analytics destination). The question travels only in a POST body, never in a URL, so no platform access record can carry it. (U) whether the ingress writes per-request records anywhere in the workspace: not read; stage 17 lists the workspace's tables after the first requests and reports any extra table.
- **7-day retention.** Workspace `retentionInDays: 30` (the workspace floor, (U)) and `workspaceCapping.dailyQuotaGb: 0.5` (a cost guard); the two tables above get `retentionInDays: 7`, `totalRetentionInDays: 7` through `Microsoft.OperationalInsights/workspaces/tables` in the same Bicep, deployed with `configureLogRetention=true` once the tables exist (they appear on first ingestion, (U)). Until then the kill switch is on and the only lines are ops lines; no visitor request is served before retention is set (§7 order). Stage 17 proves it read-only: `az monitor log-analytics workspace table show -g rg-aveto-ask --workspace-name log-aveto-ask -n ContainerAppConsoleLogs_CL --query "{r:retentionInDays,t:totalRetentionInDays}"` prints 7 and 7. (U) that table retention can go below 30 days (from memory: 4 to 730 for Analytics tables).
- **Proof that a question never reaches a log line:** `test_question_never_logged` (§10).

## 6. Container image (Cloud Deployment: `Dockerfile`, `.dockerignore`)

- **Base:** `python:3.12-slim-bookworm` for both stages, by tag; the digest `az acr build` resolves is recorded from its log at stage 17 (no registry access at this stage to read it now, (U)). uv copied from `ghcr.io/astral-sh/uv:<the version in the developer's toolchain>` (stage 11 records `uv --version`; (U) not read here).
- **Build stage:** `WORKDIR /app`; copy `pyproject.toml`, `uv.lock`; `uv sync --locked --no-dev`; copy `aveto_support/`, `aveto_service/`, `prompts/`, `docs-source.toml`, `evals/calibration-offtopic.toml`; run `uv run --no-sync python -m aveto_support ingest`. That makes exactly INV-5 (a) and (b)'s two GETs (the docs archive at the pinned commit; the embedding model's two files at the pinned revision), sha256-checked before use, **at build time inside `az acr build`**; no reranker (`--with-reranker` not passed). Ingest's last line (`wrote index/docs-index.json  sha256 <hex>`) is in the build log; stage 17 compares it with the local index's sha256 and reports match or mismatch (different CPUs may round an int8 differently; a mismatch is reported, not hidden, and the deployed index is the one the gate measures).
- **Why build-time ingest rather than copying local `models/`, `index/`:** both are gitignored, so "built from this repo" would otherwise depend on unrecorded files on one laptop. `.dockerignore` therefore excludes them: `.git`, `.venv`, `models/`, `index/`, `runs/`, `.claude/`, `.aveto-judge/`, `tests/`, `tools/`, `docs/`, `intents/`, `evals/` with `!evals/calibration-offtopic.toml`, `**/__pycache__`, `*.env`, `.env*`.
- **Runtime stage:** copy `/app/.venv`, `/app/aveto_support`, `/app/aveto_service`, `/app/prompts`, `/app/index`, `/app/models` from the build stage, all owned by root and not writable by the app user; `WORKDIR /app` (the service reads `prompts/answerability-judge-v1.txt` relative to it). `RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app`; `USER 10001`. `ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 ASK_INDEX=/app/index/docs-index.json ASK_MODELS=/app/models`. `EXPOSE 8000`. `CMD ["/app/.venv/bin/uvicorn","aveto_service.main:app","--host","0.0.0.0","--port","8000","--workers","1","--no-access-log","--log-level","critical","--no-proxy-headers","--no-server-header","--no-date-header"]`.
- **No key in the image.** No `ARG`/`ENV` carries a secret; the build has no key. `ANTHROPIC_API_KEY` exists only at runtime, injected by Container Apps from the Key Vault reference (§7). `test_dockerfile_static` (§10) fails on `ANTHROPIC_API_KEY`, `ARG .*KEY`, `--with-reranker`, or a missing `USER`.
- Size estimate ≈ 0.45 GB (slim base, onnxruntime, numpy, the ~130 MB ONNX model, index): (U), measured from the build log.

## 7. Infrastructure (Cloud Deployment: `infra/main.bicep`, `infra/main.parameters.json`)

**Resources: exactly C8.3's list, in `rg-aveto-ask` (eastus2), nothing else.** `test_bicep_resources_are_c83` (§10) parses the file and fails on any other resource type.

| Resource (type) | Name | Settings |
|---|---|---|
| User-assigned identity (`Microsoft.ManagedIdentity/userAssignedIdentities`) | `id-aveto-ask` | — |
| Container registry (`Microsoft.ContainerRegistry/registries`) | `acravetoaskgp` (globally unique, (U) free) | SKU Basic; `adminUserEnabled: false`; `anonymousPullEnabled: false` |
| Log Analytics (`Microsoft.OperationalInsights/workspaces`, plus its `tables` children for retention) | `log-aveto-ask` | PerGB2018; `retentionInDays: 30`; `workspaceCapping.dailyQuotaGb: 0.5`; tables per §5 when `configureLogRetention` |
| Container Apps environment (`Microsoft.App/managedEnvironments`) | `cae-aveto-ask` | Consumption only; `appLogsConfiguration.destination: 'log-analytics'` with the workspace's customerId and shared key (from `listKeys()` in Bicep, never in a file) |
| Container App (`Microsoft.App/containerApps`), only when `deployApp` | `ca-aveto-ask` | identity: `id-aveto-ask`; `activeRevisionsMode: 'Single'`; ingress `external: true`, `targetPort: 8000`, `transport: 'auto'`, `allowInsecure: false`; registry `{server: acr loginServer, identity: id-aveto-ask}`; secret `{name: 'anthropic-api-key', keyVaultUrl: 'https://kv-aveto-ask-gp.vault.azure.net/secrets/anthropic-api-key', identity: id-aveto-ask}`; container 0.5 vCPU / 1 GiB; env `ANTHROPIC_API_KEY` (secretRef), `ASK_KILL_SWITCH` = `killSwitch`, `ASK_CLIENT_KEY` = `clientKey`, price and cap params; scale `minReplicas: 0`, `maxReplicas: 1`, one HTTP rule `concurrentRequests: '10'`; probes: startup and readiness HTTP `GET /health` on 8000, liveness HTTP `GET /health` every 30 s |
| Role assignment (`Microsoft.Authorization/roleAssignments`) | guid(vault, identity, role) | `Key Vault Secrets User` (`4633458b-17de-408a-b874-0445c86b69e6`) on the **existing** vault `kv-aveto-ask-gp` (`existing` reference, not created) |
| Role assignment | guid(acr, identity, role) | `AcrPull` (`7f951dda-4ed3-4680-a7ca-43fe172d538d`) on the registry |

- Role IDs from memory, (U); stage 11 confirms read-only with `az role definition list --name "Key Vault Secrets User" --query "[].name" -o tsv` and the same for `AcrPull`.
- **Key Vault access model, (U), possible STOP:** `Key Vault Secrets User` works only if the vault uses Azure RBAC. Stage 11 checks read-only: `az keyvault show -n kv-aveto-ask-gp --query properties.enableRbacAuthorization`. If it prints `false`, granting access needs a vault access policy, which C8.3 does not list: that is Charter stop 9.1, reported, not worked around.
- Parameters: `deployApp` (bool, default false), `imageTag` (string), `killSwitch` (`on`|`off`, default `on`), `clientKey` (`xff_last`|`peer`, default `xff_last`), `configureLogRetention` (bool, default false), `priceInNanoPerToken` (default 3000), `priceOutNanoPerToken` (default 15000), `monthlyCapUsd` (default 10). `main.parameters.json` holds only `location: eastus2`. No secret value is a parameter.
- Outputs: the app's FQDN, the registry login server. Nothing secret.

**Commands** (run at stage 17 under C8.3 by the Orchestrator's session, which has the shell, using Cloud Deployment's stage-11 note `runs/public-ask-the-docs/11-infra-note.md` as the runbook; Cloud Deployment has no shell (§12, SR-1). Stage 11c, the Backend Architect, runs only the read-only checks of §12, including `az deployment group what-if` with the same arguments):

```sh
RG=rg-aveto-ask; F=infra/main.bicep; P=infra/main.parameters.json; TAG=$(git rev-parse --short=12 HEAD)
# 1. identity, registry, workspace, environment, role assignments (no app yet)
az deployment group create -g $RG -f $F -p @$P -p deployApp=false
# 2. build and push the image from the branch (remote build; runs ingest inside)
az acr build -r acravetoaskgp -t aveto-ask:$TAG --platform linux/amd64 -f Dockerfile .
# 3. the app, kill switch ON
az deployment group create -g $RG -f $F -p @$P -p deployApp=true imageTag=$TAG killSwitch=on
# 4. once ContainerAppConsoleLogs_CL and ContainerAppSystemLogs_CL exist: 7-day retention
az deployment group create -g $RG -f $F -p @$P -p deployApp=true imageTag=$TAG killSwitch=on configureLogRetention=true
# 5. after the off-state, health, header and XFF checks: turn it on
az deployment group create -g $RG -f $F -p @$P -p deployApp=true imageTag=$TAG killSwitch=off configureLogRetention=true
```

**Rollback** (no manual portal step; each is one command C8.3 names):

- Kill switch on (C8.1's path, and the first move for any doubt): step 5's command with `killSwitch=on`.
- Previous version: step 5's command with `imageTag=<previous tag>`; the previous image stays in the registry (tags are never overwritten: the tag is the commit). With `activeRevisionsMode: 'Single'` this starts a revision of the previous image, which is how this spec meets C8.3's "activate the previous revision"; `az containerapp revision activate` needs the CLI extension the plan does not use (P10).
- Before step 3 nothing is public; a failed step 1 or 2 is re-run, nothing to undo.
- Removing the resources is only on the owner's word (C8.3); the commands are in the runbook (stage 15), not run by the slice.

## 8. Cost model and cold start (estimates; stage 18 measures)

**Per question (Anthropic), estimate.** Input: system prompt ≈ 640 characters ≈ 150 tokens; payload measured at 7,967 to 9,323 characters on two real questions (`runs/docs-answerability-2/01-measurement.md`, `05a-smoke.md`; those figures include a ~140-character skill line) ≈ 2,000 to 2,400 tokens at ~4 characters a token; framing ≈ 20. Total ≈ 2,200 to 2,600 input tokens. Output: one line ≈ 15 to 30 tokens. At $3 / $15 per MTok **(U, price recalled for earlier Sonnet models, not read for `claude-sonnet-5-5`)**: 2,600 × 3e-6 + 30 × 15e-6 ≈ **$0.008 a question** (range $0.007 to $0.009). If high effort adds unseen reasoning tokens (U), each 500 adds $0.0075.

| Figure | Value |
|---|---|
| Daily share | $10 / 31 = $0.3226 (cap `322,580,645` nano-dollars) |
| Reservation per question (admission headroom) | ≈ (9,500 + 640 + 64) × $3e-6 + 1,024 × $15e-6 ≈ $0.046 |
| Expected capacity | ≈ 35 judged questions a day (≈ 40 by spend, less the last reservation's headroom); ≈ 19 a day if reasoning adds 500 output tokens |
| Gate + verification | ≈ 25 judged questions ≈ $0.20: fits one day's share by spend; the 10-an-hour limit sets the batches (C8.5) |

**Azure, monthly, (U) all from memory of list prices, none read:** Container Registry Basic ≈ $5 (≈ $0.167/day, the largest line); Container Apps consumption with scale to zero ≈ $0 to $5 (each wake keeps a 0.5 vCPU / 1 GiB replica up for the ~300 s cooldown; 40 wakes a day ≈ 180k vCPU-s and 360k GiB-s a month, about the per-subscription free grant); Log Analytics < 0.1 GB/month ingestion ≈ $0 (first 5 GB per billing account free); Key Vault reads ≈ $0. **Total ≈ $5 to $10 a month.** The owner confirms from Cost Management at the end review.

**Cold start, (U), measured at stage 18:** from zero, image pull (~0.45 GB, node cache unknown) + Python imports + index load + ONNX load (~1 s on a laptop) + `Searcher` build. Expect 10 to 30 s for the first request after idle; then `retrieve` ≈ 1 s plus the model call (≈ 2 to 5 s, (U)). The page's long-wait state at 8 s covers it (UX §4). `minReplicas` stays 0 as C8.3 says; `minReplicas: 1` is an owner choice at the end review (it also fixes §3.4, at the cost of an always-on replica).

## 9. New runtime dependencies (Backend adds all three at stage 8; Security reviews `uv.lock`)

| Package | Pin | Why | Brings (transitive, (U) beyond what local metadata shows) | Cost |
|---|---|---|---|---|
| `fastapi` | exact version `uv` resolves; 0.142.2 is the newest seen installed locally | ADR 0001's HTTP layer: routing, request objects, TestClient | `starlette`, `pydantic`, `typing-extensions`, `typing-inspection`, `annotated-doc`, **`opentelemetry-api`** (an API with no exporter; Security confirms no `opentelemetry-sdk` or exporter is in `uv.lock`) | a listening surface; request bodies are parsed by hand, not by pydantic models, so no validation error echoes input into a response |
| `uvicorn` (plain, **not** `[standard]`) | 0.54.0 seen locally | the ASGI server in the container | `click`, `h11` | no uvloop/httptools/watchfiles/dotenv |
| `anthropic` | `==1.7.0` (§2.4) | the Messages API client; ADR 0001: "Anthropic's SDK called directly" | `anyio`, `docstring-parser`, `httpx2`, `jiter`, `pydantic`, `sniffio`, `typing-extensions` | the only egress path; its logger silenced (§5) |

Deliberately **not** added: `python-multipart` (form parsed with `urllib.parse`), `jinja2` (`string.Template` + `html.escape`), any `azure-*` SDK (the platform resolves the Key Vault reference; the program makes no Azure call), `httpx` at runtime. **Dev group only:** `httpx`, if the resolved `starlette`'s `testclient.py` imports it (Backend checks after `uv sync`; (U)); it is not in the image (`--no-dev`).

## 10. Test plan (all in the default offline suite; the autouse network block stays; no live call before stage 17)

Fakes: `tests/service_fakes.py` (Backend) holds `FakeJudgeClient` (records every `(system_prompt, payload)`, returns a scripted `JudgeCall` or raises), a call-counting `Searcher` spy, a fixed clock, and an index built with `conftest.FakeEmbedder`. The real `AnthropicJudgeClient` is exercised only with an injected fake `messages.create`, or with a real SDK client whose socket the autouse block refuses.

| File (owner) | Tests |
|---|---|
| `tests/test_service_pipeline.py` (Backend) | `test_service_passages_byte_identical_to_retrieve` (every file and passage, in order: path, heading, lines, url, and `text.encode()` equal to `retrieve(searcher, normalise_question(q))`'s); `test_payload_sent_is_format_judge_input_of_same_result`; `test_not_answerable_is_exactly_no_confident_match`; `test_judge_error_shows_nothing` (malformed, wrong id, two tokens, control char, empty, each transport category, `PayloadMarkerError`); `test_reason_never_leaves_parser_service` (reply `Q1 ANSWERABLE <canary>`: canary absent from JSON, HTML, result store, logs); `test_unusable_question_no_model_call`; `test_core_files_unchanged` (sha256 of `aveto_support/*.py`, `prompts/answerability-judge-v1.txt`, `docs-source.toml`, `.claude/agents/aveto-answerability-judge.md`, both judge skills, `.claude/hooks/*`, recorded from `git show 2919c87:<path>` at stage 8); `test_aveto_support_imports_no_service_deps` (AST over every `aveto_support/*.py`: no `anthropic`, `fastapi`, `starlette`, `uvicorn`, `httpx`, `httpx2`, `aveto_service`) |
| `tests/test_service_limits.py` (Backend) | `test_each_limit_fails_closed_no_model_call` (parametrised over §3 steps 1 to 7: fake judge call count 0, and 0 retrievals for steps 1 to 5); `test_kill_switch_on_refuses_before_body`; `test_kill_switch_unparsable_means_on`; `test_question_500_accepted_501_refused` (code points, combining marks, emoji, CRLF); `test_body_over_cap_refused`; `test_rate_limit_eleventh_refused`; `test_rate_limit_counts_judge_errors_not_refusals`; `test_client_key_rightmost_xff` (forged leftmost ignored, IPv6 /64, mapped IPv4, invalid → peer, `ASK_CLIENT_KEY=peer`); `test_client_key_store_full_fails_closed`; `test_spend_pause_closes_day`; `test_spend_reservation_bounds_and_settles` (failed attempt keeps `R`); `test_spend_resets_at_utc_midnight`; `test_concurrent_admissions_never_exceed_cap` (threads) |
| `tests/test_service_logging.py` (Backend) | `test_question_never_logged` (canary in the question through every outcome, incl. a fake judge raising with the question in its message, a retrieval error carrying it, the 413 path, and `anthropic` logger forced to DEBUG first; `capfd` + root `caplog`; canary, its JSON- and URL-escaped forms and its first 12 characters absent; every stdout line matches the abuse or ops regex exactly); `test_abuse_line_shape_exact`; `test_library_loggers_silenced` |
| `tests/test_service_api.py` (Backend) | `test_ask_json_contract` (exact key set per outcome, status codes, no `Retry-After`); `test_health_never_calls_model`; `test_no_set_cookie_and_security_headers`; `test_startup_fails_closed_on_prompt_hash_mismatch`; `test_placeholder_judge_when_no_key` |
| `tests/test_anthropic_judge.py` (AI Engineer) | `test_request_has_no_tools` (no `tools`, `tool_choice`); `test_request_body_only_c41_data` (keys exactly `model, max_tokens, system, messages, output_config`; `system` = the prompt file's text; one user message = the payload; a canary IP, header and user agent given to the pipeline appear nowhere in the serialised request); `test_request_model_and_effort_pinned`; `test_extract_reply_text_blocks_only` (thinking dropped; tool_use → error); `test_stop_reason_not_end_turn_is_judge_error`; `test_sdk_errors_map_to_fixed_categories` (exception text with the payload is dropped); `test_retry_once_only_on_retryable`; `test_no_retry_on_timeout`; `test_real_client_blocked_offline` (real SDK client, dummy key: `JudgeTransportError`, the socket guard hit, no sleep via injected backoff) |
| `tests/test_service_pages.py` (Frontend) | `test_every_state_renders` (UX §4's exact `<h2>` per state); `test_passages_escaped_verbatim` (a passage holding `<script>` shows as text; unescaped text equals `Passage.text`); `test_form_post_after_model_call_redirects_303`; `test_form_post_refusal_renders_with_text`; `test_result_store_holds_no_question`; `test_question_never_in_url_or_title`; `test_kill_switch_page_loads_with_off_state`; `test_no_external_resources` |
| `tests/test_infra_static.py` (Backend Architect, stage 11c; §12) | `test_bicep_resources_are_c83`; `test_bicep_scale_and_ingress` (`minReplicas: 0`, `maxReplicas: 1`, `external: true`, `allowInsecure: false`, single revision); `test_bicep_kill_switch_default_on`; `test_bicep_no_secret_literals` (the key only as a Key Vault reference); `test_dockerfile_static` (non-root `USER`, no key, no `--with-reranker`, uvicorn flags of §6); `test_dockerignore_excludes_models_index` |

Unchanged and still green: all 425 existing tests, including `test_judge_modules_import_allow_list` and `test_program_offline_no_model`. Commands: `uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`. Stage 11 adds `az deployment group what-if` output; no live API call before stage 17.

## 11. Safety-text bounds for the Tech Writer (stage 15; Security checks at 14, Release Manager diffs at 16)

Facts only; the Tech Writer writes the words. Nothing outside these bounds changes; INV-1, INV-2, INV-3 are untouched (C5.3).

**INV-4 (C5.1).** Replace only the sentence "it runs only in the operator's own Claude Code session, and nothing in the program calls it" with words naming exactly two callers:
1. the operator's own Claude Code session (as now);
2. the service's `POST /ask` (package `aveto_service`, not the program `python -m aveto_support`), which calls the Anthropic Messages API with `claude-sonnet-5-5`, no `tools` in the request, system prompt `answerability-judge-v1` at sha256 `24b244d2…9427` (checked at startup; the service refuses to start on a mismatch), the user content being `judge-input`'s payload for the question, and the same verdict-only parser (`parse_verdict`: the last non-empty line, token only).

May add the JSON mapping: (a) `outcome: "answer"` with the files and passages of the same `retrieve` result at the default ranking, each passage's full verbatim text with path, heading, line range and permalink, no scores, plus the deciding-signal line; (b) `outcome: "no_confident_match"`, `text: "no confident match"` and the signal line, nothing else; (c) `outcome: "judge_error"`, `text: "judge error"`, nothing else, for any unusable reply, API error, timeout, stop reason other than `end_turn` or tool-use block. **Must state accurately** that (a) shows the passages in full where `judge-apply`'s CLI text shows an excerpt. May add the new test names: `test_service_passages_byte_identical_to_retrieve`, `test_payload_sent_is_format_judge_input_of_same_result`, `test_reason_never_leaves_parser_service`, `test_judge_error_shows_nothing`, `test_not_answerable_is_exactly_no_confident_match`, `test_request_has_no_tools`, `test_request_model_and_effort_pinned`, `test_stop_reason_not_end_turn_is_judge_error`, `test_extract_reply_text_blocks_only`.

**INV-5 (C5.2).** Add one exception, for the service alone: an HTTPS POST to `api.anthropic.com` (`/v1/messages`), at most two attempts per question, carrying only the C4.1 data (the fixed judge prompt, the question of at most 500 characters, and the passages `retrieve` would show with their paths, headings and line ranges, i.e. `judge-input`'s payload), authenticated by the key the container reads from Key Vault `kv-aveto-ask-gp` (secret `anthropic-api-key`, resolved by Container Apps through the user-assigned identity). No IP address, visitor identifier or visitor request header. **Security must rule at 14** whether the request's protocol fields (`model`, `max_tokens`, `output_config.effort`) and the SDK's own headers (`x-api-key`, `anthropic-version`, `user-agent`, `x-stainless-*` platform facts) fall inside "only the data in C4.1"; they carry nothing about the visitor. Every other INV-5 sentence stays; the service's index and model come from `ingest`'s existing (a)/(b) GETs at image build time. May add: `test_request_body_only_c41_data`, `test_real_client_blocked_offline`, `test_aveto_support_imports_no_service_deps`, `test_question_never_logged`, `test_each_limit_fails_closed_no_model_call`.

## 12. Work split (no file has two owners)

**Amendment 2026-10-21 (SR-1).** Cloud Deployment is write-scoped to `runs/`, `.azure/`, `infra/`, `azure.yaml` and has no shell, so this table could not assign it `Dockerfile`, `.dockerignore`, `tests/test_infra_static.py` or any `az` command. Ownership moves as below: `Dockerfile`, `.dockerignore`, `tests/test_infra_static.py` and the read-only Azure checks go to the Backend Architect at stage 11c (has Bash); Cloud Deployment keeps `infra/*`; stage 17's §7 commands are run by the Orchestrator's session under C8.3. This supersedes the owner named for `Dockerfile` and `.dockerignore` in the §1 file table and the §6 heading. Nothing else in the spec changes: §6's image content, §7's resources, parameters, commands and rollback, and §10's test names stand as written.

| Stage, role | Owns (creates or edits) | Reads, never edits |
|---|---|---|
| 8 Backend Architect | `pyproject.toml`, `uv.lock`; `aveto_service/{__init__,settings,judge_port,html_port,limits,abuse_log,pipeline,app}.py`; `tests/service_fakes.py`, `tests/test_service_{pipeline,limits,logging,api}.py` | `aveto_support/`, `prompts/`, this spec |
| 9 AI Engineer | `aveto_service/anthropic_judge.py`; `tests/test_anthropic_judge.py` | `judge_port.py`, `abuse_log.py`, `tests/service_fakes.py` |
| 10 Frontend Developer | `aveto_service/{pages,render,result_store,main}.py`, `aveto_service/static/{enhance.js,style.css}`; `tests/test_service_pages.py` | `html_port.py`, `app.py`, `04-ux-spec.md` |
| 11 Cloud Deployment | `infra/main.bicep`, `infra/main.parameters.json`; fixes any `az bicep build` lint or `what-if` finding that 11c reports against them | everything above, `Dockerfile`, `.dockerignore`, `tests/test_infra_static.py`; runs no command (no shell) |
| 11c Backend Architect | `Dockerfile`, `.dockerignore`, `tests/test_infra_static.py` (starting from the hand-off text in `11-infra-note.md`, checked against §6 and §10). Runs read-only only: `az bicep build -f infra/main.bicep`; `az role definition list --name "Key Vault Secrets User" --query "[].name" -o tsv` and the same for `AcrPull` (§7); `az keyvault show -n kv-aveto-ask-gp --query properties.enableRbacAuthorization` (`false` is Charter stop 9.1, §7); `az acr check-name -n acravetoaskgp`; `az deployment group what-if` with §7's arguments; then `uv run mypy && uv run ruff check && uv run pytest`. Never `create`, `az acr build`, push, or any other state-changing command. Findings in `infra/*` go back to Cloud Deployment through its artefact, not edited here | `infra/*`, this spec, `11-infra-note.md` |
| 17 Orchestrator's session (shell) | runs §7's commands 1 to 5 and the rollback commands under C8.3, from `11-infra-note.md` as the runbook; edits no file | `infra/*`, `Dockerfile`, this spec |
| 15 Tech Writer | `.agentic/SAFETY_INVARIANTS.md` (§11 bounds), `README.md`, `.agentic/CURRENT_MVP_STATUS.md`, `docs/ARCHITECTURE.md`, `docs/runbooks/public-ask.md` (commands from §7, UTC reset, retention check) | this spec, ADR 0009 |

If a stage finds the spec wrong, it records the finding in its artefact and the Orchestrator routes it back here; it does not edit another role's file.

## Risks and open items (for the Orchestrator)

1. **§3.4 counters reset with the replica** (scale to zero, kill-switch toggles). Not fixable inside C8.3; owner decision at the end review; Security rules at 14.
2. **§4 "without a redeploy"**: met as "no build, same image"; not met as "no new revision".
3. **Possible STOP at stage 11** if `kv-aveto-ask-gp` is not in RBAC mode (§7).
4. **(U) items that change behaviour, all checked before the gate:** the effort field accepted for `claude-sonnet-5-5` (stage 17 first call); the price (owner); the ingress's `X-Forwarded-For` handling (stage 17 forged-header check); table retention below 30 days (stage 17 read-back).
5. The API judge runs without the harness context the attended judge saw; the public gate measures this judge, not the attended one.
