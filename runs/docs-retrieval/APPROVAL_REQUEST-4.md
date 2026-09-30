# Approval Request 4 — change a safety control: INV-5 and INV-4 wording (rule 4)

- **Slice:** docs-retrieval
- **Rule:** HUMAN_APPROVAL_RULES §4 — changes to safety controls (the plan must call it out and the owner must approve before implementation)
- **Requested:** 2026-09-29T05:25:45Z. Only meaningful if Requests 2 and 3 are approved.

## What

Replace the current text of two invariants in `.agentic/SAFETY_INVARIANTS.md` with the
Architect's draft (runs/docs-retrieval/02-tech-spec.md, section 'Retrieval — variant embed-v3', "3. What it changes in the safety and intent record"):

**INV-5, from** "The product's only network egress is the HTTPS archive fetch of the
configured GitHub repo at a full 40-hex commit. Redirects go only to `github.com` /
`codeload.github.com`, and no credentials are sent."
**to** two read-only HTTPS GET downloads, both only by `ingest`: (a) the GitHub
archive at a full 40-hex commit, redirects only to `github.com` / `codeload.github.com`;
and (b) the pinned embedding-model files from `huggingface.co` at a full 40-hex
revision, redirects only to hosts under `hf.co`. Every model file is checked against
its committed sha256 before use; on a mismatch it is deleted and ingest fails. Trust
rests on the hash, never on the host. No credentials are sent. **No question,
passage or user text ever leaves the machine.** `retrieve`, `eval` and the default
test suite make no network calls. (Host matching is exact: `huggingface.co`, or a host
ending `.hf.co`; `hf.co.evil.example` and `evilhf.co` are refused.)

**INV-4, add one sentence** (nothing removed): "A model may be used only to rank
passages and to decide confidence. It never produces, selects fragments of, or
alters the text returned." — this strengthens it.

## Why

INV-5 as written forbids the Request 3 download; without this change the model cannot
be fetched compatibly with the invariants. The change widens allowed egress to one
more named host family and adds a hash check, and keeps "no credentials" and
"nothing leaves the machine".

## What is reversible if denied

The text stays as it is (this request edits nothing until approved), and embed-v3
is dropped. If approved and later withdrawn: revert the file.

## The smallest request

The exact INV-5 and INV-4 wording above. Not any wider host, not any credential,
and not the intent amendments (yours to make on `main`).
