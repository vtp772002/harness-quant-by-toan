---
name: encode-invariant
description: Bien rule da chap nhan thanh guard co hoc nho nhat (linter/test) kem positive + negative proof. Dung khi: them bao ve kien truc, reliability, security, quality; chan violation tai dien; bien quyet dinh trong docs/decisions thanh validation. Khong dung de suy policy tu convention, code cu, defaults.
---

# Encode Invariant (quant-adapted; y tuong tu harness-by-victoria)

## 1. Authority gate
Trich dan source chap nhan (VD: docs/NO_LOOKAHEAD.md, docs/decisions/NNNN).
Noi ro: scope, hanh vi cho phep, hanh vi cam, ngoai le. Authority mo → DUNG (xem decision 0001).

## 2. Chon guard nho nhat
Tai su dung owner hien co theo thu tu uu tien: linters/ > tests/ > evals/ > scripts/.
Khong dung framework song song, khong tao source of truth moi.
Rule quant (lookahead, determinism, costs, risk) la blocking; rule style la non-blocking.

## 3. Implement + prove
- Positive proof: case dung phai pass.
- Negative proof: mutation/violation mau phai fail DUNG rule + diagnostic (dung fixture tam, khong de violation trong product files).
- Diagnostic phai co: item vi pham, rule bi pha, source authority, hanh dong tiep theo cu the.

## 4. Bao cao
Authority, scope, owner thay doi, ket qua 2 proof, level enforce (local/CI), risk con lai.
