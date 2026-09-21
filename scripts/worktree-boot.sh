#!/usr/bin/env bash
# Boot an isolated environment per worktree, similar to an app bootable per Git worktree.
# Each worktree/agent gets its own QUANT_RUN_ID and logs/metrics/traces stack.
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BRANCH=$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || true)
BRANCH=${BRANCH:-local}
WT=$(printf '%s' "$BRANCH" | tr '/ ' '--')
export QUANT_RUN_ID="${QUANT_RUN_ID:-$WT-$$}"
bash "$ROOT/scripts/quant-harness.sh" boot --seed "${QUANT_SEED:-42}" --run-id "$QUANT_RUN_ID"
printf '%s\n' "$QUANT_RUN_ID" > "$ROOT/.worktree-id"
echo "Booted run: $QUANT_RUN_ID (stack: runs/$QUANT_RUN_ID/{logs,metrics,traces}.jsonl)"
