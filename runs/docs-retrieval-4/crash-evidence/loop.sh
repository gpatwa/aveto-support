#!/bin/bash
# Restartable loop: loop.sh <evidence-file> <total-runs> <eval|retrieve> <rrf|rerank>
# Appends "N exitcode" per run; skips run numbers already present. Run output goes to scratch, not evidence.
# NOTE: <evidence-file> must be an ABSOLUTE path (the script cd's to the repo root).
case "$1" in /*) ;; *) echo "evidence file must be absolute" >&2; exit 2;; esac
cd /Users/gopalpatwa/opt/aveto-support || exit 2
f="$1"; total="$2"; cmd="$3"; mode="$4"
case "$mode" in rrf) r=file-rrf-v1;; rerank) r=file-rerank-v1;; esac
scratch=/private/tmp/claude-501/-Users-gopalpatwa-opt-aveto-support/9da9afe8-9603-4dea-9210-b521f2eb9884/scratchpad
touch "$f"
for i in $(seq 1 "$total"); do
  grep -q "^$i " "$f" && continue
  if [ "$cmd" = eval ]; then
    uv run python -m aveto_support eval --eval-file evals/retrieval.toml --ranking $r > "$scratch/loop.out" 2>&1
  else
    uv run python -m aveto_support retrieve --ranking $r how do I install the package > "$scratch/loop.out" 2>&1
  fi
  echo "$i $?" >> "$f"
done
