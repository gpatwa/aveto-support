# Stage 11 infra note: public-ask-the-docs (Cloud Deployment, depth standard, no deploy)

## Status: PARTIAL, BLOCKED by two role-boundary limits (not Charter stops)

1. **Write scope.** `.claude/hooks/write-scope-guard.mjs` allows this role `runs/`, `.azure/`, `infra/`, `azure.yaml` only. It refused `Dockerfile`, `.dockerignore` and (by the same rule) `tests/test_infra_static.py`, which tech spec section 12 assigns to me. I did not work around it. The full proposed text of all three is in "Hand-off files" below; another role (or the Orchestrator) must write them verbatim. Spec section 12 and the write guard disagree: route to the support session.
2. **No shell.** My tools are Read, Write, Edit, Grep, Glob. None of the read-only `az` checks, nor `uv run mypy/ruff/pytest`, could run. Every check below is **NOT RUN**; the Orchestrator (or a role with a shell) must run them. Nothing was verified against Azure.

No Charter stop was hit: every resource and action below is on C8.3's list.

## Built (written to disk)

- `infra/main.bicep`: exactly the C8.3 types and nothing else: `Microsoft.ManagedIdentity/userAssignedIdentities` (id-aveto-ask), `Microsoft.ContainerRegistry/registries` (acravetoaskgp, Basic, admin off, anonymous pull off), `Microsoft.OperationalInsights/workspaces` (log-aveto-ask, PerGB2018, 30 d, 0.5 GB/day cap) with two `.../workspaces/tables` children (ContainerAppConsoleLogs_CL, ContainerAppSystemLogs_CL, 7/7, conditional on `configureLogRetention`), `Microsoft.App/managedEnvironments` (cae-aveto-ask), `Microsoft.App/containerApps` (ca-aveto-ask, conditional on `deployApp`), two `Microsoft.Authorization/roleAssignments`. The vault `kv-aveto-ask-gp` is an `existing` reference only (not created, not modified).
- Container App: Single revision mode, external ingress 8000, `allowInsecure: false`, 0.5 vCPU / 1 GiB, scale 0..1 with an HTTP rule of 10, startup/readiness/liveness probes on `/health`, secret by `keyVaultUrl` + identity, env `ANTHROPIC_API_KEY` (secretRef), `ASK_KILL_SWITCH`, `ASK_CLIENT_KEY`, `ASK_PRICE_IN_NANO_PER_TOKEN`, `ASK_PRICE_OUT_NANO_PER_TOKEN`, `ASK_MONTHLY_CAP_USD`. Env names match `aveto_service/settings.py`. `killSwitch` default `'on'`. No secret value anywhere.
- `infra/main.parameters.json`: `location: eastus2` only.
- No Application Insights, no Key Vault creation, no storage account.

## Checks (all NOT RUN, no shell)

| Command | Result |
|---|---|
| `az bicep build --file infra/main.bicep --stdout >/dev/null` | NOT RUN. Hand-written Bicep is unlinted: API versions (2023-01-31, 2023-07-01, 2023-09-01, 2022-10-01, 2024-03-01, 2022-04-01) are from memory. |
| `az role definition list --name "Key Vault Secrets User" --query "[].name" -o tsv` | NOT RUN. GUID `4633458b-17de-408a-b874-0445c86b69e6` used as in the spec: UNCONFIRMED. |
| `az role definition list --name "AcrPull" --query "[].name" -o tsv` | NOT RUN. GUID `7f951dda-4ed3-4680-a7ca-43fe172d538d` used as in the spec: UNCONFIRMED. |
| `az keyvault show -n kv-aveto-ask-gp --query properties.enableRbacAuthorization` | NOT RUN. STATE.md Setup log records the Orchestrator's earlier read-only check: `true`. |
| `az acr check-name -n acravetoaskgp` | NOT RUN. Name availability UNCONFIRMED. |
| `az deployment group what-if -g rg-aveto-ask -f infra/main.bicep -p @infra/main.parameters.json -p deployApp=false` | NOT RUN. |
| `uv run mypy && uv run ruff check && uv run pytest` | NOT RUN (no shell). Nothing of mine changes Python; the new test file is not yet on disk. |

## Stage-17 commands as they stand (identical to spec section 7)

```sh
RG=rg-aveto-ask; F=infra/main.bicep; P=infra/main.parameters.json; TAG=$(git rev-parse --short=12 HEAD)
az deployment group create -g $RG -f $F -p @$P -p deployApp=false
az acr build -r acravetoaskgp -t aveto-ask:$TAG --platform linux/amd64 -f Dockerfile .
az deployment group create -g $RG -f $F -p @$P -p deployApp=true imageTag=$TAG killSwitch=on
az deployment group create -g $RG -f $F -p @$P -p deployApp=true imageTag=$TAG killSwitch=on configureLogRetention=true
az deployment group create -g $RG -f $F -p @$P -p deployApp=true imageTag=$TAG killSwitch=off configureLogRetention=true
```

Note: the `imageTag` default is `unset`, so a first pass with `deployApp=false` needs no tag.

## Deviations from the spec

- Added a `dependsOn` of both role assignments on the app, so the identity can pull and read the secret at first start.
- Startup probe: `periodSeconds: 5`, `failureThreshold: 24` (2 minutes) to cover cold ingest-free start; readiness 10 s. Spec gave no numbers.
- `monthlyCapUsd` is an `int` (spec: "default 10"); the env gets `string(...)`.
- Dockerfile: uv stage `ghcr.io/astral-sh/uv:0.9.7` (the version in `.venv/pyvenv.cfg`; the image tag's existence is UNCONFIRMED); `UV_PYTHON_DOWNLOADS=never` so the venv uses the base image's Python and its path matches in both stages. `.dockerignore` also excludes `.agentic/`, `infra/`, `.gitignore`.

## Unconfirmed

- Bicep never compiled or what-if'd; all API versions and property names from memory.
- Role GUIDs, ACR name availability.
- Table retention below 30 days for `_CL` tables (spec says 4 to 730 from memory); `ContainerAppConsoleLogs_CL` exists only after first ingestion, so step 4 may fail before then.
- `workspace.listKeys()` in `environment` may raise a Bicep linter warning about secrets in outputs/properties; it is not an output.
- Ingress `X-Forwarded-For` behaviour; image digest of `python:3.12-slim-bookworm` (tag only); image size; cold-start time.
- The startup probe budget vs real model load time.
- `az acr build` build context: `.dockerignore` re-includes only `evals/calibration-offtopic.toml`; `docs-source.toml` must not be excluded (it is not).

## Hand-off files (write these verbatim; owner per spec section 12 is Cloud Deployment, blocked by the write guard)

### `Dockerfile`

```dockerfile
# public-ask-the-docs: container image (tech spec section 6). Built remotely by `az acr build`.
# Base by tag, not digest: no registry access at stage 11 (digest recorded from the build log at stage 17).
# uv 0.9.7 is the version recorded in the developer's .venv/pyvenv.cfg.

FROM ghcr.io/astral-sh/uv:0.9.7 AS uv

FROM python:3.12-slim-bookworm AS build
COPY --from=uv /uv /uvx /bin/
ENV UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never UV_PYTHON_PREFERENCE=only-system
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
COPY aveto_support/ aveto_support/
COPY aveto_service/ aveto_service/
COPY prompts/ prompts/
COPY docs-source.toml ./
COPY evals/calibration-offtopic.toml evals/calibration-offtopic.toml
# INV-5 (a) and (b) only: the pinned docs archive and the pinned embedding-model files, each sha256-checked
# by ingest itself. No reranker. Writes index/ and models/.
RUN uv run --no-sync python -m aveto_support ingest

FROM python:3.12-slim-bookworm AS runtime
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    ASK_INDEX=/app/index/docs-index.json \
    ASK_MODELS=/app/models
WORKDIR /app
COPY --from=build /app/.venv /app/.venv
COPY --from=build /app/aveto_support /app/aveto_support
COPY --from=build /app/aveto_service /app/aveto_service
COPY --from=build /app/prompts /app/prompts
COPY --from=build /app/index /app/index
COPY --from=build /app/models /app/models
USER 10001
EXPOSE 8000
CMD ["/app/.venv/bin/uvicorn", "aveto_service.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-access-log", "--log-level", "critical", "--no-proxy-headers", "--no-server-header", "--no-date-header"]
```

### `.dockerignore`

```
.git
.gitignore
.venv
.mypy_cache
.ruff_cache
.pytest_cache
models/
index/
runs/
.claude/
.aveto-judge/
.agentic/
tests/
tools/
docs/
intents/
evals/*
!evals/calibration-offtopic.toml
infra/
**/__pycache__
*.pyc
*.env
.env*
```

### `tests/test_infra_static.py`

```python
"""Static, offline checks of infra/main.bicep, the Dockerfile and .dockerignore (Charter C8.3)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BICEP = (ROOT / "infra" / "main.bicep").read_text(encoding="utf-8")
PARAMS = (ROOT / "infra" / "main.parameters.json").read_text(encoding="utf-8")
DOCKERFILE = (ROOT / "Dockerfile").read_text(encoding="utf-8")
DOCKERIGNORE = (ROOT / ".dockerignore").read_text(encoding="utf-8")

C83_TYPES = {
    "Microsoft.ManagedIdentity/userAssignedIdentities",
    "Microsoft.ContainerRegistry/registries",
    "Microsoft.OperationalInsights/workspaces",
    "Microsoft.OperationalInsights/workspaces/tables",
    "Microsoft.App/managedEnvironments",
    "Microsoft.App/containerApps",
    "Microsoft.Authorization/roleAssignments",
}
EXISTING_ONLY = {"Microsoft.KeyVault/vaults"}  # the owner's vault, referenced with `existing`

RESOURCE = re.compile(r"^resource\s+\w+\s+'([^'@]+)@[^']+'\s*(existing\s*)?=", re.MULTILINE)


def _code_lines(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//"))


def test_bicep_resources_are_c83() -> None:
    found = RESOURCE.findall(_code_lines(BICEP))
    assert found, "no resources parsed"
    assert len(found) == len(re.findall(r"^resource\s", _code_lines(BICEP), re.MULTILINE))
    for rtype, existing in found:
        if existing:
            assert rtype in EXISTING_ONLY, rtype
        else:
            assert rtype in C83_TYPES, f"{rtype} is not in Charter C8.3"
    created = [t for t, e in found if not e]
    for once in (
        "Microsoft.ManagedIdentity/userAssignedIdentities",
        "Microsoft.ContainerRegistry/registries",
        "Microsoft.OperationalInsights/workspaces",
        "Microsoft.App/managedEnvironments",
        "Microsoft.App/containerApps",
    ):
        assert created.count(once) == 1, once
    assert created.count("Microsoft.Authorization/roleAssignments") == 2


def test_bicep_kill_switch_default_on() -> None:
    assert re.search(r"param killSwitch string = 'on'", BICEP)
    assert re.search(r"@allowed\(\['on', 'off'\]\)\s+param killSwitch", BICEP)
    assert "killSwitch" not in PARAMS


def test_bicep_scale_and_ingress() -> None:
    assert re.search(r"minReplicas:\s*0\b", BICEP)
    assert re.search(r"maxReplicas:\s*1\b", BICEP)
    assert re.search(r"external:\s*true", BICEP)
    assert re.search(r"allowInsecure:\s*false", BICEP)
    assert "allowInsecure: true" not in BICEP
    assert re.search(r"activeRevisionsMode:\s*'Single'", BICEP)


def test_bicep_registry_private() -> None:
    assert re.search(r"adminUserEnabled:\s*false", BICEP)
    assert re.search(r"anonymousPullEnabled:\s*false", BICEP)


def test_bicep_no_secret_literals() -> None:
    for text in (BICEP, PARAMS, DOCKERFILE):
        assert not re.search(r"sk-ant-", text)
        assert not re.search(r"(?i)(password|secret|api[_-]?key|token)\s*[:=]\s*'[A-Za-z0-9+/_\-]{16,}'", text)
        assert not re.search(r"AccountKey=|-----BEGIN", text)
    assert "keyVaultUrl" in BICEP
    assert "ANTHROPIC_API_KEY" not in DOCKERFILE
    assert not re.search(r"(?im)^\s*(ARG|ENV)\s+\S*(KEY|SECRET|TOKEN|PASSWORD)", DOCKERFILE)


def test_dockerfile_non_root_and_no_forbidden_copy() -> None:
    users = re.findall(r"(?m)^USER\s+(\S+)", DOCKERFILE)
    assert users, "no USER"
    assert users[-1] not in {"root", "0"}
    for line in DOCKERFILE.splitlines():
        if line.strip().upper().startswith(("COPY", "ADD")):
            for banned in (".git", "runs", ".env", ".claude", "tests"):
                assert not re.search(rf"(^|\s|/){re.escape(banned)}(/|\s|$)", line.split(None, 1)[1]), line
    assert "--with-reranker" not in DOCKERFILE
    assert "--no-dev" in DOCKERFILE and "--locked" in DOCKERFILE
    assert "--no-proxy-headers" in DOCKERFILE and "--workers" in DOCKERFILE


def test_dockerignore_excludes_the_same() -> None:
    lines = {line.strip() for line in DOCKERIGNORE.splitlines()}
    for needed in (".git", "runs/", ".claude/", "models/", "index/", "tests/", "*.env", ".env*"):
        assert needed in lines, needed
    assert "!evals/calibration-offtopic.toml" in lines
```

## Fixes after lint (SR-1)

Applied to `infra/main.bicep` after the Backend Architect's checks (`11c-infra-checks.md`); not re-linted by me (no shell).

- F1 (BCP265): resource symbol `environment` renamed `managedEnv`; its reference `managedEnvironmentId: managedEnv.id` updated. The `environment().suffixes.keyvaultDns` function call is unchanged.
- F2 (BCP037): `anonymousPullEnabled` removed from the registry (anonymous pull is off by default). The note's earlier mention of it and the hand-off test's `test_bicep_registry_private` (which requires `anonymousPullEnabled: false`) are superseded; the test now rejects `anonymousPullEnabled: true` instead.
- F3 (BCP318): output is now `app.?properties.?configuration.?ingress.?fqdn ?? ''`.

## Findings for the Orchestrator

- Hand-off needed: write the three files above (write guard blocks this role), then run the seven NOT RUN commands.
- If `az bicep build` or `what-if` reports a spec or syntax error, fix it in `infra/main.bicep` (my file).
- The test regex assumes each `resource` declaration sits on one line, as written.
