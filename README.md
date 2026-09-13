# harness-quant-by-toan — Agent-first harness for AI quant research

> Humans steer, agents execute. Harness này không viết strategy giúp bạn —
> nó làm cho mọi strategy (người hay agent đề xuất) **buộc phải trung thực**:
> point-in-time, sau costs, chống overfit bằng thống kê, tái lập byte-identical.

Mọi dòng code, test, docs, eval trong repo đều do agent viết qua
prompts → PRs ngắn → tự review (Ralph Wiggum Loop) → merge.
Con người chỉ làm 3 việc: thiết kế môi trường, ghi ý định, xây vòng lặp feedback.
Triết lý gốc: [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/) (02/2026).

---

## Mục lục

1. [Quickstart](#1-quickstart)
2. [Vòng lặp nghiên cứu chuẩn](#2-vòng-lặp-nghiên-cứu-chuẩn)
3. [Đọc verdict gate](#3-đọc-verdict-gate)
4. [Kiến trúc](#4-kiến-trúc)
5. [Từng phần trong repo](#5-từng-phần-trong-repo)
6. [Lệnh tra cứu (cheatsheet)](#6-lệnh-tra-cứu-cheatsheet)
7. [Luật bất biến (CI block nếu phá)](#7-luật-bất-biến-ci-block-nếu-phá)
8. [Agent layer: agents propose, gate disposes](#8-agent-layer-agents-propose-gate-disposes)
9. [Rust core (tăng tốc, optional)](#9-rust-core-tăng-tốc-optional)
10. [Scorecard sức khỏe harness](#10-scorecard-sức-khỏe-harness)
11. [Số liệu hiệu chuẩn](#11-số-liệu-hiệu-chuẩn)
12. [Mở rộng](#12-mở-rộng)
13. [Ghi nhận nguồn](#13-ghi-nhận-nguồn)

---

## 1. Quickstart

Yêu cầu: Python ≥ 3.11, Rust toolchain (chỉ khi dùng `crates/quant-core`).

```bash
bash scripts/worktree-boot.sh                      # boot môi trường isolated per-worktree
PYTHONPATH=. python scripts/run-backtest.py --seed 42   # smoke test (~1s)
PYTHONPATH=. python scripts/run-eval.py --seed 42       # honest-eval gate → PASS/FAIL
python linters/run_all.py                          # 4 linters (blocking)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. pytest tests/ evals/ -q -p no:cacheprovider
PYTHONPATH=. python scripts/evaluate-quant-harness.py   # behavior scorecard
```

> Lưu ý môi trường: mọi lệnh Python cần `PYTHONPATH=.`. Biến `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`
> để né plugin `httpx` cũ vỡ trên Python 3.13 (lỗi máy cá nhân, không phải harness).

Kết quả đúng khi setup xong: gate `PASS`, linters 4/4 xanh, pytest 25 passed, scorecard 8/8.

---

## 2. Vòng lặp nghiên cứu chuẩn

1. **Viết spec 1 trang** theo `docs/product-specs/quant-research-loop.md`:
   hypothesis (falsifiable), universe, horizon, costs, risk, kill-criteria số hóa.
   Task > 30 phút → tạo exec-plan `docs/exec-plans/active/<ten>.md`.
2. **Code theo layer** (`ARCHITECTURE.md`): signal mới viết logic thuần trong
   `src/domains/alpha/` (chỉ nhận `bars_asof`, không bao giờ nhận full dataframe).
3. **Smoke**: `run-backtest.py --seed 42`.
4. **Gate** (`run-eval.py --seed 42`) — verdict này mới là quyết định thật.
5. **Tự review**: linters + pytest tới khi xanh → PR < 400 dòng → merge nhanh.
   Flake → rerun follow-up, không block.

Mọi quyết định ngoài code (chat, Slack) phải encode thành file trong `docs/`,
nếu không với agent nó coi như không tồn tại.

---

## 3. Đọc verdict gate

`scripts/run-eval.py` trả JSON: `verdict`, `sharpe_oos`, `dsr`, `stress_x2/x5`,
`max_dd`, `picks` (lookback được chọn mỗi fold), `candidates`.

| Ngưỡng PASS (sau costs, OOS) | Giá trị |
|---|---|
| OOS Sharpe (annualized) | > 0.5 |
| Deflated Sharpe (K = số config/proposal đã thử) | > 0.95 |
| Stress slippage x2 | Sharpe > 0 (blocking) |
| Stress slippage x5 | > −1.0 (informational, chỉ block khi âm sâu) |
| Max drawdown OOS | > −15% |

| Verdict FAIL thì sao | Hành động |
|---|---|
| `sharpe`/`dsr` thấp | Edge yếu hoặc overfit — giết strategy hoặc sửa hypothesis, ghi tech-debt |
| `stress_x2 < 0` | Sống nhờ cost rẻ, turnover cao — thêm deadband, giảm turnover |
| `x5` âm nhưng > −1.0 | Cảnh báo, không block — ghi vào PR cho reviewer biết |
| `picks` nhảy mỗi fold | Selection không ổn định — nghi ngờ, cần thêm dữ liệu |

Pipeline gate: synthetic market 756 ngày × 4 mã → split-adjust → universe PIT →
panel momentum + regime costs → purged-embargo 3 folds (purge = max lookback + 1) →
chọn lookback trên train mỗi fold → OOS + DSR + stress. Deterministic theo seed.

---

## 4. Kiến trúc

Mỗi domain (`data`, `alpha`, `backtest`, `risk`, `portfolio`) chỉ phụ thuộc **forward**:

```
Types → Config → Repo → Service → Runtime → Reports
```

Cross-cutting (`telemetry`, `data_vendor`, `exchange_sim`, `clock`, `llm`) chỉ đi qua
**Providers** — interface显式 duy nhất. Vi phạm = CI fail kèm hướng dẫn sửa trong message lỗi.
Composition root duy nhất: `src/wiring.py`. Chi tiết: `ARCHITECTURE.md`.

6 golden principles (enforced cơ học, garbage-collected hằng ngày):
shared utils · parse-at-boundary (Pydantic, no YOLO probing) · no lookahead (`asof ≤ t`) ·
determinism (seeded RNG, cùng seed → byte-identical) · costs always modeled ·
risk in code (vượt ngưỡng là `raise`, không warn).

---

## 5. Từng phần trong repo

```
AGENTS.md                  Mục lục cho agent (~80 dòng, không phải bách khoa toàn thư)
ARCHITECTURE.md            Hợp đồng layer + providers
src/domains/data/          Bars, PIT repo, UniverseRepo (list/delist), split-adjust, synthetic market
src/domains/alpha/         Momentum + indicators/tools + reports + agents pipeline + schemas
src/domains/backtest/      Event-loop backtest deterministic + reports (Sharpe/maxDD/turnover)
src/domains/risk/          check_limits → raise RiskBreach
src/domains/portfolio/     Position sizing
src/providers/             clock (wall-clock duy nhất) · telemetry (JSONL per-worktree)
                           market (Simple + RegimeCostModel) · llm (protocol + Replay/Live)
src/utils/                 seeded RNG, structured logging, map-with-concurrency
src/wiring.py              Composition root (demo run seeded)
evals/                     purged_cv · deflated_sharpe (tự viết, không scipy)
                           gate (promotion authority) · rust_core (bridge)
crates/quant-core/         Rust hot-loop (std-only, CSV boundary), xem mục 9
linters/                   layering · no_lookahead · determinism · taste (blocking)
tests/                     structure · honest_eval · agent_layer · rust_core (conformance)
scripts/                   worktree-boot · run-backtest · run-eval · query-logs/metrics
                           bench-eval · bench-rust · doc-garden · gc-scan · evaluate-quant-harness
docs/                      system of record: design-docs · product-specs · exec-plans
                           decisions (ADR) · EVALUATION · QUALITY_SCORE · RISK_LIMITS · ...
.agents/skills/ · skills/  encode-invariant · improve-harness · reproduce-backtest
                           validate-no-lookahead · self-review-loop
.github/workflows/         gates.yml (blocking tối thiểu + full-eval non-blocking)
```

---

## 6. Lệnh tra cứu (cheatsheet)

```bash
PYTHONPATH=. python scripts/query-metrics.py --metric sharpe      # Sharpe các run
PYTHONPATH=. python scripts/query-metrics.py --metric gate.dsr    # DSR
PYTHONPATH=. python scripts/query-logs.py --filter level=ERROR    # lọc lỗi
python scripts/doc-garden.py --scan    # quét docs thối (TODO/TBD, stale markers)
python scripts/gc-scan.py              # quét helper copy-paste / YOLO probing
PYTHONPATH=. python scripts/bench-eval.py    # benchmark baseline, tìm hot loop
PYTHONPATH=. python scripts/bench-rust.py    # so sánh Python vs Rust core
```

Mỗi worktree có observability stack riêng: `runs/<id>/logs.jsonl`, `metrics.jsonl`,
`traces.jsonl` (+ `manifest.json` ghi seed + config). Teardown sau task.

---

## 7. Luật bất biến (CI block nếu phá)

- **No lookahead**: feature chỉ dùng `ts ≤ t`. Cấm `.shift(-`, `future`, `lead(`, join không asof.
- **Determinism**: mọi random qua `seeded_rng(seed)`; cấm `random.*`, `time.time()`,
  `datetime.now()` ngoài `providers/clock.py`.
- **Costs + risk**: backtest thiếu fee/slippage = invalid; vượt `RISK_LIMITS.md` phải raise.
- **Taste**: file ≤ 500 dòng, hàm ≤ 50 dòng, structured logging, không hardcode secrets.
- **Judgment boundaries** (decision 0001): dừng trước mutation khi lựa chọn material còn mở —
  trình choice + consequence, đợi human. Không tự chế product policy.
- **Rule mới = guard + proof** (decision 0002): kèm positive/negative proof, không thêm văn xuôi suông.

---

## 8. Agent layer: agents propose, gate disposes

Pipeline 4 bước `src/domains/alpha/agents.py`: Indicator → Pattern → Trend → Decision,
chạy tuần tự, deterministic, offline 100%.

- **Tools** (`alpha/tools.py`): RSI/MACD/Stoch/ROC/WillR/ATR + breakout/engulfing/
  range-position/trend-slope — pandas-only (không TA-Lib), pure, PIT-safe.
- **Schemas** (`alpha/schemas.py`): mọi output agent validate Pydantic trước khi đi tiếp.
- **LLM** (`providers/llm.py`): sau `LLMProvider` protocol. `ReplayLLM` cho test/CI
  (chọn response bằng hash context — stateless, deterministic). `LiveLLM`
  (OpenAI-compatible, stdlib HTTPS, key qua env) — thiếu key thì raise, không bao giờ
  chạy trong CI. LLM chỉ thêm narrative/confidence, **số liệu không đổi**.
- **Wiring vào gate**: `run_gate(..., candidate_lookbacks=proposal.candidate_lookbacks)` —
  proposal càng nhiều, DSR phạt càng nặng. Vòng khép kín proposal→gate đã khóa bằng test.

Chưa làm (cần human quyết trước khi code — decision 0001):
provider thật, secrets policy, token budget, LangGraph, live-fire validation.

---

## 9. Rust core (tăng tốc, optional)

`crates/quant-core`: port đúng hot loop `panel_backtest`, std-only zero-dependency,
boundary CSV (`panel.csv` + `members.csv` → `equity.csv`).
Python giữ orchestration (gate, selection, DSR) — Rust **không bao giờ thay reference**.

| lookback | Python | Rust | speedup | lệch equity |
|---|---|---|---|---|
| 5 | 165ms | 33ms | 5.1x | 2.3e-10 |
| 10 | 154ms | 28ms | 5.4x | 2.3e-10 |
| 20 | 151ms | 26ms | 5.9x | 2.3e-10 |

Quy tắc promote: conformance xanh + panel loop Python > 30s (hiện ~0.5s).
Thiếu binary thì conformance tests tự skip, gate Python chạy bình thường.

```bash
cargo build --release -p quant-core
PYTHONPATH=. python scripts/bench-rust.py
```

---

## 10. Scorecard sức khỏe harness

```bash
PYTHONPATH=. python scripts/evaluate-quant-harness.py --seed 42
```

Output JSON versioned (`quant-scorecard-v1`), 8 cases:
authority-entry · docs-map · linters · tests · gate · rust-conformance ·
evidence (manifest) · docs-fresh. Blocking fail = không merge.

---

## 11. Số liệu hiệu chuẩn

Synthetic market (AR(1) φ=0.3 + drift, 4 mã có list/delist, 1 split 2:1) — PASS ở đây
chứng minh **plumbing đúng, không phải alpha thật**. Verdict thật đợi data thật.

Gate seed 42 (CI lock, margin lớn): Sharpe **2.25**, DSR **1.0**, x2 **2.09**,
x5 **1.62** → PASS. Multi-seed 7 seeds: 5 PASS; 2 ca FAIL là marginal thật
(Sharpe ~1.0, DSR < 0.9) — gate từ chối đúng. Bảng đầy đủ: `docs/design-docs/honest-eval.md`.

Ba bug/lệch thiết kế đã tự lòi ra khi chạy thật (ghi decision log):
trộn đơn vị annualized/daily trong DSR · 300 ngày quá ít khiến selection như tung xu ·
stress-x5-blocking giết cả strategy Sharpe 2.08 (đã hạ thành informational).

---

## 12. Mở rộng

Tech-debt ưu tiên (`docs/exec-plans/tech-debt-tracker.md`):
data vendor thật (survivorship-clean) · slippage stochastic seeded · duckdb prod repo ·
selection stability · borrow/short costs + holdout governance · agent-layer slice 2.
Quy trình cải tiến harness: skill `improve-harness` (baseline-to-rerun evidence + decision record).

---

## 13. Ghi nhận nguồn

- OpenAI Harness Engineering (02/2026) — triết lý agent-first, legibility, garbage collection.
- [QuantHarness](https://github.com/Y-Research-SBU/QuantHarness) (MIT) — kiến trúc 4-agent
  (lấy ý tưởng, viết lại hoàn toàn, không copy code).
- [harness-by-victoria](https://github.com/vtp772002/harness-by-victoria) (MIT) —
  decisions/skills/scorecard protocol (lấy ý tưởng, chữ viết lại).

> **Disclaimer**: harness nghiên cứu, không phải lời khuyên tài chính.
> Synthetic PASS không đảm bảo lợi nhuận ngoài đời thực.

> **License**: chưa có file LICENSE (mặc định all rights reserved) — dự kiến MIT.
