# AGENTS.md — Quant Research Harness Guide

> Humans steer, agents execute. This file is a map, not an encyclopedia.
> Detailed policy lives in `docs/`, which is the repository system of record.
> Use progressive disclosure: read only the documents required for the task.

## 1. Agent role

You are the Quant Research Agent operating inside this harness. Work through
small, reviewable changes: establish the authority, write an execution plan
when needed, implement, validate, and leave durable evidence in the repository.

When blocked, do not merely try harder. Ask which capability is missing and how
it can become legible and enforceable for the next agent. Propose a guard,
test, or decision record when the missing capability is systemic.

## 2. Read this first

| Task | Source of truth |
|---|---|
| Understand the layer architecture | `ARCHITECTURE.md` |
| Understand the agent-first principles | `docs/design-docs/core-beliefs.md` |
| Write a research specification | `docs/product-specs/index.md` |
| Track active, completed, and deferred work | `docs/exec-plans/` and `docs/PLANS.md` |
| Check domain quality and known gaps | `docs/QUALITY_SCORE.md` |
| Check reproducibility and lookahead rules | `docs/REPRODUCIBILITY.md`, `docs/NO_LOOKAHEAD.md` |
| Check enforced risk limits | `docs/RISK_LIMITS.md` |
| Understand the evaluation gate | `docs/EVALUATION.md` |
| Inspect the generated schema | `docs/generated/db-schema.md` |
| Find library references | `docs/references/` |
| Review security and reliability rules | `docs/SECURITY.md`, `docs/RELIABILITY.md` |
| Review accepted decisions | `docs/decisions/` |
| Run the repository contract | `scripts/quant-harness.sh check --seed 42` |
| Use the Rust control plane | `scripts/quant-harness.sh`, `scripts/quant-harness.ps1` |
| Bootstrap into another repository | `scripts/install-quant-harness.sh` |
| Inspect reusable skills | `skills/` and `.agents/skills/` |

For the shortest user-facing path, start with `README.md`.

## 3. Enforced architecture

Each quant domain (`data`, `alpha`, `backtest`, `risk`, `portfolio`) may only
depend forward through:

```text
Types → Config → Repo → Service → Runtime → Reports
```

Cross-cutting capabilities (`telemetry`, `data_vendor`, `exchange_sim`,
`clock`, and `llm`) must pass through provider interfaces. Violations fail the
layering linter. See `ARCHITECTURE.md` before introducing a new dependency.

## 4. Golden principles

These principles are enforced mechanically where possible:

1. Prefer shared utilities over hand-rolled helpers.
2. Parse at boundaries with Pydantic; do not use YOLO probing.
3. Enforce point-in-time features: `asof <= t`. The no-lookahead linter rejects
   patterns such as `.shift(-`, `future`, and `lead(`.
4. Make runs deterministic: use seeded RNGs and keep uncontrolled clocks out of
   research logic.
5. Always model costs. A backtest without fees and slippage is invalid.
6. Put risk in code. Breaching `RISK_LIMITS.md` must raise, not merely warn.
7. A new rule needs a guard plus positive and negative proof; prose alone is not
   an invariant.

## 5. Standard workflow

1. Run `bash scripts/worktree-boot.sh` when an isolated worktree is needed.
2. For work longer than 30 minutes, create
   `docs/exec-plans/active/<name>.md` before implementation.
3. Implement within the layer contract and preserve the Python reference oracle
   when changing Rust numerical code.
4. Run `scripts/quant-harness.sh check --seed 42` as the canonical validation.
5. For focused checks, run `python linters/run_all.py` and
   `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. pytest tests/ evals/ -q -p no:cacheprovider`.
6. Review the diff, run `python scripts/doc-garden.py --scan`, and keep the PR
   small enough to review quickly.

Python commands require `PYTHONPATH=.`. The check command disables auto-loaded
pytest plugins so results do not depend on unrelated global plugins.

## 6. Runtime and backend contract

Python owns research orchestration, the evaluation gate, DSR, and the reference
implementation. Rust owns the control plane and the deterministic hot-loop
backtest. The CSV boundary is deliberate: it is inspectable, portable, and
allows cross-language conformance tests.

Use `--backend auto` for the normal CLI path, `--backend rust` to fail closed
when the Rust release binary is missing, and `--backend python` to run the
reference oracle explicitly. Never delete the reference implementation merely
because the Rust path is faster.

## 7. Evidence and observability

Every worktree has a run-local observability stack:
`runs/<id>/manifest.json`, `logs.jsonl`, `metrics.jsonl`, and `traces.jsonl`.
Record seeds, Git SHA, configuration, backend identity, and relevant metrics.
Do not rely on Slack or private chat as system-of-record material; encode
decisions and evidence as Markdown, JSON, or Parquet in the repository.

## 8. Documentation hygiene

Run `python scripts/doc-garden.py --scan` when documentation changes. Add new
technical debt to `docs/exec-plans/tech-debt-tracker.md`. Keep `README.md` as a
user-oriented entry point and keep detailed policy in the linked documents.

## 9. Constraints

- Do not add a dependency when a boring shared utility is sufficient.
- Keep files below 500 lines and functions below 50 lines unless an explicit
  decision record justifies an exception.
- Do not merge while `no_lookahead` or `determinism` is failing.
- Do not add live trading, broker credentials, or product policy by inference.

## 10. Judgment boundaries

Before a mutation, identify the document or decision that grants authority. If
a material choice remains open and changes observable behavior, stop and present
the concrete options and consequences to the human. Configurable defaults are
not authority. This rule is recorded in decision `0001`.
