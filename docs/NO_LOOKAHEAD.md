# NO_LOOKAHEAD — Point-in-Time Contract (Blocking)

1. Every feature function receives `bars_asof`, already filtered to `ts <= t` by
   the repository. Do not accept a full DataFrame and filter it inside the
   feature.
2. Forbidden patterns include `.shift(-`, `future`, `lead(`, `bfill`, joins
   without `asof`, and returns using `close[t+1]`.
3. `Signal.asof <= Signal.ts` must always hold; structural tests use random
   sampling to check it.
4. The repository is the authority: `get_asof()` is the only function allowed
   to return a historical slice.
5. The backtest loop uses `bars.iloc[:i+1]`. Run the linter before every merge.
