#!/usr/bin/env bash
# Boot môi trường isolated per-worktree (tương đương "app bootable per git worktree" của OpenAI).
# Mỗi worktree/agent có QUANT_RUN_ID riêng + stack logs/metrics/traces riêng, teardown sau task.
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BRANCH=$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || true)
BRANCH=${BRANCH:-local}
WT=$(printf '%s' "$BRANCH" | tr '/ ' '--')
export QUANT_RUN_ID="${QUANT_RUN_ID:-$WT-$$}"
bash "$ROOT/scripts/quant-harness.sh" boot --seed "${QUANT_SEED:-42}" --run-id "$QUANT_RUN_ID"
printf '%s\n' "$QUANT_RUN_ID" > "$ROOT/.worktree-id"
echo "Booted run: $QUANT_RUN_ID (stack: runs/$QUANT_RUN_ID/{logs,metrics,traces}.jsonl)"
