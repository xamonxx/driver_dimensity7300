---
name: known-issues
description: Masalah terbuka dan solusinya
updated: 2026-11-23
type: issue
---

## Terbuka
- **MC2 belum pernah diuji**: basis hanya diuji di G615 MC6. Risiko gagal load atau GPU fault. Fallback: driver bawaan, kandidat #2.
- **Loader launcher GTA V belum diketahui**: apakah butuh nama `libvulkan_freedreno.so`. Karena itu dua layout zip disediakan.
- **GPU 2-core**: GTA V berat. 60 fps stabil kemungkinan tidak tercapai (ESTIMATED). Fokus ke stable30.
- **RAM tersedia ±2,2 GiB** saat audit: tutup aplikasi latar.
