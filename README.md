# Quant Research Harness

Agent-first harness for quantitative research. It makes research runs
reproducible and blocks common mistakes before a strategy is promoted:

- point-in-time data and no lookahead;
- transaction costs and risk limits;
- deterministic seeds and auditable run artifacts;
- purged walk-forward evaluation with out-of-sample gates.

This repository is a research control system, not a trading system and not a
claim that the included synthetic strategy has a real-world edge.

**Version:** `0.2.0` · **License:** [MIT](LICENSE) · **Design reference:**
[OpenAI — Harness engineering](https://openai.com/index/harness-engineering/)

## Choose your path

| Goal | Start here |
|---|---|
| Run this repository locally | [Quickstart](#quickstart) |
| Add the harness to another quant repository | [Curl installer](#curl-installer) |
| Run a research experiment | [Research loop](#research-loop) |
| Understand Python and Rust | [Runtime boundary](#runtime-boundary) |
| Change the harness | [Development checks](#development-checks) |

## Quickstart

### Requirements

- Python `>= 3.11`
- Rust toolchain (`cargo`)
- Bash on Unix-like systems; PowerShell on Windows

### Run the contract checks

From the repository root:

```bash
scripts/quant-harness.sh doctor
scripts/quant-harness.sh boot --seed 42
scripts/quant-harness.sh check --seed 42
```

`check` is the main health command. It runs the Rust control-plane checks,
linters, Python tests, the evaluation gate, Rust/Python conformance, and the
behavior scorecard.

For a single research smoke test:

```bash
PYTHONPATH=. python scripts/run-backtest.py --seed 42
PYTHONPATH=. python scripts/run-eval.py --seed 42 --backend auto
```

On Windows, use the PowerShell adapter:

```powershell
.\scripts\quant-harness.ps1 doctor
.\scripts\quant-harness.ps1 boot --seed 42 --run-id local
.\scripts\quant-harness.ps1 check --seed 42
```

Every run writes inspectable artifacts under `runs/<run-id>/`, including a
manifest, JSONL logs, metrics, and traces.

## Curl installer

Install the control-plane into an existing quant repository:

```bash
curl -fsSL https://raw.githubusercontent.com/vtp772002/harness-quant-by-toan/main/scripts/install-quant-harness.sh \
  | bash -s -- --yes --target "$PWD"
```

The installer downloads the managed payload from this repository, builds the
Rust control-plane locally, and installs `scripts/bin/quant-harness`. It uses
merge-safe behavior by default:

```bash
# Preview changes without writing files
curl -fsSL https://raw.githubusercontent.com/vtp772002/harness-quant-by-toan/main/scripts/install-quant-harness.sh \
  | bash -s -- --dry-run --target "$PWD"

# Replace managed files intentionally
curl -fsSL https://raw.githubusercontent.com/vtp772002/harness-quant-by-toan/main/scripts/install-quant-harness.sh \
  | bash -s -- --yes --override --target "$PWD"
```

The installer does not install credentials, broker integrations, live trading,
or product policy. Review the script and pin `--ref` to a release or commit
when reproducible bootstrap is required.

## Research loop

Use this loop for each hypothesis:

1. Write a short spec: hypothesis, universe, horizon, costs, risk limits, and
   numeric kill criteria. See
   [`docs/product-specs/quant-research-loop.md`](docs/product-specs/quant-research-loop.md).
2. Implement the signal in the correct domain layer. Features must be
   point-in-time and consume only data available at `t`.
3. Run a seeded backtest:
   `PYTHONPATH=. python scripts/run-backtest.py --seed 42`.
4. Run the promotion gate:
   `PYTHONPATH=. python scripts/run-eval.py --seed 42 --backend auto`.
5. Review the artifacts and run `scripts/quant-harness.sh check --seed 42`
   before opening a small PR.

The gate evaluates net-of-costs out-of-sample behavior using purged and
embargoed folds. A synthetic PASS validates the harness plumbing; it does not
validate a live-market alpha. Gate definitions and thresholds live in
[`docs/EVALUATION.md`](docs/EVALUATION.md).

## Runtime boundary

The project is intentionally hybrid:

```text
Python: data orchestration, research workflow, gate, DSR, reference oracle
                     │ CSV boundary
Rust:   deterministic hot-loop backtest and cross-platform control plane
```

Rust is used where a stable, fast numerical core and portable executable are
valuable. Python remains the reference implementation and fallback, so a Rust
change must agree with the Python oracle within the conformance tolerance.
This preserves research velocity and makes numerical regressions visible.

Select the evaluation backend explicitly when needed:

```bash
PYTHONPATH=. python scripts/run-eval.py --seed 42 --backend auto    # Rust if built, otherwise Python
PYTHONPATH=. python scripts/run-eval.py --seed 42 --backend rust    # require Rust release binary
PYTHONPATH=. python scripts/run-eval.py --seed 42 --backend python  # reference oracle
```

The Rust backtest implementation is documented in
[`docs/design-docs/rust-core.md`](docs/design-docs/rust-core.md). Compare the
two backends with:

```bash
PYTHONPATH=. python scripts/bench-rust.py
```

## Architecture and invariants

Each quant domain (`data`, `alpha`, `backtest`, `risk`, `portfolio`) follows:

```text
Types → Config → Repo → Service → Runtime → Reports
```

Cross-cutting capabilities such as market data, clock, telemetry, and LLM
access go through provider interfaces. The composition root is
`src/wiring.py`; the full contract is in [`ARCHITECTURE.md`](ARCHITECTURE.md).

The blocking invariants are:

- no lookahead: features use only timestamps `<= t`;
- determinism: seeded randomness and no uncontrolled wall-clock reads;
- costs and risk: fees/slippage are modeled and risk breaches raise;
- layer and taste checks: dependency direction, file/function size, and
  structured logging remain enforceable.

If a new rule matters, encode it as a guard with positive and negative proof;
do not rely on README prose alone.

## Repository map

```text
src/                         Python research domains and providers
evals/                       walk-forward evaluation, gate, Rust bridge
crates/quant-core/           Rust numerical backtest core
crates/harness-cli/          Rust cross-platform control plane
scripts/                     bootstrap, run, benchmark, docs, and observability tools
linters/                     blocking architecture and quality checks
tests/                       structure, evaluation, agent, and conformance tests
docs/                        system of record: specs, decisions, plans, and policies
runs/                        local per-run logs, metrics, traces, and manifests
```

Useful documents:

- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) — seeds and run evidence;
- [`docs/NO_LOOKAHEAD.md`](docs/NO_LOOKAHEAD.md) — point-in-time contract;
- [`docs/RISK_LIMITS.md`](docs/RISK_LIMITS.md) — enforced risk boundaries;
- [`docs/SECURITY.md`](docs/SECURITY.md) — security model and reporting;
- [`docs/RELIABILITY.md`](docs/RELIABILITY.md) — failure and recovery rules;
- [`docs/decisions/`](docs/decisions/) — accepted architectural decisions.

## Development checks

Run the focused checks while editing:

```bash
python linters/run_all.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. pytest tests/ evals/ -q -p no:cacheprovider
python scripts/doc-garden.py --scan
python scripts/gc-scan.py
git diff --check
```

For tasks longer than 30 minutes, create an execution plan under
`docs/exec-plans/active/`. Keep product decisions and research assumptions in
the repository so agents can read and enforce them.

## Attribution and disclaimer

The agent-first operating model is informed by [OpenAI's Harness engineering
article](https://openai.com/index/harness-engineering/). This repository is an
independent implementation and is not endorsed by OpenAI.

Research harness only. It is not financial advice and does not execute live
trades.

Released under the [MIT License](LICENSE).
