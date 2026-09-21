# Skill: self-review-loop (Ralph Wiggum Loop)

After implementation:

1. Run `python linters/run_all.py` and the focused pytest command.
2. Review the diff yourself; every comment must become a fix or a documentation
   update.
3. Request agent review by running `python scripts/gc-scan.py` and
   `python scripts/doc-garden.py --scan`.
4. Repeat until every check is green, then open the PR. Keep the PR below 400
   changed lines unless a decision record justifies more.
