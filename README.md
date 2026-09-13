# Harness-by-Toan — Agent-first harness for AI quant research

Humans steer, agents execute. Mọi dòng code, test, docs, eval đều do agent viết qua
prompts → PRs ngắn → tự review → merge. Con người thiết kế môi trường, ý định và vòng lặp feedback.

Nguồn ý tưởng: OpenAI Harness Engineering (02/2026), QuantHarness (Y-Research-SBU, MIT),
harness-by-victoria (MIT). Chi tiết attribution trong `docs/design-docs/`.

## Quickstart

```bash
bash scripts/worktree-boot.sh
PYTHONPATH=. python scripts/run-backtest.py --seed 42   # smoke
PYTHONPATH=. python scripts/run-eval.py --seed 42       # honest-eval gate (PASS/FAIL)
python linters/run_all.py                               # 4 linters (blocking)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. pytest tests/ evals/ -q -p no:cacheprovider
PYTHONPATH=. python scripts/evaluate-quant-harness.py   # behavior scorecard
```

## Cái gì ở đâu

| Muốn gì | Đọc/Chạy |
|---|---|
| Giao việc cho agent | `AGENTS.md` (mục lục, ~70 dòng) |
| Kiến trúc layer bắt buộc | `ARCHITECTURE.md` |
| Luật bất biến (lookahead, determinism, costs, risk) | `docs/NO_LOOKAHEAD.md`, `docs/REPRODUCIBILITY.md`, `docs/RISK_LIMITS.md` |
| Gate trung thực (purged CV + Deflated Sharpe + stress) | `evals/gate.py`, `scripts/run-eval.py` |
| Agent layer 4 bước (Indicator→Pattern→Trend→Decision, proposal-only) | `src/domains/alpha/agents.py` |
| Rust hot-loop core (5-6x, CSV boundary, optional) | `crates/quant-core/`, `scripts/bench-rust.py` |
| Quyết định đã chốt (ADR) | `docs/decisions/` |
| Skills | `.agents/skills/`, `skills/` |

## Nguyên tắc vàng

No lookahead · determinism (cùng seed → byte-identical) · costs always modeled ·
risk in code (raise, không warn) · agents propose, gate disposes · PR <400 dòng, merge nhanh.
