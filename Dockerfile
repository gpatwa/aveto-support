# public-ask-the-docs: container image (tech spec section 6). Built remotely by `az acr build`.
# Bases are pinned by the index digests that `docker buildx imagetools inspect` returned on 2026-10-21
# (read-only). uv 0.9.7 is the toolchain version (`uv --version`).

FROM ghcr.io/astral-sh/uv:0.9.7@sha256:ba4857bf2a068e9bc0e64eed8563b065908a4cd6bfb66b531a9c424c8e25e142 AS uv

FROM python:3.12-slim-bookworm@sha256:6a0e06f5ba0b373d051aabd3fffb9b873f27f9a2a3a14bcbe37dee6f0e3bbc70 AS build
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

FROM python:3.12-slim-bookworm@sha256:6a0e06f5ba0b373d051aabd3fffb9b873f27f9a2a3a14bcbe37dee6f0e3bbc70 AS runtime
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
# ingest writes index/ and models/ via mkstemp + os.replace, so the files are mode 0600 and root-owned:
# unreadable by uid 10001 (live finding F-LIVE-1). Group 10001 gets read-only, others nothing, nobody but root writes.
COPY --from=build --chown=root:10001 /app/index /app/index
COPY --from=build --chown=root:10001 /app/models /app/models
RUN chmod -R u=rwX,g=rX,o= /app/index /app/models
USER 10001
EXPOSE 8000
CMD ["/app/.venv/bin/uvicorn", "aveto_service.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-access-log", "--log-level", "critical", "--no-proxy-headers", "--no-server-header", "--no-date-header"]
