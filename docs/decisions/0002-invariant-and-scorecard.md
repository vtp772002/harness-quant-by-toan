# 0002 — Moi rule phai co guard + scorecard hanh vi

- Ngay: 2026-09-13. Trang thai: accepted.
- Cam hung: harness-by-victoria (encode-invariant skill + evaluate-harness.sh).

## Context
Docs da co nhieu chuan (NO_LOOKAHEAD, REPRODUCIBILITY, RISK_LIMITS) nhung chi
linter + pytest moi bien chung thanh luat that. Can mot hop dong統一 cho moi rule moi.

## Quyet dinh
1. Rule moi chi duoc chap nhan khi di kem: guard co hoc (linter/test, nam trong owner
   hien co — khong dung framework song song), positive proof + negative proof,
   diagnostic neu ro item vi pham + cach sua. Theo skill `.agents/skills/encode-invariant/`.
2. Scorecard `scripts/evaluate-quant-harness.py` la thuoc do suc khoe harness,
   output JSON versioned (`quant-scorecard-v1`), chay local + CI. That bai o case
   blocking = khong merge.
3. Khong suy policy tu convention/code cu. Check cu khong co authority la mismatch
   can bao cao, khong phai co so mo rong.

## He qua
- Them rule = them guard + proof, khong phai them doan van.
- Scorecard thay cho cam giac "harness chac on" bang so lieu.
