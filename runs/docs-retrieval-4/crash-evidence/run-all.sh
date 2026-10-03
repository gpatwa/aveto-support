#!/bin/bash
# Restartable: runs the four post-fix loops in order; each skips run numbers already recorded.
D=/Users/gopalpatwa/opt/aveto-support/runs/docs-retrieval-4/crash-evidence
$D/loop.sh $D/fixed-rrf-eval.txt 20 eval rrf
$D/loop.sh $D/fixed-rerank-eval.txt 20 eval rerank
$D/loop.sh $D/fixed-rrf-retrieve200.txt 200 retrieve rrf
$D/loop.sh $D/fixed-rerank-retrieve200.txt 200 retrieve rerank
