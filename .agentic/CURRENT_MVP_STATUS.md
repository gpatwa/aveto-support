# Current MVP Status

## What exists (retrieval from docs-retrieval-core; judge step merged in pull request #4; public service deployed from branch `claude/public-ask-the-docs`, gate scored once)

- **Public service (slice `public-ask-the-docs`): deployed on Azure Container
  Apps (East US 2) and answering at
  `https://ca-aveto-ask.salmonsmoke-fa1fa863.eastus2.azurecontainerapps.io`; gate
  scored once. The branch is not merged. The address is recorded here and in the
  runbook only; it is not linked from aveto.dev (a separate later change, on the
  owner's word). The release verdict is the Release Manager's and is not stated
  here.** Package `aveto_service` (FastAPI): `POST /ask`, `GET /health`
  and a public page at `GET /`. It runs the unchanged retrieval and judge prompt
  and returns either verbatim passages (full text, with path, heading, line range
  and permalink, no scores) or `no confident match`, or `judge error` with no
  passage. The model decides only whether the passages answer; no generated text
  is shown. It calls the Anthropic Messages API with `claude-sonnet-5-5` and no
  tools, through an `anthropic` SDK client, from the service only (the program
  `python -m aveto_support` still makes no model call). What the request carries,
  including the SDK's own headers, and the two exceptions (the operator's session
  and this service) are stated in [INV-4 and INV-5](SAFETY_INVARIANTS.md). Limits in code: 10
  judged questions per visitor per hour, 500 characters, a daily share of $10 a
  month (`10 / 31` a day, UTC reset), a kill switch (default on), all refusing
  before any model call; counters live in memory and restart with the replica. No
  question is stored or logged; abuse lines hold a time, a hashed address prefix
  and an outcome code. Also in the tree: `Dockerfile`, `infra/main.bicep` (Azure
  Container Apps, scale 0 to 1, resource group `rg-aveto-ask`), runbook
  `docs/runbooks/public-ask.md`. Recorded checks: 606 tests passed on the QA
  run (`runs/public-ask-the-docs/13-qa-evidence.md`) and Security review verdict
  PASS WITH REQUIRED FIXES (`14-security-review.md`; later rounds recorded in the
  git history). The image is built and deployed (revision `ca-aveto-ask--0000006`,
  image `aveto-ask:879cae23690b` at the gate). The attended `/aveto-judge` path
  below is unchanged and is still attended and internal; only the public service
  is no longer described that way.
  - **Gate, scored once** (`evals/public-gate-1.toml`, sha256 `7eb4f588…064f`,
    committed after the method froze; 20 questions; record in
    `runs/public-ask-the-docs/18-gate/RESULT.md`): Bar 1 **10 of 10** (all
    unanswerable and hostile questions got `no confident match`, no passage);
    Bar 2 **8 of 10** (needed 8), met exactly at the bar. **The margin is zero**,
    the set is small, and over-abstention is 2 of 10 answerable (p06, p09). This
    is a measurement, not a capability claim. Judge errors 0 in 20 calls. Answerable
    sources overlap earlier sets' files (may flatter Bar 2). S-A5 (invisible-character
    injection) not covered; no stronger live attack was run.
  - **Recorded figures:** cost per judged question about $0.0079 at Anthropic's
    published prices for `claude-sonnet-5-5` ($2 and $10 per million tokens,
    confirmed 2026-10-23 from the live pricing page and models overview; $0.1569
    for 20, recomputed from 71,151 input and 1,460 output tokens; the first live
    question $0.0099). The service's counter, at its built-in $3 and $15, reads
    50% high ($0.2354 for the same 20), a safe error. About 1,270 questions a
    month fit in the $10 console limit; the service's daily pause comes at about
    27 questions a day by its counter (about 41 at the real price). The tech spec
    had estimated $0.008; response time median 1.66 s, 90th percentile 4.14 s,
    slowest 5.09 s (n = 20, from one client, a Mac, to East US 2); cold start 30.8 s
    to the first `/health` answer from zero replicas after more than an hour idle.
  - **Live checks:** first answered call succeeded after the key was stored again
    with whitespace stripped (HTTP 200, 9 passages, 1.83 s; an earlier first call
    ended in `judge error`, cause probable, not proven); the 9 live passages equal
    local `retrieve` text, line ranges and links byte for byte (M3); log retention
    read back 7 and 7 for the two tables; kill-switch change took 65 s (on) and 66 s
    plus about 6 s for traffic to shift (off); S-C1 passed with the owner's phone
    on cellular (two networks gave two different hashed addresses; forged headers
    on one network gave one); the first live question's words appear in no log table
    (G5). The previous-image rollback was not rehearsed.

- `ingest`: downloads the markdown of the configured repo at its pinned commit
  (one read-only HTTPS archive fetch), splits it into passages at headings,
  embeds each passage with a local model, and writes a deterministic index file
  (`index/`, gitignored). On first run it also downloads two pinned model files
  from huggingface.co into `models/` (gitignored), each checked against its
  committed sha256 before use.
- `retrieve`: returns verbatim passages from the top five files with path,
  heading trail, line range and a permalink at the pinned commit, plus the top
  score. It never abstains: a question the docs do not answer still returns
  files. Ranking is hybrid: BM25 (Porter stemming, passage plus file evidence)
  fused with dense similarity by reciprocal rank fusion. The ingest-time
  reference similarity is printed for information and decides nothing.
- History: slice `docs-abstention` measured that no score-threshold or margin
  rule separates unanswerable from answerable questions on the seen sets, and a
  tried local judge model failed its seen-set check, so the owner stopped that
  path.
- Judge step (built in slice `docs-answerability-2`; merged in pull request #4,
  2026-10-17): `judge-input` and `judge-apply` (both offline, no model call) plus
  the `/aveto-judge` skill and the `aveto-answerability-judge` subagent
  (`claude-sonnet-5-5`, no tools offered). The operator runs it by hand in their
  own Claude Code session, attended only; `judge-apply` then prints either
  `retrieve`'s output or `no confident match`, or `judge error` (exit 4) on an
  unusable reply. It is a verdict on shown passages, not drafting: it writes no
  answer text. The question, shown passages, reply and session context go to
  Anthropic through that session ([INV-5](SAFETY_INVARIANTS.md)); the program
  does not. `retrieve` itself still never abstains.
- Recorded figures for the judge step, each scored once, judge errors 0 at both
  stages, tool-use audit clean (48 spawns each, 0 tools offered, 0 tool calls):
  - Stage 5 sample check (seen set): Bar 1 20/20 (needed 16/20); Bar 2 24/28
    (needed 23/28, one question of margin).
  - Stage 7 fifth set (held out): Bar 1 24/24 (needed 20/24); Bar 2 16/19 =
    84.2% (needed 80%, one question of margin).
  - Never abstain, fifth set: Bar 1 0/24. Best-score rule (`top1 < 0.67`): not
    met on both stages (stage 5: 13/20 and 17/28; stage 7: 10/24 and 13/19).
  - Over-abstention: 3 of 19 answerable questions (4 of 28 at stage 5).
  - Known limit, stated plainly: on the fifth set, retrieval put the right file
    in the top five for 19 of 24 answerable questions (79.2%, under its 80%
    bar; retrieval gate exit 1; not a registered bar of the judge slice), and
    16 of 24 ended with the right file shown after judging. The owner accepted
    this as a known limit (Charter C8.5, slice `land-answerability`). The bars
    above describe the eval path; the operator path (`/aveto-judge`) is
    unmeasured. This is not a capability claim.
  - Source files of the fifth set overlap earlier sets' (21 of 24 answerable
    questions); disclosed, may flatter Bar 2.
- Release tier 3 (the owner's ruling, `APPROVAL_RECORD-9` of slice
  `docs-answerability-2`, 2026-10-16). Slice `docs-answerability-2` closed as an
  internal release candidate; its conditions T1 to T11 are carried out by slice
  `land-answerability` (Charter approved 2026-10-17). **Merged by pull request #4
  (2026-10-17, a merge commit).** Not announced, no deploy, no unattended use. In that
  slice: S5 fixed (the operator writes the run id to `.aveto-judge/seen-id`,
  then runs `/aveto-judge-seen` with no argument; `/aveto-judge` unchanged); the
  S6 rule deleted (owner, 2026-10-16); monitoring thresholds, cadence and stop
  rules adopted as written, runbook in `docs/runbooks/answerability-judge.md`;
  the rollback rehearsed on a throwaway branch
  (`runs/land-answerability/02-rollback-rehearsal.md`). Operating rule
  (Charter C4.1): public-docs questions only until a DPA is in place (personal
  subscription, no DPA; retention and training use per that plan's public terms,
  not verified). A dry run on a fixture passed 11 of 11 criteria (no model ran
  in it); audit coverage passed with gaps G1 to G9. ADR 0008 stays
  Proposed. Limits: one model, one set, a small sample, one scored run; the
  judge adds a failure mode of over-abstaining on answerable questions.
  Nothing here claims production readiness.
- `eval`: scores retrieval against an eval file and exits non-zero below 80% on
  either group.
- The default ranking is `file-rrf-v1` (the first stage alone: hybrid dense and lexical
  rank fusion over all files). `--ranking file-rerank-v1` is opt-in: a local cross-encoder
  (`cross-encoder/ms-marco-MiniLM-L6-v2`, ONNX, CPU) re-scores the top 20 files' shown
  passages (MaxP) and orders them; it needs `ingest --with-reranker` first. Recorded
  scores: `file-rrf-v1` 14/16 on the fourth held-out set (11/16 and 12/17 on earlier
  ones; 19/24 = 79.2% on the dev set, below the 80% bar); `file-rerank-v1` 13/16 on the
  fourth. The reranker showed no demonstrated gain (slice 3 close-out).
- The models (`BAAI/bge-small-en-v1.5` and the reranker, ONNX, CPU) only rank. They never
  write or alter text. The program never sends a question anywhere; `retrieve` and
  `eval` are offline. (The operator-run judge step sends to Anthropic through the
  operator's own session; see above.)
- Runtime dependencies: `onnxruntime` and `numpy` only.

## Not yet done

- **Public service (slice `public-ask-the-docs`):** the release verdict is the
  Release Manager's and is not stated here. **Not measured:** the monthly Azure
  cost (Azure's cost data lags about a day; no figure is stated), IPv6 clients
  (the service has no AAAA record), a screen reader, real visitors and adversarial
  load, the previous-image rollback. Price confirmed (see recorded figures). Open
  item: set the service's price env values to 2000 and 10000
  (`ASK_PRICE_IN_NANO_PER_TOKEN`, `ASK_PRICE_OUT_NANO_PER_TOKEN`) if the owner
  wants the counter exact; a parameter change on redeploy, not done, the owner's
  call. The `effort` field is accepted
  (the owner's direct test and the first live call). Open owner decisions from
  the Security review (D1 to D7): D1 the daily pause holds per replica lifetime, so an
  attacker could use the month's $10 in hours; D2 what to do if the ingress
  address is not per client; D3 whether to reduce the public `/health` after the
  gate; D4 about 40 questions from a few addresses pause the service for everyone
  until 00:00 UTC; D5 Azure spend is outside the $10: partly answered on 2026-10-23, a budget alert
  now exists (`bud-aveto-ask`, $20 a month, resource group `rg-aveto-ask`,
  notifies the Owner role at 50%, 80%, 100% actual and 100% forecast, created by
  hand, not in `infra/main.bicep`) but it only notifies and no cap exists;
  D6 the identity can read every secret in the vault; D7 the console limit rests
  on the owner's word. Linking the page from aveto.dev is not done.
- Tier 3 is ruled (owner, 2026-10-16). The remaining tier 3 items are carried
  by slice `land-answerability`; the Release Manager's landing verdict is theirs
  to issue and is not stated here. Open or UNKNOWN as recorded:
  - The merge is the owner's own act; the pull request does not merge itself.
  - Anthropic's DPA is not in place (personal subscription); retention,
    training use, subprocessors, certifications and residency are UNKNOWN
    (`runs/docs-answerability-2/11b-vendor-risk.md`). The operating rule above
    is a policy control the repo cannot enforce.
  - The operator path `/aveto-judge` has never been measured.
  - Three Security probe scripts exempt themselves from lint (D6, which the
    owner acknowledged).
- One model-marked test fails in the committed tree
  (`test_sample_derivation_reproducible`; the frozen test compares the whole key
  file, which gained rows after the freeze). A later slice must change it.
- Retrieval has not passed its held-out gate as a released feature; nothing is
  released, announced or deployed, no answers are generated, and the attended
  judge step is not unattended, not a service and not wired to any drafter. (The
  public service is a separate, deployed path; see above.)
- (Resolved, for the record: `tests/fixtures/wordpiece_golden.json` exists; the
  earlier line saying it was missing was stale.)

## Out of scope (not built)

- Any generative model call by the program `python -m aveto_support`: classify,
  draft, check. (The operator-run judge step above is outside the program,
  returns only a verdict, and is not drafting. The `aveto_service` package, built
  on branch `claude/public-ask-the-docs`, makes one verdict-only model call per
  admitted question; that is the service, not the program, and it is deployed.) Generated answers and drafting are not built anywhere.
- A database, accounts or sign-in for visitors, multi-turn chat, a custom domain.
  (The HTTP surface exists as `aveto_service`; it is deployed from the branch
  above and is not on `main`.)
- CI: arrives with `docs-retrieval-ci`.
- Anything that posts to GitHub.
