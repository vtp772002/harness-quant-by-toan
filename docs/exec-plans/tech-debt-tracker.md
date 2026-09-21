# Tech Debt Tracker — append-only, garbage-collected
- [x] 2026-09-13: regime cost model + stress x2/x5 (xong trong honest-eval-stack)
- [x] 2026-09-13: rust hot-loop core + conformance (5-6x, maxdiff 2.3e-10)
- [x] 2026-09-21: promote rust backend vao CLI gate with Python oracle; keep
  Python reference for tests and fallback.
- [ ] 2026-09-13: slippage stochastic seeded (owner: agent, est: 1 PR)
- [ ] 2026-09-13: duckdb prod repo thay inject-df (owner: agent)
- [ ] 2026-09-13: selection stability (ensemble/thu hep candidates) — gate hien nhay voi seed (5/7 PASS)
- [ ] 2026-09-13: borrow/short costs + holdout governance (hash + ledger) — phase 60 ngay
- [ ] 2026-09-13: data vendor that thay synthetic (survivorship-clean universe that)
- [x] 2026-09-13: agent-layer slice 1 (tools/schemas/ReplayLLM/pipeline/gate wiring, offline)
- [ ] 2026-09-13: agent-layer slice 2 (provider that, secrets, tokens, live-fire) — can human quyet dinh
- [ ] 2026-09-13: tach QUANT harness kernel + installer (chuyen biet quantitative research, khong generic) — kernel gom: repo protocol (AGENTS template/skills/decisions/scorecard/CI) + quant contracts (no-lookahead linter + PIT repo/Universe pattern, determinism linter + seeded RNG, costs floor + RegimeCostModel, risk-in-code/RiskBreach, evals template: purged-embargo CV + DSR + stress gate, quant docs skeleton, proposal schemas + gate wiring). Product o lai: strategy code, data vendor, secrets, rust binary. Kem manifest + update path. Chi lam khi co repo thu hai that su can (YAGNI)
- [ ] 2026-09-21: promote Rust control plane beyond this repository only after a second
  consumer repo proves the adapter contract; current implementation is repository-local
  and intentionally avoids a generic installer.
- [ ] 2026-09-21: publish signed/versioned release artifacts and checksum manifest for
  curl bootstrap; current installer builds Rust source fetched from a pinned raw ref.
