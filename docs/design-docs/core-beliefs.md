# Core Beliefs — Agent-First (Adapted from OpenAI Harness Engineering)

1. Humans steer, agents execute. Humans write prompts and acceptance criteria;
   agents implement the code.
2. Legibility beats cleverness. An agent six months later should be able to
   reason from the repository alone.
3. Map, not manual. `AGENTS.md` is a map; detailed guidance is progressively
   disclosed through `docs/`.
4. Enforce invariants, keep implementations free. Linters hold the boundary;
   agents choose the implementation inside it.
5. No lookahead, ever. A point-in-time violation is a P0 bug even when Sharpe is
   high.
6. Determinism is correctness. If a run cannot be reproduced byte-for-byte, it
   does not merge.
7. Costs and risk belong in code. A backtest that models neither costs nor risk
   in code is invalid.
8. Throughput wins. Small PRs, fast merges, and cheap corrections are preferred.
   Flaky results get follow-up runs rather than silent acceptance.
9. Entropy compounds. Garbage-collect stale docs and enforce golden principles.
10. Prefer boring technology: Pydantic, pandas, DuckDB, and the standard
    library are easier for agents to model.
