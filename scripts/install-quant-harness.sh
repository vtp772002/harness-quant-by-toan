#!/usr/bin/env bash
# Bootstrap the quant harness into a target repository.
# Typical use:
# curl -fsSL https://raw.githubusercontent.com/vtp772002/harness-quant-by-toan/main/scripts/install-quant-harness.sh | bash -s -- --yes
set -euo pipefail

SOURCE_BASE="${HARNESS_SOURCE_BASE_URL:-https://raw.githubusercontent.com/vtp772002/harness-quant-by-toan}"
REF="main"
TARGET=$(pwd)
MODE="merge"
YES=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Install the quant harness control-plane into a repository.

Options:
  --target PATH             destination repository (default: current directory)
  --merge                   preserve existing files (default)
  --override                replace managed files intentionally
  --dry-run                 show the planned mutation without writing
  --yes                     skip the non-interactive confirmation
  --source-base-url URL     raw source root without the ref segment
  --ref REF                 source ref (default: main)
EOF
}

fail() {
  echo "install-quant-harness: $*" >&2
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) [[ $# -ge 2 ]] || fail "--target needs a path"; TARGET=$2; shift 2 ;;
    --merge) MODE="merge"; shift ;;
    --override) MODE="override"; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --yes) YES=1; shift ;;
    --source-base-url) [[ $# -ge 2 ]] || fail "--source-base-url needs a URL"; SOURCE_BASE=$2; shift 2 ;;
    --ref) [[ $# -ge 2 ]] || fail "--ref needs a value"; REF=$2; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) fail "unknown option: $1" ;;
  esac
done

command -v curl >/dev/null 2>&1 || fail "curl is required"
TARGET=$(cd "$TARGET" 2>/dev/null && pwd) || fail "target is not a directory: $TARGET"
SOURCE_BASE=${SOURCE_BASE%/}
SOURCE="$SOURCE_BASE"
[[ -z "$REF" ]] || SOURCE="$SOURCE/$REF"

if [[ "$DRY_RUN" -eq 0 && "$YES" -eq 0 ]]; then
  if [[ ! -t 0 ]]; then
    fail "non-interactive install requires --yes (or use --dry-run)"
  fi
  printf 'Install quant harness into %s? [y/N] ' "$TARGET"
  read -r answer
  [[ "$answer" == "y" || "$answer" == "Y" ]] || { echo "cancelled"; exit 0; }
fi

WORK=$(mktemp -d "${TMPDIR:-/tmp}/quant-harness-install.XXXXXX")
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

MANIFEST="$WORK/quant-harness-files.txt"
curl --fail --silent --show-error --location --retry 3 "$SOURCE/scripts/quant-harness-files.txt" -o "$MANIFEST"

valid_path() {
  local path=$1
  [[ "$path" != /* && "$path" != *".."* && "$path" != *$'\n'* ]]
}

download_payload() {
  local path=$1
  valid_path "$path" || fail "unsafe payload path: $path"
  local out="$WORK/$path"
  mkdir -p "$(dirname "$out")"
  curl --fail --silent --show-error --location --retry 3 "$SOURCE/$path" -o "$out"
}

while IFS= read -r path || [[ -n "$path" ]]; do
  [[ -z "$path" || "$path" == \#* ]] && continue
  download_payload "$path"
  dest="$TARGET/$path"
  if [[ -e "$dest" && "$MODE" == "merge" ]]; then
    echo "preserve $path"
  elif [[ "$DRY_RUN" -eq 1 ]]; then
    echo "install $path"
  else
    mkdir -p "$(dirname "$dest")"
    cp "$WORK/$path" "$dest"
    [[ "$path" == *.sh ]] && chmod 0755 "$dest"
    echo "installed $path"
  fi
done < "$MANIFEST"

BIN="$TARGET/scripts/bin/quant-harness"
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "install release binary: $BIN"
  exit 0
fi

if [[ "$MODE" == "merge" && -x "$BIN" ]]; then
  echo "preserve scripts/bin/quant-harness"
  exit 0
fi
command -v cargo >/dev/null 2>&1 || fail "cargo is required to build the Rust control-plane"
cargo build --release --manifest-path "$WORK/crates/harness-cli/Cargo.toml"
mkdir -p "$(dirname "$BIN")"
install -m 0755 "$WORK/crates/harness-cli/target/release/quant-harness" "$BIN"
echo "installed scripts/bin/quant-harness"
