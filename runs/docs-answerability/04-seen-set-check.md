# 04 Seen-set check: run record (slice docs-answerability, standard depth)

Role: QA Evidence scorer. No judge was spawned, no product, test or safety file was edited. Written section by section.

## VERDICT

**FAIL. Pooled Bar 2 is 44/56, below the 45/56 threshold (NOT MET). Pooled Bar 1 is 20/20 (MET).** The pooled denominators are exactly 20 and 56, so the check is valid. Pass required both bars. It fails by one answerable question. The fifth set was not read, looked for or touched.

**Stopped before the fifth set; owner decides.**

Pre-registered threshold (spec 5.4): pooled Bar 1 >= 16/20 AND pooled Bar 2 >= 45/56, JUDGE_ERROR counted as a failure on both.

## 1. Pooled and per-set bars (spec 5.5 item 1)

Produced by `uv run python -m aveto_support eval --eval-file <set> --verdicts seen-check/verdicts-<set>.toml` (outputs reproduced from the runs; each command exited 1, 1, 1, 0 for retrieval, heldout, heldout-3, heldout-4: the eval exit code is the existing retrieval gate, "bars reported, not gated here").

| set | unanswerable | Bar 1 | answerable with right file in top 5 | Bar 2 | judge errors |
|---|---|---|---|---|---|
| evals/retrieval.toml | 6 | 6/6 MET | 19 | 13/19 (68.4%) NOT MET | 0 |
| evals/retrieval-heldout.toml | 6 | 6/6 MET | 12 | 11/12 (91.7%) MET | 0 |
| evals/retrieval-heldout-3.toml | 4 | 4/4 MET | 11 | 9/11 (81.8%) MET | 0 |
| evals/retrieval-heldout-4.toml | 4 | 4/4 MET | 14 | 11/14 (78.6%) NOT MET | 1 |
| **pooled (sum of the four `bars:` lines)** | **20** | **20/20 (100%) MET (>= 16/20)** | **56** | **44/56 (78.6%) NOT MET (>= 45/56)** | **1** |

`bars:` lines as printed: `unanswerable_abstained=6/6 answerable_hit_not_abstained=13/19 judge_errors=0`; `6/6 11/12 0`; `4/4 9/11 0`; `4/4 11/14 1`. Denominators: 20 unanswerable and 56 answerable-with-hit, as registered. No rescaling.

Verdict mix over all 93: 52 ANSWERABLE, 40 NOT_ANSWERABLE, 1 JUDGE_ERROR.

## 2. Judge errors (item 2)

Under the final grammar (last non-empty line, optional colon) there is **one** judge error: **r093**, batch 6, set retrieval-heldout-4 (f13), category 4.2 "malformed verdict line": the reply was two paragraphs and its last non-empty line was a "Note:" paragraph, which does not match the line grammar. `judge-apply` exit 4 (per the ledger; I treat r093 as JUDGE_ERROR on the ledger's stated exit code and last line, the full reply is in the transcript copy and re-parses as malformed). It counts as a failure on both bars and is one of the 12 bar-relevant differences below. Had it been ANSWERABLE, pooled Bar 2 would be 45/56 (a pass); it was not, and this is not a rescoring.

Rescued by the re-registered grammars (rows that would not have parsed under the grammar they replaced; counted from the ledger's replies, not re-run):

| rescued by | rows | detail |
|---|---|---|
| colon rule (APPROVAL_RECORD-9): `Q1 <TOKEN>:` | 20 | r002, r003, r004, r005, r006, r008, r019, r035, r047, r049, r056, r064, r066, r070, r072, r078, r082, r086, r087, r088. Per batch: 1: 6, 2: 1, 3: 2, 4: 2, 5: 5, 6: 4. |
| last-line rule (APPROVAL_RECORD-10): earlier lines ignored | 5 | **r010** (observed exit 4 under the previous grammar, now ANSWERABLE; key t14 answerable), **r012** (observed exit 4, now NOT_ANSWERABLE; key hu02 unanswerable), and r046 (a14), r051 (t12), r077 (h14), which were multi-line replies produced and parsed first under the new grammar; under the previous one-line grammar they would have been `more than one line` errors (inferred, never run). |

r010 and r012 (batch 1) are the only two rows whose recorded ledger exit code (4) disagrees with the final result; their `outcomes-all.toml` entries carry the re-applied verdict and exit 0, with a comment in the file. Bar effect of the five last-line rows: r010 (t14) counts as correct on Bar 2, r012 (hu02) as correct on Bar 1, r046 (a14) is a Bar 2 miss, r051 (t12) and r077 (h14) are answerable questions whose right file is not in the top 5 (n/a for the bars).

## 3. Hard negatives, end to end, never-abstain (item 3)

- Hard negatives abstained: the product's per-set line prints `0/0` for all four sets because the eval files store `hard_negative` as an explanatory string and the loader counts only `hard_negative = true` (`evaluate.py:88`). Counted from the key instead: **5/5 abstained** (r059, r067, r068, r087, r092 all NOT_ANSWERABLE). Diagnostic only.
- End to end (answerable questions whose right file is shown after judging, diagnostic): 13/24, 11/17, 9/16, 11/16, **pooled 44/73 (60.3%)**. The 17 answerable questions whose right file is not in the top 5 are not in Bar 2: 9 got NOT_ANSWERABLE, 8 ANSWERABLE.
- Never abstain (today), same sets: Bar 1 **0/20**, Bar 2 **56/56**.

## 4. Verdicts that differ from the key, with the judge's reply (item 4; run record only)

Twelve bar-relevant differences (answerable, right file in top 5, verdict not ANSWERABLE): 11 NOT_ANSWERABLE and 1 JUDGE_ERROR. Zero unanswerable questions differ. For r046 and r093 the ledger abbreviates the reply; the full reply below is from the judge transcript copy.

### retrieval a06 = r047 (batch 3), verdict NOT_ANSWERABLE

Question: Do I have to go through market research and a PRD for a small, clear feature?

Judge reply:

    Q1 NOT_ANSWERABLE: Passages say market research is optional and can be skipped, but nothing addresses whether a PRD is required.

### retrieval a07 = r038 (batch 3), verdict NOT_ANSWERABLE

Question: Which things will the agents never do without asking me first?

Judge reply:

    Q1 NOT_ANSWERABLE The passages describe how to ask for approval and say to ask when in doubt, but never list the actions that need it.

### retrieval a09 = r014 (batch 1), verdict NOT_ANSWERABLE

Question: How does it stop a run from burning through too many tokens?

Judge reply:

    Q1 NOT_ANSWERABLE names a pre-spawn budget check and per-stage budgets, but not what happens when the budget is exceeded.

### retrieval a14 = r046 (batch 3), verdict NOT_ANSWERABLE

Question: Can I use this with Cursor or Codex instead of Claude Code?

Judge reply:

    Q1 ANSWERABLE. Passage 1a names Cursor and Codex as AGENTS.md-aware tools, and passage 4b says a second adapter could run the pack on another runtime. Neither passage states that Cursor or Codex can drive the autonomous run in place of Claude Code, so this is an inference.
    
    Hmm, on reflection that is closer to NOT_ANSWERABLE: the passages say Cursor and Codex read AGENTS.md, but they do not say the autonomous run works with them. Correcting my answer:
    
    Q1 NOT_ANSWERABLE Passages name Cursor/Codex only as AGENTS.md readers; run support is not stated.

### retrieval a19 = r020 (batch 2), verdict NOT_ANSWERABLE

Question: Which kinds of release get the most checks before going out?

Judge reply:

    Q1 NOT_ANSWERABLE The passages mention release tiers 1-3 but never say which tier gets the most checks.

### retrieval a20 = r011 (batch 1), verdict NOT_ANSWERABLE

Question: Does it follow any security guidance written specifically for AI agents?

Judge reply:

    Q1 NOT_ANSWERABLE The passages only mention OWASP Agentic Top 10 in passing, and say the NIST agentic overlays are not yet mapped.

### retrieval-heldout h12 = r058 (batch 4), verdict NOT_ANSWERABLE

Question: I want to try two versions of a page and see which one does better. How should I set that up?

Judge reply:

    Q1 NOT_ANSWERABLE Passages only mention experiment readouts, not how to set up a page A/B test.

### retrieval-heldout-3 t03 = r065 (batch 5), verdict NOT_ANSWERABLE

Question: Where do I describe what a trained model is for and where it shouldn't be used?

Judge reply:

    Q1 NOT_ANSWERABLE Passages cover training data and reproducibility, not intended use or out-of-scope use.

### retrieval-heldout-3 t16 = r084 (batch 6), verdict NOT_ANSWERABLE

Question: What are the everyday working rules the agent team follows?

Judge reply:

    Q1 NOT_ANSWERABLE The passages only describe the rules as existing ("the set of rules that keep work small") or cover one role's constraints, without listing the team's everyday rules.

### retrieval-heldout-4 f03 = r032 (batch 2), verdict NOT_ANSWERABLE

Question: How do I work out what a new feature will cost to run each month?

Judge reply:

    Q1 NOT_ANSWERABLE Passages name cost fields and volume inputs but never state how to compute monthly cost.

### retrieval-heldout-4 f13 = r093 (batch 6), verdict JUDGE_ERROR

Question: Which agent hands out the work to all the others during a run?

Judge reply:

    Q1 ANSWERABLE. Passage 1a says the Orchestrator translates asks into slices and holds the only conversation with the human; 1b and the Claude Code section describe how stages are delegated to roles.
    
    Note: the passages establish the Orchestrator's role and that it delegates stages, but the explicit phrase "hands out the work" is inferred from "delegates each stage to a role" in the Claude Code specifics and the Orchestrator description, so the wording of passage 1a alone does not state delegation.

### retrieval-heldout-4 f14 = r064 (batch 5), verdict NOT_ANSWERABLE

Question: Is there guidance for selling to large companies that need SSO and audit trails?

Judge reply:

    Q1 NOT_ANSWERABLE: the passages cover engineering requirements (SSO, audit export) and when to use the enterprise pack, not guidance on selling to large companies.

## 5. Verdicts on answerable questions whose right file was not in the top 5, judged NOT_ANSWERABLE (not part of the bars)

These differ from the key's `answerable = true` label but the bars do not count them; listed for completeness (9 of 17).

### retrieval a01 = r033 (batch 3), verdict NOT_ANSWERABLE

Question: How do I add Aveto to a project I already have?

Judge reply:

    Q1 NOT_ANSWERABLE The passages cover first-time deployment setup, slice commands and the run guide, but none say how to add Aveto to an existing project.

### retrieval a16 = r015 (batch 1), verdict NOT_ANSWERABLE

Question: How should we write down why we picked one database over another?

Judge reply:

    Q1 NOT_ANSWERABLE Passages cover budgets, depth tiers, and approvals, not recording database choice rationale.

### retrieval-heldout h05 = r044 (batch 3), verdict NOT_ANSWERABLE

Question: How can I see where a run is at without reading all its files?

Judge reply:

    Q1 NOT_ANSWERABLE Passages cover handoff checks and context discipline, never how to view run status.

### retrieval-heldout h13 = r089 (batch 6), verdict NOT_ANSWERABLE

Question: Are there targets for how fast and how reliably the process itself should run?

Judge reply:

    Q1 NOT_ANSWERABLE Passages give token budgets and product SLOs, not process speed or reliability targets.

### retrieval-heldout-3 t04 = r037 (batch 3), verdict NOT_ANSWERABLE

Question: We want to start using an outside service. How do we check whether it's safe to rely on?

Judge reply:

    Q1 NOT_ANSWERABLE Passages cover post-deploy checks and SRE duties, not vetting an outside service.

### retrieval-heldout-3 t06 = r028 (batch 2), verdict NOT_ANSWERABLE

Question: Who talks to users to find out how they actually use the product?

Judge reply:

    Q1 NOT_ANSWERABLE The passages never name who researches real user behaviour; the UX Researcher is only referenced as a hand-off.

### retrieval-heldout-3 t12 = r051 (batch 4), verdict NOT_ANSWERABLE

Question: Who decides how risky an AI feature is and what rules it has to follow?

Judge reply:

    Q1 ANSWERABLE The passages name the ML Engineer, AI Engineer, FinOps, and EM roles, and the tier rules. But they don't state one owner for AI risk classification or a rulebook that covers all AI features, so this is a partial match and I judge it NOT_ANSWERABLE.
    
    Q1 NOT_ANSWERABLE passages cover related roles and constraints, but none states who decides how risky an AI feature is or its full rule set.

### retrieval-heldout-3 t13 = r019 (batch 2), verdict NOT_ANSWERABLE

Question: If a release needs sign-off from a change board, what do we fill in?

Judge reply:

    Q1 NOT_ANSWERABLE: passages cover release checklists and approvals but never mention a change board.

### retrieval-heldout-4 f04 = r040 (batch 3), verdict NOT_ANSWERABLE

Question: What do we tick off right before shipping, including how to undo it?

Judge reply:

    Q1 NOT_ANSWERABLE Passages cover end-user Undo for bulk delete, not a pre-ship checklist or its rollback.

## 6. Pilots' figures, a different configuration (item 5)

The pilots' Haiku figures on the same 93 questions were **Bar 1 20/20, Bar 2 47/56**. They are a different configuration: 12-16 questions per batch file, one Read of the batch file, the prompt placed where the pilot doc does not record, `haiku` alias, one Read allowed; whether the pilots had any harness prefix is not recorded. This check is one question per fresh judge spawn with zero tools and the 150-character harness prefix. Bar 1 matched (20/20). Bar 2 is 44/56 here versus 47/56.

## 7. Verdict derivation and cross-checks (step 1)

- Verdicts come from the program result: exit 0 and first line `no confident match` is NOT_ANSWERABLE, exit 0 otherwise ANSWERABLE, exit 4 JUDGE_ERROR. r001-r012 use the offline re-application recorded in the ledger (r010 ANSWERABLE, r012 NOT_ANSWERABLE, the rest unchanged); their ledger exit codes are from the previous grammar. `seen-check/outcomes-all.toml` has all 93 rows (run id, input sha256, exit, verdict).
- Re-derivation: I re-parsed each ledger reply with `judge.parse_verdict(reply, "Q1")`. 87 rows have the full raw reply in the ledger and all 87 agree with the ledger verdict. 6 rows (r010, r012, r046, r051, r077, r093) are abbreviated in the ledger; for them I took the last line as the ledger states it (r093: exit 4 as given). All 6 agree with the ledger's stated verdict (r010 and r012 against the re-applied verdicts).
- Independent cross-check: I also parsed the actual final reply text in all 93 judge transcripts (the audited copies) with `judge.parse_verdict`. 93 of 93 equal the derived verdicts. The 87 single-reply rows are byte-equal (after trim) to the ledger's raw reply text.
- Note on batch labels: the ledger's "batch N complete" markers (r001-r016, r017-r032, r033-r048, r049-r064, r065-r080, r081-r093) do not match the batch files (16, 16, 16, 15, 15, 15: r001-r016, r017-r032, r033-r048, r049-r063, r064-r078, r079-r093). I use the batch files. Scoring does not depend on batch.

## 8. Audit per batch (spec 5.3 / addendum 7.4; item 6)

Transcripts: `~/.claude/projects/-Users-gopalpatwa-opt-aveto-support--claude-worktrees-aveto-docs-answerability-85eb6d/8b67d5b9-a443-4c51-b73d-0017b2c6402c/subagents/agent-*.jsonl`. 314 files there; 98 have meta agentType `aveto-answerability-judge` (the others are qa-evidence and ai-engineer and were not opened). Each was mapped to a run id by its `Question:` line against the batch files (no question text repeats, so the mapping is unique). Checks per transcript, by script: `tool_use` blocks in assistant messages and anywhere in the raw file; every assistant `message.model`; first user message = `Base directory for this skill: <path>` + blank line (prefix length) + payload; sha256 of the part after the prefix against the ledger's input sha256 (which I re-confirmed by recomputing all 93 payloads with `judge-input --question-file` on question files recreated in the scratchpad; `seen-check/q/` untouched).

| batch | run ids | judges found | tool_use blocks | model on every assistant message | prefix length | payload sha256 == ledger and recomputed | verdict |
|---|---|---|---|---|---|---|---|
| 1 | r001-r016 (16) | 16 | 0 | all claude-haiku-5-5 | 150 on all | 16/16 | clean, not voided |
| 2 | r017-r032 (16) | 16 | 0 | all claude-haiku-5-5 | 150 on all | 16/16 | clean, not voided |
| 3 | r033-r048 (16) | 16 | 0 | all claude-haiku-5-5 | 150 on all | 16/16 | clean, not voided |
| 4 | r049-r063 (15) | 15 | 0 | all claude-haiku-5-5 | 150 on all | 15/15 | clean, not voided |
| 5 | r064-r078 (15) | 15 | 0 | all claude-haiku-5-5 | 150 on all | 15/15 | clean, not voided |
| 6 | r079-r093 (15) | 15 | 0 | all claude-haiku-5-5 | 150 on all | 15/15 | clean, not voided |

No batch is voided. Every run id has exactly one transcript in the run; none is missing and none is ambiguous. The payload after the prefix is byte-identical to `judge-input` stdout (including its trailing newline), so the harness did not trim it. Each judge transcript has one user message, no tool_use, and assistant content of `thinking` (85) and `text` (93) blocks only.

**Run ids with more than one candidate transcript:** r001 (3 candidates), r002 (2), r003 (2), all from discarded attempts. Selection: the candidate whose final reply equals the ledger row's raw reply. For each of the three the match is unique (the discarded attempt-1 spawns at 00:35-00:36 have no harness prefix and different replies; the attempt-2 r001 spawn at 02:20 has the prefix but a different reply). So r001-r003 can be told apart. Selected r001 = agent-a7ef2d539b... (04:44:45), r002 = agent-a71eaa8eb4... (04:45:00), r003 = agent-a3eb83bdbc... (04:45:13).

**Judge transcripts not part of the run (5 of the 98):** 3 attempt-1 spawns (r001, r002, r003), 1 attempt-2 spawn (r001), 1 probe spawn (agent-a9858747beaf, no question). All claude-haiku-5-5. The ledger says 4 attempt-1 and 2 attempt-2 discarded spawns; the directory holds 3 and 1. I could not reconcile that difference; it does not touch the 93 registered transcripts.

**Driver audit.** Spec 5.3's driver list was written for a subagent driver. Here the Orchestrator's top-level session drove through the `aveto-judge-seen` skill. I did not audit the driver's tool calls (no driver transcript was in my scope). The ledger's own disclosures are in section 10.

**Copies (addendum 4.3).** Each of the 93 selected transcripts was copied byte for byte into `runs/docs-answerability/seen-check/transcripts/` (compared with `cmp`-equivalent byte equality, and sha256 of source and copy equal). `grep` of the copies for `API_KEY`, `sk-ant-` and `Bearer`: 0 files match.

| run id | transcript file | sha256 source = copy |
|---|---|---|
| r001 | agent-a7ef2d539b58c7466.jsonl | 234b3de951dd8dec81f2776cfea8bd478a3e6ff18955faabd4b139a586bd60df |
| r002 | agent-a71eaa8eb4bc0d906.jsonl | 26736509b439c67489d4002dd1ea12b40dddd002e839c9bd95db76141f028f3c |
| r003 | agent-a3eb83bdbcddc8eaf.jsonl | ef9dceb16954d1da10b6a93d75e0907983c93c669c4cdf544f6f199ffa6984fe |
| r004 | agent-af96978135dd1a37f.jsonl | 6863edd8a02c4f07c57099878f8069b752c2d2bc1cfeeede0ae97a4a8784d1ea |
| r005 | agent-a71a9c7cb8f4c343b.jsonl | f13cf8da6c66d49bf61e7a92a9d19ec31fb2fb92f404784669117ecdaf908180 |
| r006 | agent-a5c2eeda98e560dea.jsonl | 5236f5e694a38fc5e39973f3c900e19634278f9b3f1439113b6ce674877591f3 |
| r007 | agent-a2443776df10c0f4e.jsonl | 67fdb7ff9cd929a86bbc903041478f7477e4d3f8a8c1b429d7192408fc7c0a41 |
| r008 | agent-a1a996eadb3e0a06b.jsonl | a13c2fa14e18c84996ec513e6385414a635cd6ae7a4bc3b85453a7ce22ff8a5d |
| r009 | agent-a765f5b66fb20f8ce.jsonl | 79103baab196c8c962b14f3b70627b9ed47fa7ecb4f6a35951fd0b1cfb84e267 |
| r010 | agent-a97a06d468daeedb7.jsonl | bff62f3450747b3c552c70b1455bf178482bab4088c8607982b079d643e9240c |
| r011 | agent-ac19b187e0990cffe.jsonl | d1673587aa6c4b5db50ca6ddad7b1634b6f34d7039a5a28f385ed30311657852 |
| r012 | agent-a6b2e4303efc37655.jsonl | f170950fab67c3eed5df885f9f3eb6306555e73c749601f1e521075b30e1db12 |
| r013 | agent-aaf9618f569b35ce6.jsonl | 9d5433ffdd1f773a1b8c9f251dae8b539c1a89bf063c0335dde0a0b1b8187d5c |
| r014 | agent-a4a280adcd261bd5e.jsonl | 251d9852b707662d64c281e2433c4d0f7b1c940a5c3717a0d4e68aebb0a083a0 |
| r015 | agent-a41d530e50b9bf0de.jsonl | dd63889d75de6263a59530cc7f83da439c0016896e1763e5a67d63bdda5bdb8c |
| r016 | agent-a6c24a061286e9640.jsonl | baea403fe79a445821b76030b2bd7c070a206d2ad1afebf305a96d0c848bcc67 |
| r017 | agent-a7640182ddc86e2bc.jsonl | 47b0198326413714772517d9b3adbe015d60fda2c98ee02e354f5aa3f2563ff9 |
| r018 | agent-aa2e91b3c76344c4c.jsonl | e090cefcdbd9f24cb6b5eedafd89e9d7ce7eadae397e6389296a784b06ebfcb2 |
| r019 | agent-a083604ee0819f48b.jsonl | 4ed249d14fe50369f1e6da443abbf4dff16f29cade4db4caed2b8d252c351a95 |
| r020 | agent-a347cd17f5d63284d.jsonl | 53dd263c74a2c7fb4cef92dad9a7ace77b83abb1947be074dcd9689bf8614697 |
| r021 | agent-a2abd1229c584cb44.jsonl | 18187815c46d9cc9cd7c031a01559f82966c2959e5ae527da100aeb43d79043c |
| r022 | agent-a597e3a6adaa2e28d.jsonl | 118e326eab7fa64dab1c3308ca3328a6eb0046993e04c6a2d17ee3b09344a8a1 |
| r023 | agent-a5c7002269a129c85.jsonl | c763f602d465734e36ae132cadd2998a8e71a314cd50e13945d662584f3d95d2 |
| r024 | agent-aea93eac265760435.jsonl | 84522b50218c8532ce009cee486270527bc18af33feb4dc30b2da830ec245ca3 |
| r025 | agent-a61a5363fa6a901be.jsonl | 0f52f74e0795dd40b8c76639233cbfcadffd70b1d0a5c7a8c5d08000da1dbae8 |
| r026 | agent-aaffaf8f09952cceb.jsonl | 8545b1a95d5ed56c97fddfe11c0a471ec2dc763604e99b03d9995b6bc2283509 |
| r027 | agent-a17fa15d5ec43397c.jsonl | 05e6889fd7aa35bf2f9dd8b6daf42eed62133272deaf05126c93488e1488f141 |
| r028 | agent-ae4c33411d86d9786.jsonl | 18b5383e9a16e8c0e1a850051c3804ec888e72eff8d7c4b94de87f0df7e8d251 |
| r029 | agent-a2157bb2c8f8835df.jsonl | 7a7e17f6f9ad2a8e7e25a944a11633a6dc6b967d08220593fb68cb10e4526d2e |
| r030 | agent-a69968040e1a3cf23.jsonl | 93a49192b40180ed2a93537821f789c7e550716fa33be09c3d659b84217e0a5d |
| r031 | agent-ac6cae84c45c45b91.jsonl | 9e81c1bb3bfee987f9f951bac0b2a9a52192d2d8237484834d73a3a0f3fa01da |
| r032 | agent-ad03c979be9f5017a.jsonl | f339fbcde0d4d86f8d07ffd19bbb1099b177777b36b6acb8df6a56cc114dcc7a |
| r033 | agent-a8ae6d6ae117c65d6.jsonl | 64fcc04857ef96ca0ed3228a3ca22cb36b9fcf132ab8fe3483fafa013e014339 |
| r034 | agent-af2afc47ed69ff3f9.jsonl | 124324b92285acbd104c0c8b93c61b6ba3b7ae8479592d773837fd4fe061b03d |
| r035 | agent-a9017e0cd6c7a6d94.jsonl | 6e10e2cae38bc9aab478fd9ea900addf8d58bc15ea1757514c2c58e024f14d0f |
| r036 | agent-a4dfc6c5a26ac3345.jsonl | bdb1fc9610df60f75def3cadc4ca2c6450543c0b7d7b1f99e443dc7677784a4e |
| r037 | agent-acf18baac817a4e0c.jsonl | bb2e55280c1d5cf9ae148a7740876d078f9b6df3559cde96543b2b22c194e3dd |
| r038 | agent-a131ba8de92640f4c.jsonl | efaa973b8a1e6de5012e4662ef98242ac53e2b62f59efdebb08d2559949a764e |
| r039 | agent-ad55382389fae7a28.jsonl | e4dbe6026a6b6f2a883f9f25a62acefefc4b96f750088ef165eea0ee5bc412a2 |
| r040 | agent-aa479cd6b67c869c3.jsonl | 401016e1cb24100e40f783bb4c1c2a35ebeae8184f2a97e175fe4a2ebcabbd04 |
| r041 | agent-a38c2684065c8475a.jsonl | 3989c9b65159fe0ca0f910cc1e4a0f18116b4953418fbe6a72eeac4eeaa8cb74 |
| r042 | agent-a1a932907420a8581.jsonl | a8304708c128794a7ca4534fd96824f5242e363436b31b9faea9c4f6badae44f |
| r043 | agent-ac4d4ebaa96855035.jsonl | 95a6e29501d88c880964742272d66fb88212a6e5b8f7fe65b2f211160c7d15c7 |
| r044 | agent-ac038a99f33cfbe1f.jsonl | ec3097e084f63592461c8197f52761fc0355a3dc3c30501b97e49319bf2c3520 |
| r045 | agent-adeb3fb5c2d82a66c.jsonl | ec7a4a0ea2685cf10657b9923b6c54e51eb85956c2dc0153f5e0f91021e5a850 |
| r046 | agent-ae00618b18a12d063.jsonl | e612a25f57ee04d709d98b00f9747400d8977a5823e22ab36884c15a9413dc89 |
| r047 | agent-a49f220737ffcc108.jsonl | 3958d42346ca0c67305673febe606b23554c11f4bb070ce15e91f77f387ed026 |
| r048 | agent-a52c5a2f6dbd5decd.jsonl | f6cc9aac9381b6f9530c01a977f116e3d74313a44255e1ac80719b3e7da793c1 |
| r049 | agent-aa4be287f795518ab.jsonl | 340da55c4f4940437ca6687b2d291b9074ae3b87b88081e8e8b05ef0056e8796 |
| r050 | agent-ac70683156ce31faa.jsonl | 7c3f4eaf328ef664a568dd889656531cc04969b95b9892d60c414ef7712d0491 |
| r051 | agent-aba5ce7c67fc67b6a.jsonl | f5a9f35963e9f17aa16a6c62fcd8ff9e70358b1394906b01bf4e3d4b54368a58 |
| r052 | agent-a46ee1f301446f0fc.jsonl | 9da0613831f36e4b3663f4edb19b26e05e06074da10cb05ad6f1422294e08a76 |
| r053 | agent-a0034e710ae3e96ee.jsonl | a7d2f14a0c6f27da0fdf13b305411dafd79ffcb0ef3d66290749a3e2942b69cb |
| r054 | agent-ad7388aae2f5cb746.jsonl | 8da5a910526b1f6f966435723c626dc15c716a16cf8848415a13aaf2180eed5d |
| r055 | agent-ae359bc0e94dc0831.jsonl | 612d52dd8985b9776dbfd27c223209735a8744ac5df02b111ab32c16b8e0e1e7 |
| r056 | agent-a6cef9d3d5e0626c9.jsonl | d7bfe09672ad3cccafb53cfebc547350f94a10ed6e271fe57f7abb6c8cfd6077 |
| r057 | agent-aeaecc160b5dfc1c9.jsonl | 4072947e7b586ecefe4e245329c93c68b093ea82032822e9ad6c2a65f1a27fcd |
| r058 | agent-a9705354bee0e2098.jsonl | 5a4832fff93ee592020d98f03c028369c7ef774cd7b25500b54bcb499c838067 |
| r059 | agent-a521662dacf9cd403.jsonl | 6119c50e3723fcc1595b54ec6d464a614825df5a31f1740106c8e33f648c19f1 |
| r060 | agent-a052d7ece9231c913.jsonl | 0e4c5d108ec704cafbca7140019d812e2caa5b30b5b097f8922ab1ebf124751a |
| r061 | agent-a74749cd96e2d49b7.jsonl | fdc0322fa658c295039c066aae48f1ea557bb94610f5b982996914ea34115bfe |
| r062 | agent-a891075ab9e77dd8f.jsonl | f9b35c8e899fa6a627997b26cea5be8387f219ec32e7d5d657e8ed88dec5b7f2 |
| r063 | agent-aec0b04bcbd0d06ff.jsonl | 7f6b0a9611b36c8bd11a237178029c99cc5bba025066197f8583a81c5c662713 |
| r064 | agent-a40fd6185d684ea2b.jsonl | bb63845e7ee4d4ac18c14cc6116a88188d98675d5d7dff959ab95c710b27123b |
| r065 | agent-ab9e1a05815813d5d.jsonl | e960b8dffd625e62551a758a5e1db6eedb27ad805b3942ea92804f84886a48b9 |
| r066 | agent-af34074a6eb7403f5.jsonl | 692d0d22313d9b81f3a08f01d732371ed240126ccac16983bb8878443abb1a8b |
| r067 | agent-ad599cdf3a7768080.jsonl | bbee263df77a4998c93d558d603adaf4af38730d82aad35bcd22f43f5904376e |
| r068 | agent-aeba1580b70d89eb1.jsonl | 77adbbc41841a25ddd90d9fbcbb32ec8a1e9f7b4249a755683b1ffef746395e5 |
| r069 | agent-ad67d7f7ab427de64.jsonl | ae33b86258ab6b08c9b6a100659432d50bf42827121acb557912ed7238a630ed |
| r070 | agent-a4808318943647050.jsonl | 481a490e889f6d9a45a463c334df1ff1ee78e7fc7039e0883a48079be1d132b2 |
| r071 | agent-a5556f03c97f8b867.jsonl | 47edc2f1495710d71d5025205ef3dfe5a571f1e1ccb3937f4d0385a7b0e831a2 |
| r072 | agent-a0303ef9da5a8b759.jsonl | ffbf7cf4bfb7af14d8420d057e5a134be618eadd9067d02c7d27bd9c8dcea5cb |
| r073 | agent-a19e0d17110bdca91.jsonl | 518c4209ae3d88710153f33f0718cbaff7da53c3fc4032c7e9ffab9cef8dd1fc |
| r074 | agent-a0555139a76900227.jsonl | 66626af2774bc2e4f784b1f122a121d3dcaa7673a16caa6ef6ca58c66a8e7d38 |
| r075 | agent-adc083b90ae4e43d3.jsonl | 3cd6da1d8d36e5040afe5dabbc2da13c008ee99566d1d35a3700d0c7ba2dd246 |
| r076 | agent-af1c359150c54366b.jsonl | b870948f66bd8115c4ccd2c2b64fddcfcdf329a2c9f0786be71e256c68eec53a |
| r077 | agent-ad451fe25c1f78ddf.jsonl | 4d1428acceaacda650612885cc40259ea40be313b1d4d518fe8495bd5d8d5c63 |
| r078 | agent-a3f81cc7e37ba9758.jsonl | 12840897497aeb5b00aeea5f33846fc9090e24163a421160e9c1481ffa08cb5d |
| r079 | agent-abb0a4c48a723e612.jsonl | 25934dac86ad44d452eb78555eaa64450b08e2b7786d989f8ef6280c343fca5a |
| r080 | agent-ad97f804356f3793b.jsonl | 6456a1100d59492c35b1c5cac77afa4ded6240cd7be05bc43ed4197ff732c322 |
| r081 | agent-a486f6d99f56bd714.jsonl | e9acea114e7dea583ea0d21722b7ece1a13f2f4c401cd58bdf3d6ddb9d1ba7eb |
| r082 | agent-a861cf1668f1b5f63.jsonl | 5e2c7944ec37b3aa421df6064bb32f404374195553f29a721b2e084c8c736b1b |
| r083 | agent-acd67e0da793302dd.jsonl | b48b8d9548c7b5dc78dd7eb181919bc42b1b65ee1e72cf48b4923a4b1680e0af |
| r084 | agent-acf5660fc77b6a0b8.jsonl | 1a81b9467f13da8004aab736171ce42a460aaa6a5c095cda6cc55a79e2a58124 |
| r085 | agent-ac5e57559e7f525f8.jsonl | 5c4b068eb9422d959537dcc7262d65c143e297c213bfa088e8eae208a2afbaac |
| r086 | agent-ae8af07cfe65cc187.jsonl | efd5e1941733d0b31d776944a2c3641d30d2b29339ad069ea7f0864f79f0be2a |
| r087 | agent-acb56d5ae99fb19a5.jsonl | e3161d67fee508c9e52972f46c71016ea8f37354c591982398bfd26d347babcf |
| r088 | agent-ac88b2c3e55c9e414.jsonl | 99f84b7348adbc079167429c173392dac97f9095708ee82d4ffac061fdbdc36c |
| r089 | agent-a54c8d41d9400a315.jsonl | 029f0976ecd8ef4f34e2d6cf52950d7442a2374c0b583a9d394c935df833c8d1 |
| r090 | agent-a6b29e5573c4d0f39.jsonl | 667d2279e99106ad53545e31c8b06c4c9b60606c9c9f95316b25cdc96765e91e |
| r091 | agent-acb611aeac9f377e5.jsonl | 265dc8b7bfa2d3e46ceced23bb13178dd99a556dd721ec19263ad126642aac7a |
| r092 | agent-a0dc04dd86c264728.jsonl | 58c62d915b594b35c98afc88153c9f9cd6a00792753a6085209f4031a8821646 |
| r093 | agent-acc1a39c8da76a9ac.jsonl | ee2d678bba65ac54c6487199b44e6ddfcc84b7baabdd4aaba9cf340fa4748269 |

## 9. Model per spawn (item 7)

The harness ran `claude-haiku-5-5` for every one of the 93 registered judge spawns (every assistant message of every transcript; set of models per transcript is exactly that one value). The 5 non-run judge transcripts also show claude-haiku-5-5.

## 10. Disclosures

1. **Two re-registrations came after seeing failures on these same sets.** APPROVAL_RECORD-9 (colon rule and the "harness prefix then payload" layout) and APPROVAL_RECORD-10 (verdict read from the last non-empty line) were each decided after failures were seen on these seen sets. APPROVAL_RECORD-10 states the protection is the fifth set. The check is therefore not a clean pre-registered measurement; the grammar was tuned on this data. The bars were unchanged (16/20, 45/56). Even so the result fails.
2. **Harness prefix.** Each judge's first message carries a 150-character harness prefix (`Base directory for this skill: <path>` plus a blank line) before the payload, on all 93 spawns. This is registered in APPROVAL_RECORD-9 but is not in the pilots.
3. **Driver deviations (from the ledger).** `judge-apply` was run inside an `out=$(...)` wrapper with trimmed output; before r001 (attempt 1) the driver ran cat/ls through Bash; extra `judge-input` runs for the sha and a transcript-prefix check on r001's first forked spawn (attempt 2, discarded); the driver should have stopped at r010 (the first judge error) and did not (ledger: "driver error, disclosed"); r001-r012 were produced and first scored under the previous grammar and re-parsed offline.
4. **The driver was not a fresh context** (it was the Orchestrator's top-level session), against spec 5.2's "one fresh context per batch".
5. **Discarded attempts exist:** attempt 1 (r001-r003 judges, outcomes and replies under `seen-check/discarded/`) and attempt 2 (r001), plus the probe spawns. They are not part of the 93. The registered run was spawned once per question.
6. The seen-set questions passed through `seen-check/q/` question files that `judge-apply` deletes after use; I recreated all 93 from the batch lines in the scratchpad (r001 compared equal to the surviving file).

## 11. Exit-2 / payload errors on the real corpus (item 8)

None. `judge-input` exited 0 for all 93 questions; no `PayloadMarkerError`. All four `eval --verdicts` runs loaded their verdicts files (no exit 2); the loader recomputed each `input_sha256` and found no mismatch.

## 12. Usage (item 9)

To be recorded by Orchestrator.

## 13. Files written (QA scorer)

`seen-check/outcomes-all.toml`, `seen-check/verdicts-retrieval.toml`, `-retrieval-heldout.toml`, `-retrieval-heldout-3.toml`, `-retrieval-heldout-4.toml`, `seen-check/transcripts/` (93 files), this record. Nothing else.

## 14. Result

The check failed: pooled Bar 2 44/56 against 45/56, pooled Bar 1 20/20. Stopped before the fifth set; owner decides.

