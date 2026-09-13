# REPRODUCIBILITY — determinism (blocking)

1. Moi randomness qua `src/utils/rng_logging.seeded_rng(seed)`.
2. Cam `random.*`, `time.time()`, `datetime.now()` ngoai `providers/clock.py`.
3. Cung `--seed` -> equity curve byte-identical (test `test_determinism` hash parquet).
4. Khong `dict` iteration cho logic thu tu, khong `set` sampling khong seed.
5. Ghi `seed + git sha + config` vao `runs/<id>/manifest.json` moi run.
