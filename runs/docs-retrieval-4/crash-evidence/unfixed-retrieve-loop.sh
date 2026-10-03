#!/bin/bash
# Restartable: unfixed-retrieve-loop.sh <abs evidence file>; runs 200 retrieves on the pre-fix tree (git worktree of 6591bf3 at /private/tmp/claude-501/-Users-gopalpatwa-opt-aveto-support/9da9afe8-9603-4dea-9210-b521f2eb9884/scratchpad/prefix-wt).
f="$1"; touch "$f"; cd /private/tmp/claude-501/-Users-gopalpatwa-opt-aveto-support/9da9afe8-9603-4dea-9210-b521f2eb9884/scratchpad/prefix-wt || exit 2
for i in $(seq 1 200); do
  grep -q "^$i " "$f" && continue
  uv run python -m aveto_support retrieve --ranking file-rerank-v1 how do I install the package > /private/tmp/claude-501/-Users-gopalpatwa-opt-aveto-support/9da9afe8-9603-4dea-9210-b521f2eb9884/scratchpad/unfixed.out 2>&1
  echo "$i $?" >> "$f"
done
