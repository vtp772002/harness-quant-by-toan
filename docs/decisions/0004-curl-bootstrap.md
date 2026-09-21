# 0004 — Curl bootstrap cho quant control-plane

- Ngay: 2026-09-21. Trang thai: accepted.
- Context: control-plane da cai local bang Cargo nhung chua co install flow
  giong cac repository harness pho bien. Agent/user can need bootstrap tu repo
  dich ma khong clone ca source tree.

## Quyet dinh

1. Phat hanh `scripts/install-quant-harness.sh` qua GitHub raw URL.
2. Installer tai payload list co dinh, merge mac dinh, `--override` la lua chon
   destructive co chu y, va `--dry-run` de xem truoc.
3. Installer build Rust control-plane tai may dich va dat binary vao
   `scripts/bin/`; binary platform-specific khong commit vao repo.
4. Non-interactive `curl | bash` bat buoc `--yes`; source ref va raw base URL co
   the override de test/air-gapped mirror.

## He qua

- Bootstrap nhanh tu mot lenh, nhung van giu source/control-plane inspectable
  trong target repo.
- Curl qua HTTPS va `--ref` pin source boundary; checksum release binary la
  workstream tiep theo khi repo bat dau publish release artifacts.
- Installer khong tu dong overwrite AGENTS/docs hoac policy product.
