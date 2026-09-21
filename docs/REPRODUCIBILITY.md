# REPRODUCIBILITY — determinism (blocking)

1. Route all randomness through `src/utils/rng_logging.seeded_rng(seed)`.
2. Forbid `random.*`, `time.time()`, and `datetime.now()` outside
   `providers/clock.py`.
3. The same `--seed` must produce a byte-identical equity curve; the
   `test_determinism` test hashes the Parquet output.
4. Do not use dictionary iteration for ordered logic or unseeded set sampling.
5. Record the seed, Git SHA, and configuration in
   `runs/<id>/manifest.json` for every run.
