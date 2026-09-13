# harness-quant-by-toan — Agent-first harness for AI quant research

> Humans steer, agents execute. This harness doesn't write strategies for you —
> it forces every strategy (human- or agent-proposed) to **stay honest**:
> point-in-time, net of costs, statistically guarded against overfitting,
> byte-identical reproducible.

Every line of code, test, doc, and eval in this repo is agent-written via
prompts → short PRs → self-review (Ralph Wiggum Loop) → merge.
Humans only do three things: design environments, state intent, build feedback loops.
Root philosophy: [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/) (02/2026).

---

## Contents

1. [Quickstart](#1-quickstart)
2. [Standard research loop](#2-standard-research-loop)
3. [Reading the gate verdict](#3-reading-the-gate-verdict)
4. [Architecture](#4-architecture)
5. [Repo tour](#5-repo-tour)
6. [Command cheatsheet](#6-command-cheatsheet)
7. [Invariants (CI blocks on violation)](#7-invariants-ci-blocks-on-violation)
8. [Agent layer: agents propose, gate disposes](#8-agent-layer-agents-propose-gate-disposes)
9. [Rust core (optional speedup)](#9-rust-core-optional-speedup)
10. [Harness health scorecard](#10-harness-health-scorecard)
11. [Calibration numbers](#11-calibration-numbers)
12. [Extending](#12-extending)
13. [Attribution](#13-attribution)

---

## 1. Quickstart

Requirements: Python ≥ 3.11, Rust toolchain (only for `crates/quant-core`).

```bash
bash scripts/worktree-boot.sh                      # boot isolated per-worktree env
PYTHONPATH=. python scripts/run-backtest.py --seed 42   # smoke test (~1s)
PYTHONPATH=. python scripts/run-eval.py --seed 42       # honest-eval gate → PASS/FAIL
python linters/run_all.py                          # 4 linters (blocking)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. pytest tests/ evals/ -q -p no:cacheprovider
PYTHONPATH=. python scripts/evaluate-quant-harness.py   # behavior scorecard
```

> Environment notes: every Python command needs `PYTHONPATH=.`.
> `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` works around an old `httpx` plugin broken on
> Python 3.13 (local machine issue, not the harness).

Done right, you get: gate `PASS`, 4/4 linters green, 25 pytest passed, 8/8 scorecard.

---

## 2. Standard research loop

1. **Write a 1-page spec** per `docs/product-specs/quant-research-loop.md`:
   falsifiable hypothesis, universe, horizon, costs, risk, numeric kill-criteria.
   Task > 30 min → create an exec-plan at `docs/exec-plans/active/<name>.md`.
2. **Code by layer** (`ARCHITECTURE.md`): new signals go as pure logic in
   `src/domains/alpha/` (take only `bars_asof`, never the full dataframe).
3. **Smoke**: `run-backtest.py --seed 42`.
4. **Gate** (`run-eval.py --seed 42`) — this verdict is the only one that counts.
5. **Self-review**: linters + pytest until green → PR < 400 lines → fast merge.
   Flake → follow-up rerun, never blocks.

Every off-code decision (chat, Slack) must be encoded as a file under `docs/` —
otherwise, as far as the agent is concerned, it doesn't exist.

---

## 3. Reading the gate verdict

`scripts/run-eval.py` returns JSON: `verdict`, `sharpe_oos`, `dsr`, `stress_x2/x5`,
`max_dd`, `picks` (lookback selected per fold), `candidates`.

| PASS thresholds (net of costs, OOS) | Value |
|---|---|
| OOS Sharpe (annualized) | > 0.5 |
| Deflated Sharpe (K = configs/proposals tried) | > 0.95 |
| Slippage stress x2 | Sharpe > 0 (blocking) |
| Slippage stress x5 | > −1.0 (informational, blocks only if deeply negative) |
| OOS max drawdown | > −15% |

| On FAIL | Action |
|---|---|
| Low `sharpe`/`dsr` | Weak edge or overfit — kill the strategy or fix the hypothesis, log tech-debt |
| `stress_x2 < 0` | Survives only on cheap costs, high turnover — add deadband, cut turnover |
| `x5` negative but > −1.0 | Warning, non-blocking — note it in the PR for reviewers |
| `picks` flip every fold | Unstable selection — be suspicious, needs more data |

Gate pipeline: 756-day × 4-symbol synthetic market → split-adjust → PIT universe →
panel momentum + regime costs → purged-embargo 3 folds (purge = max lookback + 1) →
per-fold train lookback selection → OOS + DSR + stress. Deterministic per seed.

---

## 4. Architecture

Each domain (`data`, `alpha`, `backtest`, `risk`, `portfolio`) may only depend **forward**:

```
Types → Config → Repo → Service → Runtime → Reports
```

Cross-cutting concerns (`telemetry`, `data_vendor`, `exchange_sim`, `clock`, `llm`) go
exclusively through **Providers** — the single explicit interface. Violations fail CI
with remediation instructions in the error message.
Single composition root: `src/wiring.py`. Details: `ARCHITECTURE.md`.

Six golden principles (mechanically enforced, garbage-collected daily):
shared utils · parse-at-boundary (Pydantic, no YOLO probing) · no lookahead (`asof ≤ t`) ·
determinism (seeded RNG, same seed → byte-identical) · costs always modeled ·
risk in code (breaches `raise`, never warn).

---

## 5. Repo tour

```
AGENTS.md                  Agent entrypoint (~80 lines, a table of contents, not an encyclopedia)
ARCHITECTURE.md            Layer + provider contracts
src/domains/data/          Bars, PIT repo, UniverseRepo (list/delist), split-adjust, synthetic market
src/domains/alpha/         Momentum + indicator tools + reports + agent pipeline + schemas
src/domains/backtest/      Deterministic event-loop backtest + reports (Sharpe/maxDD/turnover)
src/domains/risk/          check_limits → raises RiskBreach
src/domains/portfolio/     Position sizing
src/providers/             clock (sole wall-clock owner) · telemetry (per-worktree JSONL)
                           market (Simple + RegimeCostModel) · llm (protocol + Replay/Live)
src/utils/                 seeded RNG, structured logging, map-with-concurrency
src/wiring.py              Composition root (seeded demo run)
evals/                     purged_cv · deflated_sharpe (hand-rolled, no scipy)
                           gate (promotion authority) · rust_core (bridge)
crates/quant-core/         Rust hot loop (std-only, CSV boundary), see section 9
linters/                   layering · no_lookahead · determinism · taste (blocking)
tests/                     structure · honest_eval · agent_layer · rust_core (conformance)
scripts/                   worktree-boot · run-backtest · run-eval · query-logs/metrics
                           bench-eval · bench-rust · doc-garden · gc-scan · evaluate-quant-harness
docs/                      system of record: design-docs · product-specs · exec-plans
                           decisions (ADR) · EVALUATION · QUALITY_SCORE · RISK_LIMITS · ...
.agents/skills/ · skills/  encode-invariant · improve-harness · reproduce-backtest
                           validate-no-lookahead · self-review-loop
.github/workflows/         gates.yml (minimal blocking + non-blocking full-eval)
```

---

## 6. Command cheatsheet

```bash
PYTHONPATH=. python scripts/query-metrics.py --metric sharpe      # Sharpe across runs
PYTHONPATH=. python scripts/query-metrics.py --metric gate.dsr    # DSR
PYTHONPATH=. python scripts/query-logs.py --filter level=ERROR    # filter errors
python scripts/doc-garden.py --scan    # scan for rotten docs (TODO/TBD, stale markers)
python scripts/gc-scan.py              # scan for copy-pasted helpers / YOLO probing
PYTHONPATH=. python scripts/bench-eval.py    # baseline benchmark, find the hot loop
PYTHONPATH=. python scripts/bench-rust.py    # Python vs Rust core comparison
```

Each worktree gets its own observability stack: `runs/<id>/logs.jsonl`, `metrics.jsonl`,
`traces.jsonl` (+ `manifest.json` recording seed + config). Torn down after the task.

---

## 7. Invariants (CI blocks on violation)

- **No lookahead**: features may only use `ts ≤ t`. Banned: `.shift(-`, `future`, `lead(`, non-asof joins.
- **Determinism**: all randomness via `seeded_rng(seed)`; banned `random.*`, `time.time()`,
  `datetime.now()` outside `providers/clock.py`.
- **Costs + risk**: a backtest without fee/slippage is invalid; breaching `RISK_LIMITS.md` must raise.
- **Taste**: files ≤ 500 lines, functions ≤ 50 lines, structured logging, no hardcoded secrets.
- **Judgment boundaries** (decision 0001): stop before mutating while a material choice is open —
  present choice + consequence, wait for the human. Never invent product policy.
- **New rule = guard + proof** (decision 0002): ship positive/negative proof, not prose.

---

## 8. Agent layer: agents propose, gate disposes

Four-step pipeline in `src/domains/alpha/agents.py`: Indicator → Pattern → Trend → Decision.
Sequential, deterministic, 100% offline.

- **Tools** (`alpha/tools.py`): RSI/MACD/Stoch/ROC/WillR/ATR + breakout/engulfing/
  range-position/trend-slope — pandas-only (no TA-Lib), pure, PIT-safe.
- **Schemas** (`alpha/schemas.py`): every agent output validated with Pydantic before moving on.
- **LLM** (`providers/llm.py`): behind the `LLMProvider` protocol. `ReplayLLM` for tests/CI
  (picks responses by context hash — stateless, deterministic). `LiveLLM`
  (OpenAI-compatible, stdlib HTTPS, key via env) — raises without a key, never runs in CI.
  LLMs only add narrative/confidence; **numbers never change**.
- **Gate wiring**: `run_gate(..., candidate_lookbacks=proposal.candidate_lookbacks)` —
  the more you propose, the harder DSR penalizes. The proposal→gate loop is test-locked.

Not done (needs human decisions first — decision 0001):
real provider, secrets policy, token budget, LangGraph, live-fire validation.

---

## 9. Rust core (optional speedup)

`crates/quant-core`: ports exactly the `panel_backtest` hot loop, std-only with zero
dependencies, CSV boundary (`panel.csv` + `members.csv` → `equity.csv`).
Python keeps orchestration (gate, selection, DSR) — Rust **never replaces the reference**.

| lookback | Python | Rust | speedup | equity diff |
|---|---|---|---|---|
| 5 | 165ms | 33ms | 5.1x | 2.3e-10 |
| 10 | 154ms | 28ms | 5.4x | 2.3e-10 |
| 20 | 151ms | 26ms | 5.9x | 2.3e-10 |

Promotion rule: conformance green + Python panel loop > 30s (currently ~0.5s).
Without the binary, conformance tests self-skip and the Python gate runs normally.

```bash
cargo build --release -p quant-core
PYTHONPATH=. python scripts/bench-rust.py
```

---

## 10. Harness health scorecard

```bash
PYTHONPATH=. python scripts/evaluate-quant-harness.py --seed 42
```

Versioned JSON output (`quant-scorecard-v1`), 8 cases:
authority-entry · docs-map · linters · tests · gate · rust-conformance ·
evidence (manifest) · docs-fresh. Any blocking fail = no merge.

---

## 11. Calibration numbers

The synthetic market (AR(1) φ=0.3 + drift, 4 symbols with list/delist, one 2:1 split) —
a PASS here proves **the plumbing is correct, not that the alpha is real**.
Real verdicts need real data.

Gate seed 42 (CI lock, wide margin): Sharpe **2.25**, DSR **1.0**, x2 **2.09**,
x5 **1.62** → PASS. Multi-seed over 7 seeds: 5 PASS; the 2 FAILs are genuinely marginal
(Sharpe ~1.0, DSR < 0.9) — the gate correctly rejects them. Full table:
`docs/design-docs/honest-eval.md`.

Three design bugs surfaced by actually running (in the decision log):
annualized/daily unit mix-up in DSR · 300 days too few so selection was coin-flip ·
blocking x5 stress killed even a 2.08-Sharpe strategy (downgraded to informational).

---

## 12. Extending

Prioritized tech-debt (`docs/exec-plans/tech-debt-tracker.md`):
real (survivorship-clean) data vendor · seeded stochastic slippage · duckdb prod repo ·
selection stability · borrow/short costs + holdout governance · agent-layer slice 2.
Harness improvement process: `improve-harness` skill (baseline-to-rerun evidence + decision record).

---

## 13. Attribution

- OpenAI Harness Engineering (02/2026) — agent-first philosophy, legibility, garbage collection.
- [QuantHarness](https://github.com/Y-Research-SBU/QuantHarness) (MIT) — 4-agent architecture
  (idea adopted, fully rewritten, no code copied).
- [harness-by-victoria](https://github.com/vtp772002/harness-by-victoria) (MIT) —
  decisions/skills/scorecard protocol (idea adopted, text rewritten).

> **Disclaimer**: research harness, not financial advice.
> A synthetic PASS guarantees nothing about real-world profit.

> **License**: no LICENSE file yet (all rights reserved by default) — MIT intended.
