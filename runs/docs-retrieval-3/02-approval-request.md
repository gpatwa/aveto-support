# Approval request — docs-retrieval-3 (slice A): the reranker model (A1) and the INV-5 wording (A2)

> Drafted by the Software Architect, 2026-09-30, for the Orchestrator to put to the owner (Gopal Patwa). Per `docs/HUMAN_APPROVAL_RULES.md` ("How to ask for approval", "What explicit approval means"). Spec: `runs/docs-retrieval-3/02-tech-spec.md`.
>
> **Two separate asks. Answer each on its own.** A yes to A1 is not a yes to A2, and neither is a yes to anything wider. Only the owner's own words in the Orchestrator's session count; a relayed message, silence or "looks good" does not. **Nothing is downloaded, installed or edited until both are answered yes and recorded** (`APPROVAL_RECORD-<n>.md` and the STATE Approvals table).
>
> **A1 is not ready to answer until every `TO BE FILLED` cell below is filled.** The Architect has no network tool and opened no model page. The Orchestrator fills each cell from the model repository's published metadata at the pinned revision (the file page's "SHA256" / LFS pointer and size, and the commit id), names where each figure came from, and only then shows A1 to the owner. The owner approves **exact hashes**, not "whatever is downloaded" (scope section 5, option (i)).

---

## A1 — Approve this specific reranker model (rule 5)

**What.** Let `ingest` download, and `retrieve`/`eval` run locally on CPU, exactly these two files of exactly this model at exactly this revision, and nothing else from it:

| Item | Value |
|---|---|
| Model | `cross-encoder/ms-marco-MiniLM-L6-v2` — canonical id **CONFIRMED** by the Hub API (`id` = `cross-encoder/ms-marco-MiniLM-L6-v2`); the hyphenated `-L-6-` name does not resolve |
| Source repository URL | `https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2` (confirmed) |
| Revision (full 40-hex commit) | `233902d25c440f23af6f7d6e94d2946bac0bee0a` (Hub API `sha`, `last modified 2026-08-09T15:22:24Z`) |
| Download host | `huggingface.co`; URL form `https://huggingface.co/<model>/resolve/<revision>/<file>`; redirects followed only to hosts under `hf.co` (for example `us.aws.cdn.hf.co`, `cas-bridge.xethub.hf.co`); any other host is refused. Same host rule as the embedding model today |
| Licence | Apache-2.0 (Hub API tag `license:apache-2.0`, confirmed). See "Licence note" below |
| Runtime | `onnxruntime` + `numpy` (already dependencies); no PyTorch; no `trust_remote_code`; no new package; `pyproject.toml` and `uv.lock` unchanged |
| What it does | reads (question, passage) and returns one number per pair, used only to re-order the top 20 files of the existing ranking. It cannot produce text (a classification head, one logit) |

**Exact file list:**

| File (path in the repo) | Size (bytes) | sha256 | Used for |
|---|---|---|---|
| `onnx/model.onnx` (fp32; **not** any `model_O*.onnx` or `model_*int8*.onnx` variant) | 91,011,230 | `5d3e70fd0c9ff14b9b5169a51e957b7a9c74897afd0a35ce4bd318150c1d4d4a` (Hub LFS metadata) | the model |
| `vocab.txt` | 231,508 | `07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3` (not read from the file: the Hub's git blob id for this `vocab.txt` is `fb140275c155a9c7c5a3b3e0e77a9e839594a938`, identical to bge-small's pinned `vocab.txt` at its revision, so the bytes are identical and bge's committed sha256 applies) | the tokenizer |

**Checks the Orchestrator makes when filling the cells (not files we download):**

| Check | Expected | If not |
|---|---|---|
| `vocab.txt` sha256 equals `07eced37…2038a3` | yes | **Do not put A1 to the owner.** The proposal is void (the existing tokenizer golden test would not cover it); hand back to the Architect |
| `tokenizer_config.json` at the revision says `do_lower_case: true` | yes | same: hand back |
| `onnx/model.onnx` exists at the revision | yes | same: hand back |
| `config.json` architecture is `BertForSequenceClassification`, one label, no `auto_map` (no remote code) | yes | same: hand back |
| `onnx/model.onnx` size is under 200,000,000 bytes (the existing download cap, not raised) | yes (~91 MB) | same: hand back |

**Why, and which rule.** Rule 5: a new model enters the retrieval path, and `ingest` gains a new network download (the build path), which changes what every fresh setup fetches. The intent says the reranker "needs rule 4 and 5 approval of the specific model before anything is installed or downloaded". Rule 6 does **not** fire: same host as today, only pinned files are fetched, no question, passage or user text is sent, no credentials (spec, "Rule 6 check"). The INV-5 change this download requires is asked separately as A2.

**Ongoing cost the owner is agreeing to.** No API key, no token spend, no money. About 91 MB more to download on each fresh model cache (and, later, in CI). About 2 to 2.5 seconds of one CPU core per question in `retrieve`/`eval` (an estimate; the Implementer measures it). About 1 second to load per process.

**Licence note (to weigh, not decided by an agent).** The model weights are published under Apache-2.0. The model was trained on MS MARCO, whose terms describe the data as for non-commercial research use. Whether that restriction reaches a model trained on it is a legal question the Architect cannot settle. This product is a public template others may deploy. Saying yes to A1 lets the slice build and score the reranker; the owner may still want a legal view before any release (slice B's Release Gate).

**If A1 is denied.** Nothing is downloaded, installed or written; `main` and this branch's product code stay exactly as they are (`file-rrf-v1`). Implementation does not start. Choosing a different model needs a fresh Architecture spawn (about 110k), which does not fit slice A's 50k headroom, so the Orchestrator stops and asks the owner with the numbers (spent, estimate, budget). Alternatively the slice closes with nothing changed and the reranker question goes to a new intent.

**Smallest request.** Approve downloading and running these two files, at this revision, with these hashes. Not: other files in the repository, a later revision, a quantised variant, or any other model.

> **A1 answer (owner's own words):** _______________________

---

## A2 — Approve the exact safety-invariant wording (rule 4)

**What.** Replace the INV-5 block and the INV-4 enforcement note in `.agentic/SAFETY_INVARIANTS.md` with the text below, **verbatim**. The Implementer applies it exactly as written; any later change to these words is a new A2.

**Why, and which rule.** Rule 4: INV-5 is the product's egress and model-integrity control. It names exactly two downloads and, in (b), only the embedding model; a third model's files cannot be fetched without changing it. The INV-4 invariant itself is **not** reworded (the reranker only ranks, which it already allows); only its list of enforcing tests grows so the reranked path has named tests.

### A2.1 — INV-5, full proposed text (replaces the whole current INV-5 bullet)

```
- **INV-5** — The product's network egress is limited to two kinds of
  read-only HTTPS GET download, both made only by `ingest`:
  (a) the archive of the configured GitHub repo at a full 40-hex commit, with
  redirects only to `github.com` / `codeload.github.com`; and
  (b) the pinned files of exactly two local models — the configured embedding
  model (`docs-source.toml`) and the reranker model pinned in
  `aveto_support/rerank.py` — each requested from `huggingface.co` at its own
  full 40-hex revision, with redirects only to hosts under `hf.co` (for example
  `us.aws.cdn.hf.co`).
  Every model file is checked against its committed sha256 **before it is
  used**. On a mismatch the file is deleted and ingest fails. Trust rests on the
  hash, never on the host. No credentials are sent. **No question, passage or
  user text ever leaves the machine.** `retrieve`, `eval` and the default test
  suite make no network calls.
  *(Enforced by `test_redirect_to_other_host_refused`,
  `test_hf_redirect_outside_hf_co_refused`, `test_short_sha_rejected`,
  `test_model_revision_must_be_40_hex`,
  `test_model_hash_mismatch_rejected_and_deleted`,
  `test_cached_file_rehashed_before_use`,
  `test_retrieve_is_offline_with_cached_model`,
  `test_reranker_revision_must_be_40_hex`,
  `test_reranker_hash_mismatch_rejected_and_deleted`,
  `test_reranker_cached_file_rehashed_before_use`,
  `test_reranker_redirect_outside_hf_co_refused`,
  `test_retrieve_is_offline_with_cached_reranker`, and the autouse network
  block.)*
```

What changes against today's text: "two read-only HTTPS GET downloads" becomes "two kinds of read-only HTTPS GET download"; (b) "the pinned files of the configured embedding model, requested from `huggingface.co` at a full 40-hex revision" becomes the two-model wording above; five reranker tests are added to the enforcement list. Every other sentence is unchanged.

### A2.2 — INV-4 enforcement note, full proposed text (replaces only the italic note under INV-4; the invariant's sentences are unchanged)

```
  *(Enforced by `test_result_invariant_enforced`,
  `test_retrieved_text_is_verbatim_slice_of_file`,
  `test_hybrid_hits_are_verbatim_passages`, and, for the reranked method,
  `test_reranked_hits_are_verbatim_passages`,
  `test_reranked_result_invariant_enforced` and
  `test_reranker_returns_only_scores`.)*
```

What changes: "and a new `test_hybrid_hits_are_verbatim_passages`" loses "a new" (the test exists now) and three reranked-path tests are added. No existing enforcing test is retired or weakened.

**If A2 is denied.** `.agentic/SAFETY_INVARIANTS.md` is not touched. Without the INV-5 change the reranker's files may not be fetched, so Implementation does not start even if A1 is yes; the Orchestrator stops and asks the owner with the numbers. If the owner wants different words, the owner's wording becomes the new A2 text and is approved as written. If the owner approves A2.1 but not A2.2, INV-5 is applied and the INV-4 note stays as it is (the tests are still written and run; they are just not listed there).

**Smallest request.** Approve these exact words for INV-5 (A2.1) and, separately if preferred, for the INV-4 note (A2.2). Not: any other edit to `SAFETY_INVARIANTS.md` (the "PARTIAL" header, the close-out's open abstention note, or the stale "plain code" wording elsewhere are out of this slice).

> **A2 answer (owner's own words):** _______________________

---

## What happens after

- **Both yes, recorded:** Implementation (backend-architect, one fresh spawn, ~130k) pins exactly the approved id, revision and hashes into `RerankParams`, fetches only in `ingest`, applies A2 verbatim, runs the full regression, and never runs `eval` on any `evals/` file. Then the freeze.
- **Either no, or A1 cells unfilled:** stop. No download, no code, no invariant edit.


---

## Orchestrator's fill-in (2026-10-01, from the Hugging Face Hub API only; **no model file was downloaded or opened**)

Source: `GET https://huggingface.co/api/models/cross-encoder/ms-marco-MiniLM-L6-v2/revision/233902d25c440f23af6f7d6e94d2946bac0bee0a?blobs=true`, and the same call for `BAAI/bge-small-en-v1.5` at its pinned revision `5c38ec7c…`. It returns metadata only (sizes, git blob ids, LFS sha256).

| Check | Result |
|---|---|
| `vocab.txt` equals bge-small's | **Yes** (same git blob id `fb140275…a938`, same size 231,508) |
| `onnx/model.onnx` exists, fp32 | Yes: 91,011,230 B (< 200,000,000 cap); LFS sha256 above. The `model_O*.onnx` and `qint8`/`quint8` variants are not requested |
| `config.json` architecture | `BertForSequenceClassification`, model_type `bert`, no `auto_map` in the Hub's parsed config |
| `tokenizer_config.json` `do_lower_case: true` | **Reported true by the Aveto AI SDLC session** (its own read-only fetch, 2026-09-30: BertTokenizer, `do_lower_case` true, `model_max_length` 512; file sha256 `a5c2e5a7…5fd8`). The Orchestrator did not open the file itself. The Implementer re-verifies it first after approval and hands back if it differs. That session also reports `config.json` as BertForSequenceClassification, 6 layers, hidden 384, and the `model.onnx` resolve answering 302 to `us.aws.cdn.hf.co` (under `hf.co`) |
| Unpinned alternates | none: pin is the full commit, so a later push to the repo changes nothing |

The owner approves these exact hashes. The vocab hash is derived by identity with a file the repo already pins, not by hashing the file itself; the Implementer's tests recompute it on download as for every model file.
