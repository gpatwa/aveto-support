# Approval Request 1 — network fetch in the build/test path

- **Slice:** docs-retrieval
- **Rule:** HUMAN_APPROVAL_RULES §5 — "Adding a network call to the build / test / commit path."
- **Requested:** 2026-09-27T02:29:54Z, at Intake, before any implementation.

## What

Allow the slice to ship code that fetches the markdown of
`gpatwa/agentic-sdlc-playbook` at commit
`3a83b669a8b53dfdff869a1bbe361bdb156e3a13` from GitHub over the network:

- from the `ingest` command, run locally, and
- from the new GitHub Actions workflow, which runs ingest and the eval score on
  every push and pull request.

This is the only network access. It is read-only, targets one public repo at
one pinned commit, and uses no credentials. No model is called.

## Why

The intent's "Done means" requires ingest to read the pinned docs and CI to
check the eval score on every push. Both need the docs. §5 exists because a
network call in the test path changes what every run depends on. Here the
concern is availability (a GitHub outage or rate limit fails CI), not cost:
nothing is metered.

## What is reversible if denied

If denied, the slice can instead **vendor a snapshot** of the pinned docs into
the repo as test data. Tests and CI then run offline, and ingest against a
live repo becomes a manual command outside CI. The "Done means" line saying
the only network access is fetching the pinned docs stays true either way.

## The smallest request

One action: read-only fetch of one public repo at one pinned commit, in ingest
and in CI. It does not cover any other host, any model, or any credential.
