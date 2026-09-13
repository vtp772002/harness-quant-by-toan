# Exec Plan: Honest-Eval Stack (Phase 30 ngay)

## Goal
Mot eval xanh o day thuc su co nghia. Chot 4 lo hong noi doi lon nhat voi agent quant:
survivorship bias, cost phang, chon loc nhieu lan thu (multiple testing), train/test rinh nhau.

## Scope (4 workstreams, moi cai 1-3 PRs ngan)
1. **PIT universe** — `Listing` (list/delist dates) + `UniverseRepo.get_members(t)` + split-adjustment.
   Backtest chi trade member song tai t. Xong khi: test CCC mat sau delist, AAA lien tuc qua split.
2. **Regime cost model** — `RegimeCostModel`: slip phu thuoc vol regime + participation rate,
   stress x2/x5 bat buoc trong gate. Xong khi: slip don dieu theo qty va vol, deterministic.
3. **Purged-embargo CV + Deflated Sharpe** — `evals/purged_cv.py`, `evals/deflated_sharpe.py`
   (Acklam inverse-normal, khong them scipy), gate chon lookback tren train, danh gia OOS.
   K = so config da thu. Xong khi: gate deterministic, DSR test voi gia tri biet truoc.
4. **Gate + calibration** — `evals/gate.py` + `scripts/run-eval.py`, nguong:
   OOS Sharpe>0.5, DSR>0.95, stress x2/x5 Sharpe>0, maxDD>-15%.
   Synthetic market hieu chinh de PASS (chung minh plumbing, KHONG phai claim co alpha that).

## Non-goals (de lai phase sau)
- Data vendor that (van synthetic), duckdb prod repo, borrow/short costs, intraday LOB.
- Toi uu toc do (cache, slice) — phase 60 ngay.

## Decision log (append-only)
- 2026-09-13: DSR tu viet (erf + Acklam) thay vi scipy — giu boring deps, deterministic.
- 2026-09-13: ref_vol la prior co dinh (0.01), khong uoc luong tu full-sample — tranh leak vao cost.
- 2026-09-13: Gate chon lookback tren train moi fold (that), K=3 trials vao DSR — minh hoa selection that.
- 2026-09-13: Synthetic PASS chi nghia la plumbing dung. Ghi ro trong design doc de khong tu lua.
- 2026-09-13: BUG tim thay khi chay that — DSR tron don vi (trial_var annualized vs sr_hat daily) nen DSR恒=0.
  Fix: nhat quan daily + trial_var = phuong sai candidates trong-fold. Linter khong bat duoc — them test DSR known-values.
- 2026-09-13: n_days 300→756 — Sharpe per-fold SE ~1.6 nen selection nhu tung xu. 756 ngay on dinh hon.
- 2026-09-13: Deadband min_trade=25 (strategy, khong phai hack) — turnover hang ngay an het edge (~16bps/trade vs ~4bps edge).
- 2026-09-13: x5 blocking→informational (floor -1.0) — strategy Sharpe 2.08 van rot x5; gate cung se giet do that.

## Acceptance
`python linters/run_all.py` xanh + `scripts/run-eval.py --seed 42` PASS 2 lan byte-identical +
`pytest tests/ evals/` xanh.
