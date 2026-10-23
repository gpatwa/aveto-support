# APPROVAL_RECORD-3: the page's AI-disclosure wording and privacy statements approved (owner, typed, after the run)

Approver: **Gopal Patwa** (owner, in the driving session). Owner's words: "I approve the Article 50 wording and the privacy notice as served in PR #5 (render.py at head dbc8b81). Record it as an approval in END_REVIEW."

Recorded at: 2026-10-23T06:37:20Z (`date -u` when recorded; the owner's message carries no timestamp).

## What was approved (verified before recording)
- Head of PR #5 and of `origin/claude/public-ask-the-docs`: `dbc8b8190900`.
- `aveto_service/render.py` at that head: sha256 `a0bc17f0f4fa229675b78bd7ff83fe8477387a755bc8c2700dfd47a716e5cbfb`. It is byte-identical to `render.py` in the image that is live (`aveto-ask:879cae23690b`, built from what is now commit `8ebf76c6848d`), and the text served by the live service matches it word for word (compared 2026-10-22).
- The wording, as served on `GET /`:
  - Intro: "Verbatim passages from Aveto's docs; an AI model decides only whether they answer. Nothing on this page is written by an AI model."
  - "You get passages copied word for word from the docs, with the file and line numbers, or a plain note that the docs don't answer your question."
  - "Limits: 10 questions an hour and 500 characters a question. The service pauses for the day when the day's allowance is used."
  - "Please don't put personal or confidential information in your question."
  - "This service does not store or log your question. To decide whether the passages answer, your question and the passages found are sent to Anthropic, the company that makes the AI model. Anthropic handles them under its own terms, which this page does not control."
  - "To apply the limits we read your address, then keep only a scrambled form of it, the time and the outcome for 7 days. The service runs in the United States (Azure, East US 2)."
  - "The docs are in English. One question at a time; nothing is remembered between questions."

## What this approval is, and is not
- It is the owner's acceptance of the AI-disclosure wording (the intro line, which says an AI model is involved and that nothing shown is AI-written) and of the privacy statements above, as the page serves them. It closes release-checklist items 06 R1 and R2 and 07 G1, G5 and G8 as **accepted by the owner** (the "privacy notice" is these on-page statements; no separate notice page or link exists, which the UI amendment left to the owner's decision).
- It is **not** a legal conclusion by any agent: whether the EU AI Act's Article 50 duty applies to this service, whether a hashed address is personal data, and whether the wording satisfies either remain the owner's own judgement, now given. The run's own finding is unchanged: the wording says what the service does; it was not reviewed by a lawyer.
- It covers `render.py` at `dbc8b8190900` only. A later change to that wording needs a new approval.
