# Honest-Eval Design (system of record cho phase 30 ngay)

## Vi sao 4 mieng nay?
Agent co throughput cao bien moi lac quan trong eval thanh hang tram chien luoc rac.
Thu tu uu tien theo muc do noi doi pho bien:
1. **Survivorship** — backtest tren universe hien tai am tham loai bo ke da chet.
   Fix: membership la ham cua t (`get_members`), delist la su kien first-class.
2. **Cost phang** — fee co dinh bien strategy turnover-cao thanh sieu sao ao.
   Fix: slip = spread co so * vol-regime + impact * sqrt(participation), stress x2/x5.
3. **Multiple testing** — thu 500 bien the, bao cai tot nhat, quen 499 xac chet.
   Fix: K (so trials) di vao Deflated Sharpe; chon hyperparam trong fold, khong ngoai.
4. **Leakage train/test** — trailing window doi qua bien fold.
   Fix: purged-embargo splits, purge >= max_lookback + 1.

## Gia dinh duoc chot (assumptions, co the sai — ghi de agent biet)
- Khop tai gia close, volume bar hien tai coi nhu biet truoc (chap nhan duoc cho daily).
- ref_vol = 0.01 la prior, khong phai uoc luong — neu doi regime that, hieu chinh lai.
- Khong borrow cost / short constraint trong gate v1 (ghi no: tech-debt).
- Synthetic market co momentum that (AR(1) + drift) de gate PASS — day la test plumbing,
  KHONG phai bang chung strategy co loi nhuan. Verdict that doi data that.

## Nguong gate (sau costs, OOS) — giu lam chuan
Sharpe_ann > 0.5, DSR > 0.95, stress x2 > 0 (blocking), x5 > -1.0 (informational),
maxDD > -15%. DAT khong duoc cham holdout cuoi — enforce o phase sau bang hash + ledger.

## Multi-seed calibration (2026-09-13, chay that)
| seed | verdict | Sharpe | DSR | x2 | x5 |
|---|---|---|---|---|---|
| 1 | PASS | 2.13 | 0.997 | 1.47 | 0.28 |
| 2 | FAIL | 0.96 | 0.776 | 1.10 | 1.18 |
| 3 | PASS | 2.08 | 1.000 | 1.99 | -0.22 |
| 7 | PASS | 2.91 | 1.000 | 1.49 | 1.06 |
| 42 (CI lock) | PASS | 2.25 | 1.000 | 2.09 | 1.62 |
| 99 | PASS | 2.19 | 0.999 | 1.46 | 0.81 |
| 123 | FAIL | 1.05 | 0.841 | 0.71 | 0.21 |

5/7 PASS. 2 ca FAIL la marginal that (Sharpe ~1.0, DSR<0.9) — gate tu choi dung.
CI lock seed 42 (margin lon). Selection instability la tech-debt phase 60 ngay.
