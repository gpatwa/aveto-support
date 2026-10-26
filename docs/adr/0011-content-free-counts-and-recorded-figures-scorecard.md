# ADR 0011: Usage is counted in memory without content; the scorecard shows only recorded figures from a committed file

- **Status:** proposed
- **Date:** 2026-10-26
- **Slice:** `runs/polished-chat-experience/` (tech spec `05-tech-spec.md` sections 3.7 and 3.8)

## Context

The intent asks for counts "for the customer evidence" (visits, questions asked, answered versus refused, clicks to the docs) with no question text and no identifiers beyond what the service already keeps, computed in the service, and for a quality scorecard "built from recorded figures only", where "a line with no record behind it is not shown". The service has no database and must not store or log questions. The image is built once per release, and `runs/`, `docs/` and `evals/` are not in it.

## Decision

- **Counts:** `aveto_service/counts.py` keeps four integers (visits, answered, refused, docs clicks) and the time the app was built, in memory. Callers pass only an outcome or nothing. The docs-click beacon (`POST /count/docs-click`) counts only an empty, same-origin request, at most 60 in a rolling hour across all visitors, and reads no address. No count writes a log line. Counts reset with every restart, scale to zero and revision; the page says "since the service last started".
- **Scorecard:** `GET /scorecard` renders `aveto_service/scorecard.toml`, a committed file in which every row names its record (a repository path) and a basis that starts "Measured" or "Recorded", with labels limited to the owner-seen copy deck. The reader fails closed; a test checks that every named record exists. Rows with no record are not written, so they are not shown. The service's own measurements on the page are the counts and the start time only.

## Alternatives considered

- **Per-event log lines aggregated in Log Analytics.** Rejected: a new log shape, an outside tool, and closer to storing per-request data than the intent allows.
- **Persisted counters (a file or a database).** Rejected: out of scope (an earlier slice's decision D1 keeps counters in memory) and a new data store.
- **A per-visitor limit on the beacon.** Rejected: it would read and keep the visitor's hashed address for a vanity count; a global cap bounds inflation without any identifier.
- **In-service cold-start and latency figures.** Not added: the process cannot see the container start a visitor waits through, and a server-side latency would sit beside the recorded client-side figure under the same label. Recorded measurements, with date and method, are used instead.
- **Figures read from `runs/` at runtime.** Impossible: `runs/` is not in the image.

## Consequences

- No question, address or per-event record exists anywhere for the counts; the numbers are small and reset often, and the page says so.
- Visits are page loads (reloads count); clicks can be inflated by at most 60 an hour.
- A new figure reaches the page only through a commit and a new image; figures measured after a build (live timings, the rollback rehearsal) appear one release later.
- Revisit if the owner wants lifetime totals (needs a store and a decision) or wants the counts off the public page (render-only change).
