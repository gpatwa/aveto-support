# Security & Privacy Review — docs-abstention

- **Reviewer:** Security & Privacy Agent (standard depth, review archetype)
- **Range reviewed:** `0dfd433` (main) .. `HEAD` (`34c23d7`), branch `claude/docs-abstention-c835b1`
- **Verdict:** **PASS with advisories** (0 blockers, 0 required-fix, 4 advisories)

## 1. Net change to product code, tests, dependencies, lockfile, corpus pin, `.claude/` — PASS

- `git diff --stat 0dfd433 HEAD -- aveto_support tests pyproject.toml uv.lock docs-source.toml .gitignore .claude` is **empty**.
- The whole-range name list, minus `runs/docs-abstention/**` and `docs/adr/0007-answerability-judge.md`, is exactly one file: `.agentic/SAFETY_INVARIANTS.md` (section 2).
- Revert exactness: `git diff 479f82a^ f1a96ad` is **empty** — the tree after the revert equals the tree before the candidate commit. 479f82a touched 10 files (`aveto_support/{__main__,evaluate,ingest,judge,search}.py`, `tests/{conftest,test_evaluate,test_ingest,test_judge,test_search}.py`); none survive. `aveto_support/judge.py` does not exist at HEAD.
- No file was added outside `runs/docs-abstention/` and `docs/adr/0007-*` (`git diff --diff-filter=A`).

## 2. INV-4 edit — PASS

- Whitespace-normalised comparison of INV-4 at `0dfd433` vs `HEAD`: the new first sentence equals the APPROVAL_RECORD-7 approved text **character for character** (line-wrapping only), and everything after it (the "never returns generated or reworded text" sentence, the **bold** model sentence, and the six-test enforcement list) is **identical** to main.
- The diff hunk is confined to INV-4 (one `@@` hunk, lines 29-35); INV-1, INV-2, INV-3 and INV-5 are byte-unchanged.
- Truth at HEAD: `grep -rni "no confident match\|abstain" aveto_support/` finds only `search.py:455` ("Never abstains") and `__main__.py:130` ("diagnostic, retrieval does not abstain"). Nothing in `aveto_support/` can print "no confident match". `evaluate.py:151` prints `unanswerable: N (diagnostic only, not gated)`. The sentence is true of the code.
- Approval chain: rule 4 change, owner typed approval in the driving session (APPROVAL_RECORD-7, 17:50:52Z), after APPROVAL_RECORD-6 explicitly left 8.3 pending. Correct order.

## 3. INV-5 at HEAD — PASS

- Net diff for `aveto_support/`, `pyproject.toml`, `uv.lock`, `docs-source.toml` is empty, so network egress is exactly main's.
- `grep -rni "judge\|qnli\|electra" aveto_support/ pyproject.toml docs-source.toml` → **no matches**. The judge download is not wired into `ingest`; no module references it.
- Network code at HEAD is only `aveto_support/ingest.py`: the GitHub archive GET (line 256) and the HF model GET (line 293), both through the host-restricted redirect handler. `search.py:383/389` only format permalink strings. These are the two documented kinds.
- The judge files remain in the gitignored cache (`models/cross-encoder--qnli-electra-base`; `.gitignore:16 models/`), not tracked, and nothing at HEAD loads them (advisory A2).

## 4. Secrets, PII, approvals — PASS

- `git grep` over `runs/docs-abstention/` and `docs/adr/0007-*` at HEAD for API keys, `hf_`/`gh*_`/`sk-`/AKIA tokens, JWTs, private-key headers, `bearer`/`authorization:`, `password`/`secret`, and e-mail addresses: **no matches**.
- No user or question text: `02-baseline-questions.csv` carries set, id, label, scores and file paths only; eval questions referenced elsewhere come from the committed seen sets under `evals/`, not from users.
- Local absolute paths (advisory A3): `00-slice-plan.md:5`, `STATE.md:10` (playbook path), `02-baseline.md:7` and `:376` (worktree path). They expose a local username only.
- `02-baseline-sweep.py` (committed under `runs/`) imports only stdlib (`argparse, csv, os, statistics, sys, pathlib`) and writes CSVs to its output dir; no network, no subprocess.
- STATE.md Approvals table matches the records: 1 (plan), 2 (Q1-Q5), 3 (budget), 4 (licence), 5 (rule 5 + rule 4 4-i/4-ii + INV-5/A1, 17:05:20Z), 6 (option 1 and the lapse, 17:49:16Z), 7 (INV-4 spec 8.3, 17:50:52Z). Approver, rule, timestamp and record path agree on every row.
- Lapsed approvals (record 5) were not applied: the only commits since main that touch `.agentic/`, `aveto_support/`, `tests/`, dependencies, `evals/` or `.claude/` are 479f82a (candidate code), f1a96ad (its exact revert) and 34c23d7 (the record-7 text). No record-5 text (items 4-i/4-ii, three-model INV-5, A1 line, `test_retrieve_is_offline_with_cached_judge`) appears in `.agentic/`, `README.md` or `docs/` outside ADR 0007. The rule-5 download happened inside the approval window (17:05 to 17:49) for the seen-set confirmation; the lapse looks forward and nothing uses the file now.

## 5. Fifth or gate set — PASS

- `git diff --diff-filter=A 0dfd433 HEAD` adds no file outside `runs/docs-abstention/` and `docs/adr/0007-*`; nothing under `evals/` changed.
- Eval files at HEAD: `evals/retrieval.toml`, `retrieval-heldout.toml`, `retrieval-heldout-3.toml`, `retrieval-heldout-4.toml` (the four seen sets) plus the existing `calibration-offtopic.toml`. No fifth set.
- Records consistently state it was not read: `00-slice-plan.md:35` ("I have not read it"), `02-baseline.md:371`, `STATE.md` option-1 plan ("the fifth set stays unspent and unread"). The worktree has no untracked files outside the usual ignored caches.

## 6. Other safety-control or approval-path changes — PASS (no further changes)

- `.claude/` (hooks, agents, settings) unchanged; `.gitignore` unchanged.
- ADR 0007 status changed proposed to **rejected**, citing APPROVAL_RECORD-6. The "never edited after it is accepted" rule does not apply because it was never accepted.
- No audit or approval code path exists in the diff (no product code changed), so no audit event could be added or removed. No placeholder adapter changed. No generative model was added. INV-1 posting gate untouched.

## Advisories (not blocking)

- **A1 — stale abstention claims elsewhere (pre-existing, not in this diff).** The corrected INV-4 now says retrieval does not abstain, but these lines still describe `no confident match` as a retrieval output: `README.md:50`, `.agentic/CURRENT_MVP_STATUS.md:12`, `docs/ARCHITECTURE.md:27, 87, 111, 142`. They overstate a safety behaviour the product lacks, and the intent's Done-means asks that README and CURRENT_MVP_STATUS claim nothing stronger than the truth. Fix them in close-out or a follow-up docs slice. Note that `.agentic/CURRENT_MVP_STATUS.md` needs the usual owner path. The intent's Must-not-break line "when unsure ... default is to say 'no confident match'" is also unmet, as it was on main. The Release Manager should record it as the reason for "not releasable", not as a regression.
- **A2 — cached judge files.** `models/cross-encoder--qnli-electra-base` (~438 MB, gitignored) stays on disk under a lapsed approval. It is harmless while unreferenced. Any future slice that reuses it needs a fresh rule 5 approval and a fresh hash check; the owner may delete it.
- **A3 — local absolute paths** in four committed record lines (section 4). They expose a username only. Use repo-relative or `../agentic-sdlc-playbook` paths in future records.
- **A4 — open exit-134 item** (recorded in STATE, observed with the now-removed judge session loaded). This is not a security issue, and the code that produced it is gone. Keep it filed against the existing crash item.

## Recommendation

**GO for the Release Gate** (the gate itself will rule "not releasable": the bars were never met). Nothing blocks on security or privacy grounds. The net product change is empty, and the single safety-control edit is the exact owner-approved INV-4 text and true of the code.
