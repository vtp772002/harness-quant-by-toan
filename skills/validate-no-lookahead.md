# Skill: validate-no-lookahead

Before every alpha or backtest PR:

1. `python linters/no_lookahead.py` must pass.
2. Search the diff manually for `shift\(`, `future`, `lead`, and `bfill`.
3. Spot-check three timestamps and assert that each signal uses only bars with
   `ts <= t`, using `repo.get_asof`.
4. Record the result in the PR checklist.
