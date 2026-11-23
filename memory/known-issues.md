---
name: known-issues
description: Masalah terbuka dan solusinya
updated: 2026-11-23
type: issue
---

## Terbuka
- **V0.1 force close di launcher GTA V** (semua layout). Momen crash UNKNOWN. Langkah: V0.2 stable30, lalu safe30,
  lalu freedreno. Uji PanProbe (zenithblue) untuk memisahkan masalah driver dari loader launcher.
- **Launcher mungkin membatasi driver custom di GPU non-Adreno**: bagian PERFORMANCE terlihat kosong di screenshot Infinix.
- **MC2 belum pernah diuji**: basis hanya diuji di G615 MC6. Risiko gagal load atau GPU fault. Fallback: driver bawaan, kandidat #2.
- **Loader launcher GTA V belum diketahui**: apakah butuh nama `libvulkan_freedreno.so`. Karena itu dua layout zip disediakan.
- **GPU 2-core**: GTA V berat. 60 fps stabil kemungkinan tidak tercapai (ESTIMATED). Fokus ke stable30.
- **RAM tersedia ±2,2 GiB** saat audit: tutup aplikasi latar.
