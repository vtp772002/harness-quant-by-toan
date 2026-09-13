#!/usr/bin/env bash
# Boot môi trường isolated per-worktree (tương đương "app bootable per git worktree" của OpenAI).
# Mỗi worktree/agent có QUANT_RUN_ID riêng + stack logs/metrics/traces riêng, teardown sau task.
set -e
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo local)
WT=$(echo "$BRANCH" | tr '/ ' '--')
export QUANT_RUN_ID="${QUANT_RUN_ID:-$WT-$$}"
mkdir -p "runs/$QUANT_RUN_ID"
echo "{\"run_id\":\"$QUANT_RUN_ID\",\"seed\":42}" > "runs/$QUANT_RUN_ID/manifest.json"
echo "$QUANT_RUN_ID" > .worktree-id
echo "Booted run: $QUANT_RUN_ID (stack: runs/$QUANT_RUN_ID/{logs,metrics,traces}.jsonl)"
python3 -c "import pydantic,pandas,numpy,duckdb; print('deps ok')"
