# 0001 — Judgment boundaries: dung truoc lua chon mo

- Ngay: 2026-09-13. Trang thai: accepted.
- Cam hung: harness-by-victoria (repository authority + stop-before-mutation).

## Context
Agent co xu huong tu che product policy khi yeu cau bo ngo lua chon quan trong
(vi du: "them rate limiting" ma khong quota; "chon universe" ma khong dinh nghia survivorship).

## Quyet dinh
Truoc moi mutation, agent phai neu ro authority (doc nao cho phep).
Neu lua chon con mo o muc material (doi duoc hanh vi quan sat ben ngoai):
DUNG truoc edit, trinh lua chon cu the + he qua, doi human chon.
Configurable defaults KHONG phai authority.

## He qua
- PR nao che policy khong co authority → review reject, khong can tranh luan ky thuat.
- Skill `encode-invariant` la noi duy nhat bien rule thanh guard (xem docs/decisions/0002).
