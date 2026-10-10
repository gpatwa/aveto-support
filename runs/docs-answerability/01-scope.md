# Scope Review — docs-answerability

> Engineering Manager, standard depth. Tier 2. Repo at 56b4723 (main + the slice's intent). Every check below is a grep or read of the cited line; "unverified" means the source was outside my read list. I did not edit the intent. I did not read or look for a fifth set.

## 1. Verdict

**Scope accepted, with one required clarification (section 5, Q1) and one pre-registered split trigger (section 4).** The slice already has the A/B split at the freeze. Implementation is accepted as one pass, provided its file count stays within the rule.

## 2. Claims checked against the repo

### Orchestrator findings (00-slice-plan.md "Findings")

| # | Finding | Result | Evidence |
|---|---------|--------|----------|
| 1 | Judge input is not the displayed text; do not reuse `_excerpt` | **Confirmed** | `_excerpt` keeps at most 3 non-empty lines, each cut at 160 chars (`aveto_support/__main__.py:26-37`). `per_file_cap = 2` (`index.py:86`), applied at `search.py:407`, so at most two passages per file are shown. The pilots' "at most two passages per file" matches that cap. The pilots' own input format is **unverified** here (pilot doc not on my list). |
| 2 | Pilots' prompt is a section of the playbook pilot doc, not a file | **Unverified** | Pilot doc is outside my read list. The Architect reads that one section and copies it byte for byte, then hashes. |
| 3 | Budget: intent 700k vs measured about 935k | **Confirmed** | A = 55+80+60+130+100 = 425k; B = 60+100+115+150+30+55 = 510k; total 935k. The owner confirmed 950k with ceiling 1.4M (about 1.5x), STATE.md lines 46-47. |
| 4 | `CURRENT_MVP_STATUS.md` stale | **Confirmed, and the file differs from the plan's line numbers** | Lines 38-39 say `wordpiece_golden.json` is missing; `tests/fixtures/wordpiece_golden.json` exists. Lines 22-23 say `eval` "exits non-zero below 80% on either group"; the code gates answerable only (`evaluate.py:50-52`; `LOCAL_COMMANDS.md:17` agrees). The "lines 8-10 and 17-18" in the plan refer to an older file; at HEAD, lines 5-10 (two embedding-model files) are accurate and the abstention text at 17-21 is already corrected. |
| 5 | `ARCHITECTURE.md` stale, ADR 0007 | **Confirmed** | `docs/ARCHITECTURE.md:193` lists ADR 0007 as "abstention by a local answerability judge"; ADR 0007 line 5 says status **rejected**. Next ADR number is 0008 (0001-0007 exist). |
| 6 | 93 seen questions | **Confirmed** | `[[question]]` counts: `retrieval.toml` 30, `retrieval-heldout.toml` 23, `-3` 20, `-4` 20 = 93. Unanswerable (`answerable = false`): 6+6+4+4 = 20, matching "20". The 56 answerable-with-hit figure is derived by running retrieval and I did not verify it. `evals/calibration-offtopic.toml` (59) is **not** one of the seen sets; the seen-set check must not include it. |
| 7 | No judge among generated agents; installer rewrites the directory | **Partly confirmed** | No `*judge*` file under `.claude/agents/`. `install.mjs:5,93-102` generates `.claude/agents/<role>.md` from the playbook's briefs. Whether it also deletes foreign files is **not established**; the Architect reads `install.mjs` before choosing a location. I did not recount the 28. |
| 8 | README and INV-5 consistent with the intent | **Confirmed** | README 4-6 and 55-56 ("never abstains"), 70-71 ("no question or passage text ever leaves your machine"); INV-5's sentence at `SAFETY_INVARIANTS.md:57-58`. |

### Intent claims and what the Orchestrator missed

| # | Claim | Result | Evidence and consequence |
|---|-------|--------|---------------------------|
| A | Stakes allow the short path | **Contradiction, see Q1** | Stakes ticks "real user data" and "safety control". The EM brief: "Stakes override completeness ... the full chain runs however complete the intent is." The plan's "Skipped on purpose (short path)" for Market Research, PRD, UX needs the owner's recorded word. |
| B | INV-4 "gains a statement that a model may judge" | **Partly stale** | INV-4 already says "A model may be used only to rank passages and to decide confidence" (`SAFETY_INVARIANTS.md:35-36`). It also says retrieval "does not abstain". The new wording must reconcile both: `retrieve` still does not abstain; the verdict command does. The Architect proposes exact words; this is the rule 4 text. |
| C | INV-5 sentence is rescoped | **Confirmed, and it is mirrored** | The same sentence appears in `docs/ARCHITECTURE.md:157` and README 70-71, and INV-4 is mirrored at `ARCHITECTURE.md:142`. The Tech Writer fixes all mirrors only after the verdict and under the approved words. |
| D | "No new API key / no metered API" | **Conflicts with a standing project line** | `.agentic/PROJECT_CONTEXT.md:83-84` says runtime model calls use the owner's API key behind a spend cap; line 78 says "No generative model is used anywhere"; lines 68-79 still describe slice 2 as "in progress". This file is owner-written. The intent overrides it for this slice by the owner's decision 1. Do not edit it; flag it in the close-out. |
| E | "`eval` scoring the two bars ... retrieval gate's exit code unchanged" | **Constraint found** | `EvalReport.passed` and exit 0/1 depend only on answerable hits (`evaluate.py:50-52`, `__main__.py:166`). `__main__.py:164` calls `evaluate.py` "frozen". Recommended default: new scoring goes in a new module and a new flag or subcommand; `score`, `EvalReport.passed` and `format_report` stay unmodified. The Architect decides. |
| F | Judge "with no tools beyond what it provably needs" | **Architect to settle** | The payload is in the prompt, so the likely answer is no tools. The pilots' tool-use audit (any tool use beyond the allowed reads voids a batch) is the check; the Architect states it. |
| G | Starts from main, slice 5 merged, pack v17 | **Confirmed** | `git log`: PR #3 (docs-abstention) merged under 56b4723; STATE.md line 13 records pack v17. |
| H | Retrieval, ranking, corpus, embedding model unchanged | **Holds at HEAD**, to be re-proved at the gate | Diff of `search.py`, `embed.py`, `index.py`, `docs-source.toml` must be empty at the Release Gate. |

## 3. Stages, tier, gates, approvals

- **Tier 2** (behavioural change, no external effect from the program). Agree with the plan. Tier 2 gates: all implementation, QA and security gates, release checklist, rollback plan (`RELEASE_GATES.md:85-91`). Tier 3 does not apply: nothing the product does posts, deploys or sends. The operator's own session sends data; that is rule 6, already approved.
- **Stages: as in the plan, unchanged.** Scope, Architecture (two passes), Implementation, Seen-set check, Freeze, Label review, Scoring, Security, Release Gate, Docs, Close-out.
- **Security stays adversarial** (intent line 133; a lower depth needs the owner's recorded word, and none is on record). **The Release Gate is not compressed**: three spawns (plan, QA run, Release Manager verdict).
- **Approvals.** Rule 6 approved (APPROVAL_RECORD-2), attended only approved (APPROVAL_RECORD-1). **Rule 4** (exact INV-4/INV-5 words) and **rule 5** (judge artefacts: prompt with sha256, agent definition, tier, tools) are requested only after Architecture pass 2, in one packet, with the exact words. No safety-control text is edited, and no code or artefact that sends data exists, before the owner approves. `HUMAN_APPROVAL_RULES.md` rule 4's list does not name an invariant edit, but the intent and `AGENTS.md` treat it as a safety-control change; I agree with that conservative reading. Rule 5 applies because an LLM step enters the path that was deterministic, even though the program itself never calls a model.

## 4. Scope

**In**
1. `retrieve` and `eval` unchanged in default behaviour, offline.
2. Three offline, deterministic additions, each tested: judge-input output mode; verdict-applying command printing today's output or exactly `no confident match` (exit 0) and naming the deciding signal; `eval` scoring the two bars from a verdicts file with the retrieval gate's exit code unchanged.
3. Judge artefacts: fixed prompt (committed, sha256), Haiku-class agent definition, the command or skill that runs the step.
4. A test that asserts the program makes no network call and calls no model.
5. Verdict grammar: exactly one of two tokens, else `judge error` (fail closed, no reasoning shown or stored).
6. INV-4/INV-5 words, ADR 0008 (supersedes the rejected ADR 0007's role), contract text.
7. Seen-set check, freeze, label review, one scored run on the fifth set, Security, Release Gate, docs after the verdict, close-out.

**Non-goals** (as in the plan, restated): drafting, the INV-3 draft checker, classification; any change to retrieval, ranking, corpus or embedding model; any second model or tier unless a measurement says so; posting; unattended or scheduled use; any credential, API key, metered call or `claude -p`; `docs-retrieval-ci`; the Azure runner; editing `evaluate.py`'s existing scoring; editing `PROJECT_CONTEXT.md`.

**File-count check (rule: more than 10 files for non-refactor is rejected).** Implementation's expected files: `__main__.py`, one new judge-input and verdict module, one new scoring module (or `evaluate.py` if the Architect justifies it), the prompt file, the agent definition, the skill or command, and three test files (new tests plus `conftest.py` if the offline block needs a marker) = about 9. Docs (`SAFETY_INVARIANTS.md`, ADR 0008, `ARCHITECTURE.md`, README, status) belong to Architecture and Docs stages, not Implementation. **Split trigger, pre-registered:** if the Architect's spec lists more than 10 files for Implementation, split it into 3a (the three offline pieces and tests, which need neither rule 4 nor rule 5) and 3b (judge artefacts, after the approvals). Do not mix any refactor of `__main__.py` into this slice (rule: no behaviour change mixed with refactor).

**Stop conditions (pre-registered, from the intent and the plan)**
1. Seen-set check pooled below 16/20 unanswerable or 45/56 answerable-with-hit: stop before the fifth set is touched; report numbers to the owner (about 365k spent by then).
2. Any tool use beyond the allowed reads in a scoring batch voids that batch; one rerun; both reported. A second voiding stops the slice.
3. Spend above the 1.4M ceiling, or any gate that would have to be compressed: stop and ask. The ceiling is never raised by an agent.
4. Any request to edit safety-control text, or to create a code path or artefact that sends data, before the owner approves the exact words: stop.
5. The fifth set arrives before the method commit is recorded, or any agent in the method stages has read it: stop.
6. Two bars are never moved: 20 of 24 unanswerable abstained; at least 80% of answerable-with-right-file-in-top-five not abstained. Either failing means "not releasable".
7. A gate fails or a stage fails twice: `FAILURE_LOOP.md`, then the owner.

## 5. Open questions for the owner

**Q1 (required). Stakes override.** The intent ticks "touches real user data" and "changes a safety control". The EM brief says the full chain runs in that case; the plan skips Market Research, PRD, UX, UI, Cloud Deployment, SRE and Production Verification. If `APPROVAL_RECORD-1` named these skipped stages, cite it and this is closed; I could not read it. If it did not, the owner should say so in his own words. **Recommended default: keep them skipped.** There is no screen, no market question, and no deployment; the Architect's threat model and the adversarial Security Review cover the risk the override exists for. Do not run a PM or UX stage.

**Q2. Exit code when the verdict is `judge error`.** The intent fixes only that it prints `judge error` and shows nothing as judged. **Recommended default:** a distinct non-zero exit (not 0, so a script cannot mistake it for a judged result; not 1, which `eval` already uses for the bar; the Architect picks the number and updates the exit-code list in `LOCAL_COMMANDS.md`).

**Q3. Where the judge definition lives.** The Architect decides after reading `install.mjs` (whether it prunes foreign files). **Recommended default:** a product-local skill or command under `.claude/` that the installer does not generate, with the prompt file under a repo path, so a pack re-install cannot silently replace it. If the installer prunes, use a skill outside `.claude/agents/`.

**Q4. Fifth-set handover.** Confirm that the support session hands it over only at the Freeze, after the method commit is in STATE.md. **Recommended default: yes**, as the intent says.

No question about the product, the bars or the budget.

## 6. Read lists for the later stages (tight)

**Architecture, pass 1** (about 10 files):
1. `runs/docs-answerability/intent.md` and `01-scope.md` (this file).
2. `.agentic/SAFETY_INVARIANTS.md`.
3. `aveto_support/__main__.py`.
4. `aveto_support/search.py` lines 175-215 and 452-505 only (the result types and `retrieve`).
5. `aveto_support/evaluate.py`.
6. `aveto_support/index.py` lines 80-105 only (`per_file_cap`).
7. The playbook pilot doc `docs/pilots/2026-10-llm-answerability-pilot.md`: the prompt section (about line 103), the block format, the verdict grammar and the tool-use audit only, by absolute path.
8. Playbook `execution/install.mjs` lines 90-130 and 200-230 (what it writes and prunes), plus one generated agent file for frontmatter shape.
9. Playbook `docs/HUMAN_APPROVAL_RULES.md` lines 65-108 (rules 4-6) and `docs/adr/0007-answerability-judge.md` as the format to supersede.

Not for Architecture: the other `runs/` artefacts, `ingest.py`, `embed.py`, `rerank.py`, any eval file's contents, the fifth set.

**Architecture, pass 2:** its own pass-1 spec, `SAFETY_INVARIANTS.md`, `HUMAN_APPROVAL_RULES.md` 65-108, `docs/ARCHITECTURE.md` lines 138-160 and 190-195, the approval template. Nothing else.

**Implementation:** the Architect's spec, the approved INV words (APPROVAL_RECORD-3 or later, whichever holds them), `aveto_support/__main__.py`, `evaluate.py`, `search.py` result types (the same ranges), `tests/conftest.py` (autouse network block), `tests/test_evaluate.py` and `tests/test_search.py` for fixture style, and `.agentic/LOCAL_COMMANDS.md`. It must not read any eval file beyond the format lines in `load_eval_set`, and must not read the fifth set.

**QA, seen-set check:** the spec's section on the check, the judge prompt file and agent definition, the four seen eval files, the product's block output (run `retrieve`/judge-input, not the code), `runs/docs-answerability/03-implementation.md`. Fresh judge subagents per batch under the tool-use audit. Nothing about the fifth set.

**Label review (slice B):** the fifth set and the `docs/` corpus it targets (via the pinned index), the intent's "Done means" label rules. No method code.

## 7. Estimate check

This stage is est. 55k against a spent budget of 0 in a 950k plan: `spent + estimate <= budget` holds. No stage in the plan is over the ceiling at its estimate. Review stages have run over estimate in the last two slices (docs-abstention close-out section 3); the read lists above are the control.
