# Support requests — public-ask-the-docs

Appended by the Orchestrator, per AGENTS.md ("Two sessions"). Nothing was patched or worked around; the slice carries on by routing the spec fault back to its owner.

## SR-1 — 2026-10-21 — Cloud Deployment cannot do what a tech spec can assign it (stage 11)

**File:** `.claude/hooks/write-scope-guard.mjs` (EXTRA table, `cloud-deployment`: `.azure/`, `infra/`, `azure.yaml`) and `.claude/agents/cloud-deployment.md` (tools: Read, Write, Edit, Grep, Glob — no Bash).
**What happened:** the Architect's tech spec §12 assigned Cloud Deployment `Dockerfile`, `.dockerignore` and `tests/test_infra_static.py`, plus read-only `az` checks (`az bicep build`, `az role definition list`, `what-if`) and, at stage 17, the deploy commands. The guard denied the three files (outside `infra/`); the role has no shell, so none of the `az` commands ran and the Bicep is uncompiled.
**Expected:** a role that the playbook names as the deploy role should be able to produce the image definition for its own deploy and to run (at least) read-only validation, or the Architect brief should say it cannot be assigned them. Our reading: the guard is correct as designed; the fault is the spec assigning outside the role's scope, but the pack gives no stage that can validate Bicep or run the deploy except the Orchestrator's own shell.
**Routed now:** (1) Architect amends §12 to give `Dockerfile`, `.dockerignore`, `tests/test_infra_static.py` and the read-only Azure checks to the Backend Architect (has Bash); `infra/*` stays with Cloud Deployment, who fixes any lint finding. (2) Stage 17's Charter-covered commands (C8.3) are run by the Orchestrator's session, which has the shell, with Cloud Deployment's note as the runbook.
**Ask of the support session:** say whether a shell-less Cloud Deployment role is intended; if not, a pack change. No reply needed for this run to proceed.
