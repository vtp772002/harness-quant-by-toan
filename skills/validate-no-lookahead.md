# Skill: validate-no-lookahead
Trước mọi PR alpha/backtest:
1. `python linters/no_lookahead.py` phải xanh.
2. Grep thủ công `shift\(`, `future`, `lead`, `bfill` trong diff.
3. Spot-check: pick 3 timestamps, assert signal chỉ dùng bars ts<=t (dùng repo.get_asof).
4. Ghi kết quả vào PR checklist.
