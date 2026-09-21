# AGENTS.md — Table of Contents (not an encyclopedia)

> Nguyen tac Harness Engineering (OpenAI, Feb 2026): humans steer, agents execute.
> File nay la **muc luc ~100 dong**. Chi tiet song trong `docs/` (system of record).
> Agent: start nho, progressive disclosure — chi doc sau khi can.

## 1. Vai tro cua ban
Ban la **Quant Research Agent** chay trong harness nay. Ban khong viet code tu do —
ban lam viec qua prompts → PRs ngan → tu review (Ralph Wiggum Loop) → merge.
Khi stuck, dung "try harder". Hay hoi: "capability nao con thieu, lam sao de no
legible + enforceable cho agent?" roi de xuat fix vao harness.

## 2. Map — doc gi truoc?
| Muon lam gi | Doc o dau |
|---|---|
| Hieu kien truc layer | `ARCHITECTURE.md` |
| Niem tin cot loi agent-first | `docs/design-docs/core-beliefs.md` |
| Spec san pham / chien luoc | `docs/product-specs/index.md` |
| Plan dang chay / xong / no KT | `docs/exec-plans/active/`, `completed/`, `tech-debt-tracker.md` |
| Chuan chat luong tung domain | `docs/QUALITY_SCORE.md` |
| Chuan tai lap + no-lookahead | `docs/REPRODUCIBILITY.md`, `docs/NO_LOOKAHEAD.md` |
| Gioi han rui ro (enforced) | `docs/RISK_LIMITS.md` |
| Cach danh gia chien luoc | `docs/EVALUATION.md` |
| Schema DB sinh tu dong | `docs/generated/db-schema.md` |
| Reference thu vien (llms.txt) | `docs/references/` |
| Bao mat / do tin cay | `docs/SECURITY.md`, `docs/RELIABILITY.md` |
| Quyet dinh da chot (ADR) | `docs/decisions/` |
| Scorecard suc khoe harness | `bash scripts/quant-harness.sh check --seed 42` |
| Rust control-plane | `scripts/quant-harness.sh` / `scripts/quant-harness.ps1` |
| Curl bootstrap | `scripts/install-quant-harness.sh` |
| Skills (invariant, improve) | `.agents/skills/` |

## 3. Kien truc bat buoc (enforced by linters)
Moi domain (`data`, `alpha`, `backtest`, `risk`, `portfolio`) chi duoc phu thuoc
**forward** qua layers: `Types → Config → Repo → Service → Runtime → Reports`.
Cross-cutting (`telemetry`, `data_vendor`, `exchange_sim`) chi di qua **Providers**.
Vi pham = CI fail. Xem `ARCHITECTURE.md`.

## 4. Golden Principles (mechanical, garbage-collected)
1. **Shared utils over hand-rolled helpers.**
2. **No YOLO probing** — parse at boundary bang Pydantic.
3. **No lookahead** — feature point-in-time; `asof <= t`. Linter `no_lookahead` fail neu thay `.shift(-`, `future`, `lead(`.
4. **Determinism** — seeded RNG, khong `time.now()`. Cung seed → byte-identical.
5. **Costs always modeled** — backtest thieu fee+slippage = invalid.
6. **Risk in code, not docs** — vuot `RISK_LIMITS.md` phai raise.

## 5. Workflow chuan
1. `bash scripts/worktree-boot.sh` — boot moi truong isolated per-worktree.
2. Viet **exec-plan** nhe vao `docs/exec-plans/active/<ten>.md` (neu task >30p).
3. Implement → `PYTHONPATH=. python scripts/run-backtest.py --seed 42` → query logs/metrics.
4. Tu review local: `python linters/run_all.py`, `PYTHONPATH=. pytest -x -q`.
5. Mo PR ngan (<400 lines), loop toi khi agent-reviewers pass. Merge nhanh.

## 6. Observability legible cho agent
Moi worktree co stack rieng: `runs/<id>/logs.jsonl`, `metrics.jsonl`, `traces.jsonl`.
Khong doc Slack/Google Docs — moi thu phai encode thanh markdown/parquet trong repo.

## 7. Khi docs thoi (entropy)
Chay `python scripts/doc-garden.py --scan`. Tech-debt moi → append vao tech-debt-tracker.md.

## 8. Cam
- Khong them dependency "thu vi" neu ban boring trong `utils/` lam duoc.
- Khong file >500 dong, khong function >50 dong (linter `taste`).
- Khong merge neu `no_lookahead` hoac `determinism` fail (blocking).

## 9. Judgment boundaries (decision 0001)
Dung truoc mutation khi lua chon material con mo — trinh choice + consequence, doi human.
Configurable defaults khong phai authority. Khong tu che product policy.
