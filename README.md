# Quant Research Harness

Agent-first infrastructure for quantitative research. The harness turns a
research hypothesis into a reproducible, reviewable experiment and blocks
common sources of false confidence:

- point-in-time data and no lookahead;
- explicit fees, slippage, and risk limits;
- deterministic seeds and inspectable run evidence;
- purged walk-forward evaluation and out-of-sample promotion gates;
- a Rust control plane and hot loop with a Python reference oracle.

This is a research control system, not a live-trading system. A PASS on the
included synthetic market proves that the plumbing is working; it does not
prove that an alpha is real or profitable.

**Version:** `0.2.0` · **License:** [MIT](LICENSE) · **Design reference:**
[OpenAI — Harness engineering](https://openai.com/index/harness-engineering/)

## Contents

| If you want to... | Read |
|---|---|
| Run the repository | [Quickstart](#quickstart) |
| Install into another repository | [Curl installer](#curl-installer) |
| Run a strategy experiment | [Research workflow](#research-workflow) |
| Understand the gate result | [Evaluation gate](#evaluation-gate) |
| Understand Python/Rust responsibilities | [Runtime boundary](#runtime-boundary) |
| Contribute safely | [Development and validation](#development-and-validation) |
| Find the detailed policy | [Documentation map](#documentation-map) |

## What this repository provides

The harness provides five things:

1. **A repository contract.** `AGENTS.md`, `ARCHITECTURE.md`, and the `docs/`
   tree tell agents where decisions, assumptions, and constraints live.
2. **A deterministic research loop.** Seeded synthetic data, backtests, logs,
   metrics, and manifests make a run inspectable and repeatable.
3. **A skeptical evaluation gate.** Purged folds, embargoing, cost stress,
   selection-aware Deflated Sharpe, and drawdown limits make promotion harder.
4. **Mechanical feedback.** Linters, tests, Rust/Python conformance, and a
   versioned scorecard fail early when the contract is violated.
5. **A portable entrypoint.** Bash and PowerShell are thin adapters around the
   Rust control plane, so the same `doctor`, `boot`, and `check` contract works
   across supported environments.

It intentionally does not provide a broker, credentials, live order execution,
real market data, or a claim of investment performance.

## Quickstart

### Requirements

- Python `>= 3.11`;
- Rust toolchain with `cargo`;
- Bash on Unix-like systems;
- PowerShell on Windows.

Clone the repository and run commands from its root. Python commands in this
repository use `PYTHONPATH=.` so local packages resolve consistently.

### 1. Check the environment

```bash
scripts/quant-harness.sh doctor
```

This checks that the repository root and required contract files are present.

### 2. Create a reproducible run

```bash
scripts/quant-harness.sh boot --seed 42 --run-id smoke-42
```

This creates a run manifest containing the run ID, seed, Git SHA, harness
version, and configuration. The run-local files live under `runs/<run-id>/`.
Use the same run ID for the commands that follow.

### 3. Run the complete contract

```bash
scripts/quant-harness.sh check --seed 42 --run-id smoke-42
```

This is the canonical health command. It builds the Rust numerical core, tests
the Rust control plane, runs blocking linters and Python tests, runs the honest
evaluation gate, checks Rust/Python conformance, and executes the behavior
scorecard. A failing blocking stage stops the command.

### 4. Run only the research path

```bash
QUANT_RUN_ID=smoke-42 PYTHONPATH=. python scripts/run-backtest.py --seed 42
QUANT_RUN_ID=smoke-42 PYTHONPATH=. python scripts/run-eval.py --seed 42 --backend auto
```

The first command is a small deterministic smoke backtest. The second command
is the promotion gate on a separate 756-day synthetic panel. Their Sharpe
values are not expected to match: they answer different questions.

Query only this run instead of the historical `runs/local` directory:

```bash
PYTHONPATH=. python scripts/query-metrics.py --run smoke-42 --metric sharpe
PYTHONPATH=. python scripts/query-logs.py --run smoke-42 --filter level=ERROR
```

On Windows, use the control-plane adapter:

```powershell
.\scripts\quant-harness.ps1 doctor
.\scripts\quant-harness.ps1 boot --seed 42 --run-id smoke-42
.\scripts\quant-harness.ps1 check --seed 42 --run-id smoke-42
```

For Python commands in PowerShell:

```powershell
$env:PYTHONPATH = "."
$env:QUANT_RUN_ID = "smoke-42"
python scripts/run-backtest.py --seed 42
python scripts/run-eval.py --seed 42 --backend auto
```

## Curl installer

Install the control plane and managed harness files into an existing quant
repository without cloning this repository:

```bash
curl -fsSL https://raw.githubusercontent.com/vtp772002/harness-quant-by-toan/main/scripts/install-quant-harness.sh \
  | bash -s -- --yes --target "$PWD"
```

The installer:

1. downloads the fixed payload manifest from the selected source ref;
2. downloads only the managed files listed in that manifest;
3. preserves existing files by default;
4. builds the Rust control plane locally with Cargo; and
5. installs `scripts/bin/quant-harness` in the target repository.

It does not install credentials, broker integrations, live trading, or product
policy. Cargo is required on the target machine because the installer builds a
platform-specific binary locally.

Choose exactly one of the following commands. Do not paste the whole block as
one shell script:

```bash
# Preview without writing files
( set -o pipefail; curl -fsSL https://raw.githubusercontent.com/vtp772002/harness-quant-by-toan/main/scripts/install-quant-harness.sh \
  | bash -s -- --dry-run --target "$PWD" )

# Normal merge install; existing managed files are preserved
( set -o pipefail; curl -fsSL https://raw.githubusercontent.com/vtp772002/harness-quant-by-toan/main/scripts/install-quant-harness.sh \
  | bash -s -- --yes --target "$PWD" )

# Replace managed files intentionally
( set -o pipefail; curl -fsSL https://raw.githubusercontent.com/vtp772002/harness-quant-by-toan/main/scripts/install-quant-harness.sh \
  | bash -s -- --yes --override --target "$PWD" )
```

For non-interactive use, `--yes` is required. To pin the source, pass
`--ref <real-commit-or-tag>`; do not run a placeholder literally. The
repository currently has no published release tag, so use a real commit SHA or
`main`. Release checksums are a follow-up workstream; the current installer
builds source locally rather than fetching a prebuilt binary.

The installer installs only the control-plane payload listed in
`scripts/quant-harness-files.txt`: shell/PowerShell adapters, Rust CLI source,
and the installer itself. It does not install Python dependencies, research
code, docs, credentials, or market data. The target repository still needs the
contract files required by `doctor`.

In merge mode, `preserve <path>` means that the target already has that managed
file; it is a successful no-op. In dry-run mode, `preserve` means the same thing
but no files are written.

When stdout and stderr are terminals, the installer shows a colored four-stage
progress UI with a spinner while downloading files and compiling Rust. It
automatically falls back to plain, log-friendly output in CI or redirected
shells. Set `NO_COLOR=1` or `HARNESS_INSTALLER_UI=never` to disable the UI; set
`HARNESS_INSTALLER_UI=always` only when the output is a terminal emulator that
supports ANSI control sequences.

## Research workflow

Use this loop for every hypothesis. The gate is a promotion authority, not a
replacement for research judgment.

### 1. Write the experiment specification

Create a short specification containing:

- a falsifiable hypothesis;
- the universe and its point-in-time membership rule;
- horizon and rebalance frequency;
- feature definitions and the `asof` rule;
- fees, slippage, and stress multipliers;
- position, drawdown, and turnover limits; and
- numeric kill criteria.

Use [`docs/product-specs/quant-research-loop.md`](docs/product-specs/quant-research-loop.md)
as the template. For work longer than 30 minutes, create an execution plan in
`docs/exec-plans/active/` before implementation.

### 2. Implement within the architecture

Put code in the correct domain and preserve the dependency direction:

```text
Types → Config → Repo → Service → Runtime → Reports
```

Feature functions must receive point-in-time data, not a full future-bearing
DataFrame. Risk decisions belong in `src/domains/risk/`; provider boundaries
belong in `src/providers/`.

### 3. Run the deterministic smoke test

```bash
QUANT_RUN_ID=smoke-42 PYTHONPATH=. python scripts/run-backtest.py --seed 42
```

Inspect the emitted metrics and the run artifacts. Query them with:

```bash
PYTHONPATH=. python scripts/query-metrics.py --run smoke-42 --metric sharpe
PYTHONPATH=. python scripts/query-logs.py --run smoke-42 --filter level=ERROR
```

### 4. Run the promotion gate

```bash
QUANT_RUN_ID=gate-42 PYTHONPATH=. python scripts/run-eval.py --seed 42 --backend auto
```

Do not promote based on an in-sample result or a single attractive chart. Read
the JSON verdict, OOS metrics, selected candidates, backend identity, and run
manifest.

### 5. Validate and review

```bash
scripts/quant-harness.sh check --seed 42
```

Keep changes small, encode decisions in `docs/`, and attach reproducible
evidence to the change. A flaky strategy result should trigger a follow-up run;
it should not be silently treated as proof.

## Evaluation gate

The gate runs a deterministic synthetic panel through:

```text
market data → split adjustment → point-in-time universe →
cost-aware backtest → purged/embargoed folds →
train-only candidate selection → OOS metrics → stress tests
```

The current blocking thresholds are:

| Metric | Requirement |
|---|---:|
| OOS annualized Sharpe | `> 0.5` |
| Deflated Sharpe | `> 0.95` |
| Slippage stress ×2 Sharpe | `> 0` |
| Slippage stress ×5 Sharpe | `> -1.0`; informational unless deeply negative |
| OOS maximum drawdown | `> -15%` |

The JSON output includes `verdict`, `backend`, `sharpe_oos`, `dsr`,
`stress_x2`, `stress_x5`, `max_dd`, `picks`, and `candidates`. `K` in the
Deflated Sharpe calculation includes candidate configurations proposed by the
agent layer; proposing more alternatives increases the multiple-testing
penalty.

Full policy, known limitations, and calibration evidence are in
[`docs/EVALUATION.md`](docs/EVALUATION.md) and
[`docs/design-docs/honest-eval.md`](docs/design-docs/honest-eval.md).

## Runtime boundary

The project is deliberately hybrid:

```text
Python: data orchestration, research workflow, gate, DSR, reference oracle
                              │ inspectable CSV boundary
Rust:   deterministic hot-loop backtest and cross-platform control plane
```

### Python responsibilities

- research-domain models, repositories, services, and providers;
- orchestration of the evaluation gate and candidate selection;
- Deflated Sharpe and report generation;
- the reference implementation used for conformance and fallback;
- agent proposals and deterministic replay of LLM responses.

### Rust responsibilities

- the `doctor`, `boot`, and `check` control-plane commands;
- the standard-library-only numerical hot loop in `crates/quant-core`;
- a portable executable entrypoint for repository automation.

Rust is promoted for speed and a stable executable boundary, not because
Python is being deleted. The Python oracle remains necessary to detect semantic
drift. Rust and Python must agree within the documented tolerance.

Choose the backend explicitly when diagnosing or benchmarking:

```bash
# Normal path: Rust when the release binary exists, Python otherwise
PYTHONPATH=. python scripts/run-eval.py --seed 42 --backend auto

# Fail closed if the Rust release binary is not available
PYTHONPATH=. python scripts/run-eval.py --seed 42 --backend rust

# Force the reference oracle
PYTHONPATH=. python scripts/run-eval.py --seed 42 --backend python

# Compare runtime and numerical conformance
PYTHONPATH=. python scripts/bench-rust.py
```

The boundary and conformance contract are documented in
[`docs/design-docs/rust-core.md`](docs/design-docs/rust-core.md).

## Architecture and invariants

Cross-cutting capabilities such as market data, clock, telemetry, and LLM
access pass through provider interfaces. The composition root is
`src/wiring.py`; the complete layer contract is in
[`ARCHITECTURE.md`](ARCHITECTURE.md).

The blocking invariants are:

- **No lookahead:** features use only timestamps `<= t`.
- **Determinism:** use seeded randomness and controlled clocks.
- **Costs and risk:** fees/slippage are modeled and risk breaches raise.
- **Layering:** dependencies only point forward through the domain layers.
- **Boundary parsing:** external data is validated before it enters domain logic.
- **Taste:** file/function size, logging, and secret checks remain enforceable.

If a rule matters, encode it as a guard with positive and negative proof. Do
not rely on README prose alone.

## Observability and command reference

Each run writes the following evidence under `runs/<run-id>/`:

```text
manifest.json   seed, Git SHA, config, version, and backend identity
logs.jsonl      structured events and errors
metrics.jsonl   queryable research and gate metrics
traces.jsonl    provider and execution traces where applicable
```

| Command | Purpose |
|---|---|
| `quant-harness.sh doctor` | Validate repository contract and required paths |
| `quant-harness.sh boot --seed 42 --run-id ID` | Create a reproducible run manifest |
| `quant-harness.sh check --seed 42 --run-id ID` | Run the complete blocking contract |
| `QUANT_RUN_ID=ID python scripts/run-backtest.py --seed 42` | Run the deterministic smoke backtest |
| `python scripts/run-eval.py --backend auto` | Run the promotion gate |
| `python scripts/evaluate-quant-harness.py` | Run the versioned harness scorecard |
| `python scripts/bench-rust.py` | Compare Python and Rust backends |
| `python scripts/doc-garden.py --scan` | Find stale documentation markers |
| `python scripts/gc-scan.py` | Find duplicated helpers and unsafe probing |

## Repository map

```text
AGENTS.md                  agent entrypoint and progressive-disclosure map
ARCHITECTURE.md            layer and provider contracts
src/                       Python research domains and providers
evals/                     walk-forward evaluation, gate, and Rust bridge
crates/quant-core/         Rust numerical backtest core
crates/harness-cli/        Rust cross-platform control plane
scripts/                   install, run, benchmark, docs, and observability tools
linters/                   blocking architecture and quality checks
tests/                     structure, evaluation, agent, and conformance tests
docs/                      specifications, policies, plans, and decisions
runs/                      local run evidence; do not commit generated runs
```

## Development and validation

Run focused checks while editing:

```bash
python linters/run_all.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. pytest tests/ evals/ -q -p no:cacheprovider
python scripts/doc-garden.py --scan
python scripts/gc-scan.py
git diff --check
```

For the full repository contract, prefer:

```bash
scripts/quant-harness.sh check --seed 42
```

The local `pytest` command disables auto-loaded plugins because unrelated global
plugins can otherwise change the environment. The control-plane check applies
the same isolation.

Before opening a PR:

1. confirm the relevant source-of-truth documents were updated;
2. confirm no lookahead and determinism checks pass;
3. compare Rust and Python if numerical code changed;
4. inspect the run manifest and metrics; and
5. keep the change small and explain any remaining technical debt.

## Documentation map

- [`AGENTS.md`](AGENTS.md) — agent operating contract and reading map;
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — dependency direction and providers;
- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) — seeds and evidence;
- [`docs/NO_LOOKAHEAD.md`](docs/NO_LOOKAHEAD.md) — point-in-time contract;
- [`docs/RISK_LIMITS.md`](docs/RISK_LIMITS.md) — enforced risk boundaries;
- [`docs/EVALUATION.md`](docs/EVALUATION.md) — gate policy and thresholds;
- [`docs/SECURITY.md`](docs/SECURITY.md) — secrets and data handling;
- [`docs/RELIABILITY.md`](docs/RELIABILITY.md) — runtime failure rules;
- [`docs/decisions/`](docs/decisions/) — accepted architectural decisions;
- [`docs/exec-plans/`](docs/exec-plans/) — active, completed, and deferred work.

## Attribution and disclaimer

The agent-first operating model is informed by [OpenAI's Harness engineering
article](https://openai.com/index/harness-engineering/). This repository is an
independent implementation and is not endorsed by OpenAI.

Research harness only. It is not financial advice and does not execute live
trades.

Released under the [MIT License](LICENSE).
