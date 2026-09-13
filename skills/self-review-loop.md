# Skill: self-review-loop (Ralph Wiggum Loop)
Sau khi implement:
1. `python linters/run_all.py` + `pytest -x -q`.
2. Tự review diff: mỗi comment phải thành fix hoặc doc update.
3. Request agent-review: chạy `python scripts/gc-scan.py` + `doc-garden.py --scan`.
4. Loop tới khi tất cả xanh mới mở PR. PR <400 lines.
