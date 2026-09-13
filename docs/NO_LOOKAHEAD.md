# NO_LOOKAHEAD — chuan point-in-time (blocking)

1. Moi feature function nhan `bars_asof` (da filter `ts <= t` o repo). Khong nhan full df roi tu filter.
2. Cam: `.shift(-`, `future`, `lead(`, `bfill`, join khong asof, `close[t+1]` return.
3. `Signal.asof <= Signal.ts` luon dung — co structural test random sampling.
4. Repo la bien duy nhat: `get_asof()` la ham duy nhat tra slice qua khu.
5. Backtest loop: `bars.iloc[:i+1]` — chay linter truoc moi merge.
