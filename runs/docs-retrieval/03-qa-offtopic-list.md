# QA: off-topic calibration list (docs-retrieval, embed-v3)

Author: QA Evidence, depth standard. File: `evals/calibration-offtopic.toml`. Uncommitted; the Orchestrator commits and freezes it and records the sha256 (none computed here).

- **Count:** 59 `[[question]]` entries (`o01`..`o59`), `pinned_commit` = 3a83b669a8b53dfdff869a1bbe361bdb156e3a13. Parses as TOML, 59 unique questions.
- **Unanswered at the pinned commit:** for each question I chose 1 to 4 subject terms and ran
  `git -C /Users/gopalpatwa/opt/agentic-sdlc-playbook grep -n -i -E "<terms>" 3a83b669a8b53dfdff869a1bbe361bdb156e3a13 -- '*.md'`
  (local git only, no network). Zero hits for 44 questions. For the 15 with hits (for example changelog, keyboard, registry, latency, certificate, wildcard, benchmark, translate, uptime, emoji, OAuth) I read the hits: each is an unrelated sense, so those are intentional hard negatives.
- **Replaced:** 1 replaced because the docs answer it in part (a "put my site behind Cloudflare" question; `docs/DEPLOYMENT.md` and README describe Cloudflare Pages). A further 12 first-draft questions were dropped for dev-set subject overlap (see below) or redundancy, and 9 fresh ones were added.
- **Non-overlap with `evals/retrieval.toml` (read only, not edited):** compared by subject against all 30 dev questions. Dropped drafts on the same subject as a dev question: platform support (Raspberry Pi, Chromebook, phone app; cf. u02 Windows), editor plugins (IntelliJ, Neovim; cf. u04 VS Code), alternative git host (Bitbucket; cf. u03 GitLab), SSO/account (Okta; cf. u05), Copilot/autocomplete (cf. a14 other tools), free CI minutes (pricing; cf. u01). No question mentions licence pricing, Windows, GitLab, VS Code, passwords, Slack, AWS, Cursor/Codex, ADRs, tokens or approvals. This is a judgement on subject, not a mechanical test.
- **Could not check:** overlap with the owner's fresh held-out set. It is not in the repo and I did not look for it. That check is the owner's. Also not checked: the docs in formats other than `*.md` at the pinned commit (the configured source), and how embed-v3 actually scores these (no eval run, by instruction).
