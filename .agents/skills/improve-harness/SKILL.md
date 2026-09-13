---
name: improve-harness
description: Cai tien harness co chung cu baseline-to-rerun. Chi dung khi user yeu cau explicit. Cam tu y sua guidance/tools/validation trong luc lam task khac.
---

# Improve Harness (quant-adapted; y tuong tu harness-by-victoria)

## 1. Baseline truoc
Chay va ghi lai: `python linters/run_all.py`, full pytest, `scripts/run-eval.py --seed 42`,
`scripts/evaluate-quant-harness.py`. Luu output lam baseline.

## 2. Thay doi nho nhat
Mot cai tien = mot PR <400 lines. Khong tron refactor + feature + rule moi.

## 3. Rerun + so sanh
Chay lai toan bo baseline. Cai tien chi dat khi: tat ca xanh nhu baseline (hoac hon),
gate seed 42 van PASS byte-identical, khong them dependency moi neu ban boring lam duoc.

## 4. Ghi decision
Moi cai tien behavior-level phai co `docs/decisions/NNNN-*.md` + cap nhat tech-debt-tracker.
Khong decision = khong merge.
