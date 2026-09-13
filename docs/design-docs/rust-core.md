# Rust Core Design (system of record)

## Kien truc: hybrid, khong rewrite
Python giu orchestration (gate, selection, DSR, universe, telemetry) — noi agent lam viec.
Rust (`crates/quant-core`) chi port hot loop (`panel_backtest` day-loop) — noi may lam viec.
Boundary: CSV (`panel.csv`, `members.csv` -> `equity.csv` + stdout meta). Boring, inspectable,
parse duoc bang mat thuong. Zero dependencies (std only) — khong serde, khong tokio.

## Tai sao CSV chu khong phai PyO3?
- Agent doc/debug duoc boundary ma khong can hieu FFI.
- Determinism check xuyen ngon ngu bang diff file.
- Khong them toolchain build phuc tap vao moi truong agent (cargo build rieng, binary drop-in).
- Tra gia: dump 21ms + spawn process ~25ms — chap nhan duoc, amortize bang dump 1 lan / 9 configs.

## So lieu hieu chinh (2026-09-13, seed 42, 756 ngay x 4 symbols)
| lookback | python | rust | speedup | maxdiff equity |
|---|---|---|---|---|
| 5 | 165ms | 33ms | 5.1x | 2.3e-10 |
| 10 | 154ms | 28ms | 5.4x | 2.3e-10 |
| 20 | 151ms | 26ms | 5.9x | 2.3e-10 |

maxdiff 2.3e-10 tren equity ~1e6 (tuong doi ~2e-16) — lech last-ulp tu thuat toan std cua pandas.
Conformance test khoa o rtol=1e-9.

## Quy tac promote (chua dat — Rust hien la dev/bench only)
1. Conformance xanh tren moi seed CI (hien chi seed 42).
2. Gate end-to-end dung Rust vuot trigger: panel loop Python > 30s (hien ~0.5s).
3. Reference mai mai la Python — Rust khong bao gio thay gate Python, chi lam backend tang toc.
