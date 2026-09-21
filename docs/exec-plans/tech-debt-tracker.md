# Tech Debt Tracker — Append-Only and Garbage-Collected

- [x] 2026-09-13: regime cost model and stress ×2/×5 (completed in
  `honest-eval-stack`)
- [x] 2026-09-13: Rust hot-loop core and conformance (5–6x in the original
  baseline; current benchmark is recorded in `rust-core.md`)
- [x] 2026-09-21: promote Rust backend into the CLI gate with a Python oracle;
  keep the Python reference for tests and fallback
- [ ] 2026-09-13: seeded stochastic slippage (owner: agent, estimate: one PR)
- [ ] 2026-09-13: production DuckDB repository instead of injected DataFrames
  (owner: agent)
- [ ] 2026-09-13: selection stability (ensemble or fewer candidates); the gate
  is seed-sensitive (5/7 PASS)
- [ ] 2026-09-13: borrow/short costs and holdout governance (hash plus ledger);
  60-day phase
- [ ] 2026-09-13: replace synthetic data with a real survivorship-clean vendor
- [x] 2026-09-13: agent-layer slice 1 (tools, schemas, ReplayLLM, pipeline, and
  gate wiring; offline)
- [ ] 2026-09-13: agent-layer slice 2 (real provider, secrets, tokens, and
  live-fire validation); requires human decisions
- [ ] 2026-09-13: split the quant harness kernel and installer from a product
  repository. Do this only when a second real repository needs it (YAGNI).
  The kernel would contain the AGENTS template, skills, decisions, scorecard,
  CI, no-lookahead and PIT contracts, determinism, cost and risk guards,
  evaluation templates, and documentation skeleton. Product-specific strategy,
  data vendor, secrets, and Rust binaries would remain outside the kernel.
- [ ] 2026-09-21: promote the Rust control plane beyond this repository only
  after a second consumer proves the adapter contract; the implementation is
  intentionally repository-local today
- [ ] 2026-09-21: publish signed/versioned release artifacts and checksum
  manifests for curl bootstrap; the current installer builds Rust source from a
  pinned raw ref
- [x] 2026-09-21: clarify installer dry-run/placeholder errors and propagate
  explicit run IDs through the Rust validation stages (decision `0006`)
- [x] 2026-09-22: add TTY-aware curl installer progress UI with plain-output
  fallback (decision `0007`)
