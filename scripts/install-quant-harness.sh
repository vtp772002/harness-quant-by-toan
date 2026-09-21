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
UI_MODE="${HARNESS_INSTALLER_UI:-auto}"
UI=0
GREEN=""
CYAN=""
DIM=""
RESET=""

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
  if [[ "$UI" -eq 1 ]]; then
    printf '%s✗%s install-quant-harness: %s\n' "$GREEN" "$RESET" "$*" >&2
  else
    echo "install-quant-harness: $*" >&2
  fi
  exit 2
}

setup_ui() {
  case "$UI_MODE" in
    always) UI=1 ;;
    never) UI=0 ;;
    auto)
      if [[ -t 1 && -t 2 && "${TERM:-dumb}" != "dumb" && -z "${NO_COLOR:-}" ]]; then
        UI=1
      fi
      ;;
    *) fail "HARNESS_INSTALLER_UI must be auto, always, or never" ;;
  esac
  if [[ "$UI" -eq 1 ]]; then
    GREEN=$'\033[32m'
    CYAN=$'\033[36m'
    DIM=$'\033[2m'
    RESET=$'\033[0m'
  fi
}

ui_header() {
  [[ "$UI" -eq 1 ]] || return 0
  printf '\n%sQuant Harness Installer%s\n' "$CYAN" "$RESET" >&2
  printf '%s%s%s\n' "$DIM" "$SOURCE" "$RESET" >&2
  printf '%sTarget:%s %s\n' "$DIM" "$RESET" "$TARGET" >&2
}

ui_phase() {
  [[ "$UI" -eq 1 ]] || return 0
  printf '\n%s[%s]%s %s\n' "$CYAN" "$1" "$RESET" "$2" >&2
}

ui_result() {
  if [[ "$UI" -eq 1 ]]; then
    printf '  %s✓%s %s\n' "$GREEN" "$RESET" "$1" >&2
  else
    printf '%s\n' "$1"
  fi
}

run_step() {
  local label=$1
  shift
  if [[ "$UI" -eq 0 ]]; then
    "$@"
    return
  fi
  local log="$WORK/.installer-step.log"
  "$@" >"$log" 2>&1 &
  local pid=$!
  local frames='|/-\\'
  local index=0
  while kill -0 "$pid" 2>/dev/null; do
    printf '\r\033[2K  %s%c%s %s' "$CYAN" "${frames:index:1}" "$RESET" "$label" >&2
    index=$(( (index + 1) % 4 ))
    sleep 0.1
  done
  local status=0
  if wait "$pid"; then
    status=0
  else
    status=$?
  fi
  if [[ "$status" -eq 0 ]]; then
    printf '\r\033[2K  %s✓%s %s\n' "$GREEN" "$RESET" "$label" >&2
  else
    printf '\r\033[2K  %s✗%s %s\n' "$GREEN" "$RESET" "$label" >&2
    [[ -s "$log" ]] && sed 's/^/    /' "$log" >&2
  fi
  return "$status"
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

setup_ui
command -v curl >/dev/null 2>&1 || fail "curl is required"
case "$REF" in
  *COMMIT_SHA*|*YOUR_*|\<*\>)
    fail "--ref must be a real branch, tag, or commit; replace the placeholder"
    ;;
esac
TARGET=$(cd "$TARGET" 2>/dev/null && pwd) || fail "target is not a directory: $TARGET"
SOURCE_BASE=${SOURCE_BASE%/}
SOURCE="$SOURCE_BASE"
[[ -z "$REF" ]] || SOURCE="$SOURCE/$REF"
ui_header

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
ui_phase "1/4" "Fetching the managed-file manifest"
run_step "Downloading manifest" curl --fail --silent --show-error --location --retry 3 "$SOURCE/scripts/quant-harness-files.txt" -o "$MANIFEST" || fail "could not download the managed-file manifest"

valid_path() {
  local path=$1
  [[ "$path" != /* && "$path" != *".."* && "$path" != *$'\n'* ]]
}

download_payload() {
  local path=$1
  valid_path "$path" || fail "unsafe payload path: $path"
  local out="$WORK/$path"
  mkdir -p "$(dirname "$out")"
  run_step "Downloading $path" curl --fail --silent --show-error --location --retry 3 "$SOURCE/$path" -o "$out" || fail "could not download $path"
}

ui_phase "2/4" "Applying managed files"
while IFS= read -r path || [[ -n "$path" ]]; do
  [[ -z "$path" || "$path" == \#* ]] && continue
  download_payload "$path"
  dest="$TARGET/$path"
  if [[ -e "$dest" && "$MODE" == "merge" ]]; then
    ui_result "preserve $path"
  elif [[ "$DRY_RUN" -eq 1 ]]; then
    ui_result "install $path"
  else
    mkdir -p "$(dirname "$dest")"
    cp "$WORK/$path" "$dest"
    [[ "$path" == *.sh ]] && chmod 0755 "$dest"
    ui_result "installed $path"
  fi
done < "$MANIFEST"

BIN="$TARGET/scripts/bin/quant-harness"
if [[ "$DRY_RUN" -eq 1 ]]; then
  ui_phase "3/4" "Planning the Rust control-plane binary"
  if [[ "$MODE" == "merge" && -x "$BIN" ]]; then
    ui_result "preserve $BIN"
  else
    ui_result "install release binary: $BIN"
  fi
  ui_phase "4/4" "Dry run complete; no files changed"
  exit 0
fi

if [[ "$MODE" == "merge" && -x "$BIN" ]]; then
  ui_phase "3/4" "Checking the Rust control-plane binary"
  ui_result "preserve scripts/bin/quant-harness"
  ui_phase "4/4" "Installation complete"
  exit 0
fi
command -v cargo >/dev/null 2>&1 || fail "cargo is required to build the Rust control-plane"
ui_phase "3/4" "Building the Rust control-plane binary"
run_step "Compiling quant-harness" cargo build --release --manifest-path "$WORK/crates/harness-cli/Cargo.toml" || fail "Cargo could not build the Rust control-plane"
mkdir -p "$(dirname "$BIN")"
install -m 0755 "$WORK/crates/harness-cli/target/release/quant-harness" "$BIN"
ui_result "installed scripts/bin/quant-harness"
ui_phase "4/4" "Installation complete"
