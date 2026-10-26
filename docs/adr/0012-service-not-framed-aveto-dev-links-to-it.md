# ADR 0012: The ask service is not framed by aveto.dev; the site links to it

- **Status:** accepted (decided by the owner on 2026-10-26, in `intents/polished-chat-experience.md`, option (a))
- **Date:** 2026-10-26
- **Slice:** `runs/polished-chat-experience/` (tech spec `05-tech-spec.md` section 1)

## Context

The intent wants the service shown on aveto.dev. The service's pages are sent with `Content-Security-Policy: ... frame-ancestors 'none'` (`aveto_service/pages.py`), so no other site can frame them. Two options were put to the owner: (a) keep the service on its own address and show it on aveto.dev as a recording plus a button; (b) allow framing by `https://aveto.dev` only.

## Decision

Option (a). `frame-ancestors 'none'` and every other response header stay byte-identical. aveto.dev carries a recording and a link that opens the service in its own tab; that site change is a separate commit in the playbook repository with wording the owner approves.

## Alternatives considered

- **(b) Allow `frame-ancestors https://aveto.dev`.** Not taken in this slice: it changes a security header (a Charter safety-control item needing its own approval and Security Review), and the page's protections (form posts, the 303 to a result page, `Referrer-Policy: no-referrer`, the same-origin check on `POST /ask`) were reviewed for a top-level page; framed, the cross-site rule and clickjacking defence would need re-reading. It remains possible as a separate later intent.

## Consequences

- No header, Charter safety control or Security Review item for framing in this slice; a test pins the headers byte for byte.
- A visitor leaves aveto.dev to use the service.
- Revisit only through a new intent for option (b), naming the one origin and no wildcard.
