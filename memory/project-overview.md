---
name: project-overview
description: Tujuan, status terkini, langkah berikutnya
updated: 2026-11-23
type: project
---

## Tujuan
Driver Vulkan **xamonxx mali7300** (Mesa PanVK on mali_kbase) untuk Infinix Note 50X 5G (Mali-G615 MC2),
dipakai di launcher GTA V. Target owner: **FPS 30–60 yang sangat stabil**, suhu terkendali.

## Status (2026-11-23)
- Top 3 kandidat diunduh dan diaudit (semua PASS), lihat `docs/CANDIDATES.md`. Basis: zenithblue v26.3.1.
- Patch seri rilis (p0175) dan `xamonxx/0001_frame_pacer.py` diuji apply secara lokal: bersih.
- **V0.1 RILIS** (CI 45212424366, setelah fix header xcb): release `v0.1` berisi 4 zip + SHA256SUMS.txt. Audit lokal PASS.
  Catatan rilis memakai `docs/RELEASE_NOTES.md`. Status driver: **NOT TESTED** di HP.

- **V0.1 FORCE CLOSE** di launcher GTA V "saat membuka game" (laporan owner 2026-11-24).
- **V0.2 RILIS** (CI 45226695057): stable30 / safe30 / debug30 / stable60 (+freedreno). Profil MC2 (IR off, heap 10,400),
  debug30 menulis `Android/media/<pkg>/xamonxx_mali7300_{crash,mesa}.log`.
- **V0.2 Stable30 diuji: force close.** Root cause dari log launcher: swapchain import `data[0]` bukan dma-buf. **V0.3 RILIS** (CI 45231212776) = fix (patch 0004), audit PASS. NOT TESTED di HP.

## Next steps
1. Owner uji V0.2: stable30, lalu safe30, lalu debug30, dan kirim log crash/mesa bila force close.
   Simbolisasi: `gh run download 45226695057 -n symbols-debug30`, lalu `python -I tools/symbolize_crash.py <so> <crash.log>`.
2. V0.2 berdasarkan hasil uji (mis. cap 40/45, atau fallback kandidat #2 JimVulkan bila #1 gagal load).

## Lingkungan
- PC owner Windows 11 tanpa virtualisasi, jadi build lewat GitHub Actions. gh login `xamonxx`.
- Menjalankan script hasil download di PC owner diblokir pengaman. Patch basis diterapkan lokal hanya sebagai data (`git apply`/`git am`).
- Source referensi lokal: `C:\Users\Administrator\DRIVER_dimensity7300_src\` (zb sparse + Mesa p0175, tidak di-commit).
