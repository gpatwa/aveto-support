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
EXISTING_ONLY = {
    "Microsoft.KeyVault/vaults"
}  # the owner's vault, referenced with `existing`

RESOURCE = re.compile(
    r"^resource\s+\w+\s+'([^'@]+)@[^']+'\s*(existing\s*)?=", re.MULTILINE
)


def _code_lines(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("//")
    )


def test_bicep_resources_are_c83() -> None:
    found = RESOURCE.findall(_code_lines(BICEP))
    assert found, "no resources parsed"
    assert len(found) == len(
        re.findall(r"^resource\s", _code_lines(BICEP), re.MULTILINE)
    )
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
    # anonymous pull is off by default and the property is not valid on Basic (BCP037)
    assert not re.search(r"anonymousPullEnabled:\s*true", BICEP)


def test_bicep_no_secret_literals() -> None:
    for text in (BICEP, PARAMS, DOCKERFILE):
        assert not re.search(r"sk-ant-", text)
        assert not re.search(
            r"(?i)(password|secret|api[_-]?key|token)\s*[:=]\s*'[A-Za-z0-9+/_\-]{16,}'",
            text,
        )
        assert not re.search(r"AccountKey=|-----BEGIN", text)
    assert "keyVaultUrl" in BICEP
    assert "ANTHROPIC_API_KEY" not in DOCKERFILE
    assert not re.search(
        r"(?im)^\s*(ARG|ENV)\s+\S*(KEY|SECRET|TOKEN|PASSWORD)", DOCKERFILE
    )


def test_dockerfile_static() -> None:
    users = re.findall(r"(?m)^USER\s+(\S+)", DOCKERFILE)
    assert users, "no USER"
    assert users[-1] not in {"root", "0"}
    for line in DOCKERFILE.splitlines():
        if line.strip().upper().startswith(("COPY", "ADD")):
            for banned in (".git", "runs", ".env", ".claude", "tests"):
                assert not re.search(
                    rf"(^|\s|/){re.escape(banned)}(/|\s|$)", line.split(None, 1)[1]
                ), line
    assert "--with-reranker" not in DOCKERFILE
    assert "--no-dev" in DOCKERFILE and "--locked" in DOCKERFILE
    assert "--no-proxy-headers" in DOCKERFILE and "--workers" in DOCKERFILE
    assert "--no-access-log" in DOCKERFILE
    assert "aveto_service.main:app" in DOCKERFILE
    assert "aveto_support ingest" in DOCKERFILE
    for image in re.findall(r"(?m)^FROM\s+(\S+)", DOCKERFILE):
        assert re.search(r"@sha256:[0-9a-f]{64}$", image), (
            f"base not pinned by digest: {image}"
        )


def test_dockerignore_excludes_models_index() -> None:
    lines = {line.strip() for line in DOCKERIGNORE.splitlines()}
    for needed in (
        ".git",
        "runs/",
        ".claude/",
        "models/",
        "index/",
        "tests/",
        "*.env",
        ".env*",
    ):
        assert needed in lines, needed
    assert "!evals/calibration-offtopic.toml" in lines
