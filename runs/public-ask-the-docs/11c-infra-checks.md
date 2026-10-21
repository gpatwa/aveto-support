# Stage 11c: infra checks (Backend Architect, depth standard, read-only, no deploy)

Date 2026-10-21. Nothing in Azure was created or changed. Only `az bicep build`, `az role definition list`, `az keyvault show`, `az acr check-name`, `az deployment group what-if`, and read-only `docker buildx imagetools inspect`.

## Files written
`Dockerfile`, `.dockerignore`, `tests/test_infra_static.py` (start: the hand-off text in `11-infra-note.md`).
Corrections to that text: both base images and the uv image are now pinned by digest (confirmed read-only below); test names aligned to spec §10 (`test_dockerfile_static`, `test_dockerignore_excludes_models_index`); added assertions (uvicorn target, `--no-access-log`, `ingest` step, digest pin); the registry test no longer requires `anonymousPullEnabled: false` (see finding F2) and instead fails on `true`.

## Image pins (confirmed, read-only)
- `docker buildx imagetools inspect python:3.12-slim-bookworm` -> index digest `sha256:6a0e06f5ba0b373d051aabd3fffb9b873f27f9a2a3a14bcbe37dee6f0e3bbc70` (used).
- `docker buildx imagetools inspect ghcr.io/astral-sh/uv:0.9.7` -> exists, index digest `sha256:ba4857bf2a068e9bc0e64eed8563b065908a4cd6bfb66b531a9c424c8e25e142` (used); `uv --version` = 0.9.7.

## Azure checks
| # | Command | Output | Verdict |
|---|---|---|---|
| 1 | `az bicep build --file infra/main.bicep --stdout >/dev/null` | exit 1. ERROR BCP265 (169,47) `environment` is not a function; WARNING BCP037 (62,5) `anonymousPullEnabled` not allowed on RegistryProperties; WARNING BCP318 (239,40) `app` may be null | FAIL (findings F1 to F3) |
| 2 | `az role definition list --name "Key Vault Secrets User" --query "[].name" -o tsv` | `4633458b-17de-408a-b874-0445c86b69e6` | PASS: equals spec §7 and `infra/main.bicep` line 46 |
| 3 | same for `AcrPull` | `7f951dda-4ed3-4680-a7ca-43fe172d538d` | PASS: equals spec §7 and line 47 |
| 4 | `az keyvault show -n kv-aveto-ask-gp --query properties.enableRbacAuthorization -o tsv` | `true` | PASS: no Charter stop 9.1 |
| 5 | `az acr check-name -n acravetoaskgp` | `nameAvailable: true`, loginServer `acravetoaskgp.azurecr.io` | PASS |
| 6 | `az deployment group what-if -g rg-aveto-ask -f infra/main.bicep -p @infra/main.parameters.json -p deployApp=false` | stopped by the same compile error BCP265, no what-if result | FAIL (blocked by F1) |
| 6b | Same what-if on a scratch copy (outside the repo) with only F1 and F2 patched (rename symbol `environment` to `caEnv`, delete the `anonymousPullEnabled` line), `deployApp=false` | compiles (exit 0); "6 to create, 1 to ignore": identity id-aveto-ask, registry acravetoaskgp, workspace log-aveto-ask (30 d, 0.5 GB cap), environment, role assignment on the registry (AcrPull GUID), role assignment on the vault (KV Secrets User GUID); vault kv-aveto-ask-gp is "ignore" (existing, untouched) | PASS for the patched copy; evidence that F1 and F2 are the only blockers for step 1 |
| 6c | Same scratch copy, `deployApp=true imageTag=abc123abc123 killSwitch=on configureLogRetention=true` | "9 to create, 1 to ignore": the above 6 plus ca-aveto-ask and the two `_CL` tables. what-if does not check that the image exists or the tables exist at deploy time | PASS for the patched copy (unconfirmed: the real create) |

## Findings for Cloud Deployment (`infra/main.bicep`; not fixed by me)
- F1 (blocking) `infra/main.bicep` lines 98 and 151, 169: the resource symbol `environment` (line 98, used at 151 as `environment.id`) shadows the `environment()` function used at line 169, giving BCP265. Rename the symbol (for example `caEnv`) at lines 98 and 151.
- F2 `infra/main.bicep` line 62: `anonymousPullEnabled: false` is not in the ACR 2023-07-01 `RegistryProperties` type (BCP037) and anonymous pull is off by default (and is not offered on Basic). Remove the line, or move to an API version that has it if the spec's "anonymous pull off" must be explicit. The test now accepts either.
- F3 `infra/main.bicep` line 239: `output appFqdn string = deployApp ? app.properties...` raises BCP318 (app may be null). Use the safe-access form, e.g. `app.?properties.?configuration.?ingress.?fqdn ?? ''`, or drop the warning knowingly.
- F4 (informational, unconfirmed) `az bicep` is not the newest (v0.48.1 available); not a defect.
- Note for stage 17: what-if cannot confirm that `ContainerAppConsoleLogs_CL` exists before first ingestion (step 4); unconfirmed until run.

## Image
Docker client is present but the daemon is not running (`failed to connect to the docker API at unix:///Users/gopalpatwa/.docker/run/docker.sock`). **The image is unbuilt.** Nothing about ingest-in-build, image size, runtime start, or the venv path surviving the stage copy is verified; first test is `az acr build` at stage 17. Unconfirmed: that `uv run --no-sync python -m aveto_support ingest` works from the `Dockerfile` context (files copied: pyproject, uv.lock, aveto_support, aveto_service, prompts, docs-source.toml, evals/calibration-offtopic.toml).

## New tests, failing first
The base commit has no `Dockerfile`, `.dockerignore` or test file (module absent, nothing to pass). Mutation checks against the new tests, each restored afterwards (git status shows `infra/` unmodified):
- `USER 10001` -> `USER root`: `test_dockerfile_static` FAILED.
- runtime base without digest: `test_dockerfile_static` FAILED.
- appended `Microsoft.Storage/storageAccounts` resource to main.bicep: `test_bicep_resources_are_c83` FAILED.
Tests added: 7 (`test_bicep_resources_are_c83`, `test_bicep_kill_switch_default_on`, `test_bicep_scale_and_ingress`, `test_bicep_registry_private`, `test_bicep_no_secret_literals`, `test_dockerfile_static`, `test_dockerignore_excludes_models_index`).

## Regression
`uv sync --locked && uv run mypy && uv run ruff check && uv run pytest`: mypy clean (45 files), ruff clean, 591 passed, 12 deselected.
