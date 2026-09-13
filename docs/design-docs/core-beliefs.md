# Core Beliefs — agent-first (adapted tu OpenAI Harness Engineering)

1. Humans steer, agents execute. Nguoi viet prompt + acceptance criteria, agent viet moi dong code.
2. Legibility > cleverness. Code phai de agent 6 thang sau reason duoc tu repo only.
3. Map, not manual. AGENTS.md la muc luc; chi tiet progressive disclosure trong docs/.
4. Invariants enforced, implementations free. Linter giu bien; trong bien agent tu do.
5. No lookahead, always. Feature vi pham point-in-time la bug P0 du Sharpe cao.
6. Determinism la correctness. Khong tai lap byte-identical = khong merge.
7. Costs + risk in code. Backtest thieu fee/slippage hoac risk chi trong docs = invalid.
8. Throughput wins. PR ngan, merge nhanh, corrections cheap. Flake -> follow-up, khong block.
9. Entropy compounds. Golden principles + garbage collection hang ngay.
10. Boring tech. Uu tien thu agent model duoc: pydantic, pandas, duckdb, stdlib.
