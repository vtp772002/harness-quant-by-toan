# 0004 — Curl Bootstrap for the Quant Control Plane

- Date: 2026-09-21. Status: accepted.
- Context: the control plane could be installed locally with Cargo but lacked a
  familiar harness-repository install flow. An agent or user may need to
  bootstrap from a target repository without cloning the full source tree.

## Decision

1. Publish `scripts/install-quant-harness.sh` through a GitHub raw URL.
2. The installer downloads a fixed payload list, merges by default, requires
   intentional `--override` for replacement, and supports `--dry-run`.
3. The installer builds the Rust control plane on the target machine and puts
   the platform-specific binary in `scripts/bin/`; binaries are not committed.
4. Non-interactive `curl | bash` requires `--yes`. The source ref and raw base
   URL can be overridden for tests or an air-gapped mirror.

## Consequences

- One-command bootstrap remains fast while the source and control plane stay
  inspectable in the target repository.
- HTTPS and `--ref` pin the source boundary. Signed release binaries and
  checksums are a follow-up workstream.
- The installer does not automatically overwrite `AGENTS.md`, docs, or product
  policy.
