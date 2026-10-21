# Current MVP Status

## What exists (retrieval from docs-retrieval-core; judge step merged in pull request #4; public service built on branch `claude/public-ask-the-docs`; nothing deployed)

- **Public service, built on branch `claude/public-ask-the-docs` (slice
  `public-ask-the-docs`); not merged, not deployed, no live model call made, no
  figure measured.** Package `aveto_service` (FastAPI): `POST /ask`, `GET /health`
  and a public page at `GET /`. It runs the unchanged retrieval and judge prompt
  and returns either verbatim passages (full text, with path, heading, line range
  and permalink, no scores) or `no confident match`, or `judge error` with no
  passage. The model decides only whether the passages answer; no generated text
  is shown. It calls the Anthropic Messages API with `claude-sonnet-5-5` and no
  tools, through an `anthropic` SDK client, from the service only (the program
  `python -m aveto_support` still makes no model call). Limits in code: 10
  judged questions per visitor per hour, 500 characters, a daily share of $10 a
  month (`10 / 31` a day, UTC reset), a kill switch (default on), all refusing
  before any model call; counters live in memory and restart with the replica. No
  question is stored or logged; abuse lines hold a time, a hashed address prefix
  and an outcome code. Also in the tree: `Dockerfile`, `infra/main.bicep` (Azure
  Container Apps, scale 0 to 1, resource group `rg-aveto-ask`), runbook
  `docs/runbooks/public-ask.md`. Recorded checks: 606 tests passed on the QA
  run (`runs/public-ask-the-docs/13-qa-evidence.md`) and Security review verdict
  PASS WITH REQUIRED FIXES (`14-security-review.md`; later rounds recorded in the
  git history). The image has never been built and the Bicep has not been
  deployed; the read-only Azure checks are in `11c-infra-checks.md`. The attended
  `/aveto-judge` path below is unchanged and is still attended and internal.

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
  Release Manager's and is not stated here. Not yet measured (stage 18): cost per
  question, median and slowest response time, cold-start time, monthly Azure cost,
  the 20-question gate result. Not yet run: the image build, the deploy, the
  stage 17 checks (S-C1: the client address behind the ingress, with the kill
  switch on; S-C2: both log tables read back 7 and 7; S-C3: build from the
  worktree root only), and the first live call (which settles whether the
  `effort` field is accepted for `claude-sonnet-5-5`). Open owner decisions from
  the Security review: D1 the daily pause holds per replica lifetime, so an
  attacker could use the month's $10 in hours; D2 what to do if the ingress
  address is not per client; D3 whether to reduce the public `/health` after the
  gate; D4 about 40 questions from a few addresses pause the service for everyone
  until 00:00 UTC; D5 Azure spend is outside the $10 and no budget alert exists;
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
  public service on the branch is a separate, undeployed path; see above.)
- (Resolved, for the record: `tests/fixtures/wordpiece_golden.json` exists; the
  earlier line saying it was missing was stale.)

## Out of scope (not built)

- Any generative model call by the program `python -m aveto_support`: classify,
  draft, check. (The operator-run judge step above is outside the program,
  returns only a verdict, and is not drafting. The `aveto_service` package, built
  on branch `claude/public-ask-the-docs`, makes one verdict-only model call per
  admitted question; that is the service, not the program, and it is not
  deployed.) Generated answers and drafting are not built anywhere.
- A database, accounts or sign-in for visitors, multi-turn chat, a custom domain.
  (The HTTP surface exists on the branch above as `aveto_service`; it is not
  deployed and is not on `main`.)
- CI: arrives with `docs-retrieval-ci`.
- Anything that posts to GitHub.
