#!/usr/bin/env bash
# Cross-platform adapter: policy lives in the Rust control plane.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
INSTALLED="$ROOT/scripts/bin/quant-harness"
if [[ -x "$INSTALLED" ]]; then
  exec "$INSTALLED" "$@" --root "$ROOT"
fi
exec cargo run --quiet --manifest-path "$ROOT/crates/harness-cli/Cargo.toml" -- "$@" --root "$ROOT"
