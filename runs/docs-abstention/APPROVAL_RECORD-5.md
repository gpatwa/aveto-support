# Approval record 5 — rule 5 (model) and rule 4 (INV-4, INV-5, A1 line)

- **Approver:** Gopal Patwa, typed directly in the driving session
- **When (UTC):** 2026-10-09T17:05:20Z
- **In the owner's words:** "approve all, including the A1 line"
- **What "all" covers** (the four requests shown to the owner in this session immediately before, verbatim from `02-tech-spec.md` sections 8.1, 8.2, 8.4):
  1. **Rule 5:** download and use `cross-encoder/qnli-electra-base` at revision `c7dea87c98b2269a935686c31336e97e837cbbeb`, files `onnx/model.onnx` (438,212,375 bytes, sha256 `595b37541289472b7b784ed2af05bcad6000991a2657aeee4f92f68b42ae61d9`) and `vocab.txt` (231,508 bytes, sha256 `07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3`), Apache-2.0 per the model card (licence decision: APPROVAL_RECORD-4.md), as the default-path answerability judge fetched by every `ingest`. ONNX input names are checked at first load; if they do not match, the model is not used.
  2. **Rule 4, INV-4 item 4-i** (the "exactly no confident match ... and the name of the signal that decided" clause).
  3. **Rule 4, INV-4 item 4-ii** (the judge sentence).
  4. **Rule 4, INV-5:** three local models (embedding, judge, reranker); default `ingest` fetches embedding + judge, reranker only with `--with-reranker`; seven judge tests appended to INV-5's list; revision kept in `judge.py` and ADR 0007, not in the invariant's prose.
  5. **The optional A1 line** in INV-5: "On the default path, `retrieve` and `eval` load only the cached embedding model and judge, and make no network call (`test_retrieve_is_offline_with_cached_judge`)."
- **Exact text** is the text in `runs/docs-abstention/02-tech-spec.md` sections 8.1, 8.2 and 8.4 at commit of this record; nothing may be applied that differs from it. It is applied by the Orchestrator in the method commit, not before the code.
- **Not approved:** push, merge, PR, deploy, any other model or download, any budget raise.
