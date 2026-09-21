# 0003 — Rust control plane with thin shell adapters

- Ngay: 2026-09-21. Trang thai: accepted.
- Context: harness da co quant logic va scorecard, nhung chua co mot entrypoint
  cross-platform de agent boot, tao evidence, va chay cung mot validation
  contract. README va shell script dang mo ta nhieu lenh rieng le.

## Quyet dinh

1. Rust la control plane nho, std-only: `doctor`, `boot`, va `check`.
2. Bash va PowerShell chi chuyen tiep lenh, khong lap lai policy hay quant
   logic.
3. Python tiep tuc la reference implementation cho pandas/Pydantic, eval va
   scorecard; Rust khong thay the reference khi chua co conformance proof.
4. `check` phai dat `PYTHONPATH=.` va tat auto-loaded pytest plugins de ket qua
   khong phu thuoc plugin toan cuc trong may agent.

## He qua

- Agent co mot contract discoverable va inspectable thay vi nho cac lenh roi rac.
- Rust them mot build surface nho, doi lai co manifest/evidence va failure
  boundary ro rang.
- Live data, broker, LLM, va deployment van la product-owned decisions; harness
  khong tu suy dien hay cap credential.

## Alternatives rejected

- Python CLI moi: trung lap orchestration va lam mo ranh gioi "it Python".
- Shell-only orchestration: khong co contract typed/portable du tot cho
  PowerShell.
- Rust thay toan bo backtest: vi pham nguyen tac Python reference + conformance.
