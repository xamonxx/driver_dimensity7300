---
name: test-results
description: Hasil uji di Infinix Note 50X (terbaru di atas)
updated: 2026-11-23
type: test
---

### 2026-11-23/24: V0.1 di launcher GTA V: **FORCE CLOSE** (semua driver)
- Laporan owner: "semua drivers ketika di pasang semuanya force close" (V0.1 stable30/stable60 dan layout freedreno).
  Momen tepat crash (saat import, saat memilih driver, atau saat game start) **UNKNOWN**. Sudah diminta ke owner.
- Screenshot settings: RESOLUTION 1066×480, V-SYNC ON, Target FPS 30, Graphics DEFAULT. Bagian PERFORMANCE
  (yang di iQOO berisi Vulkan Driver/Import) terlihat kosong di screenshot.
- Benchmark 23:49 (driver yang aktif **kemungkinan driver bawaan Mali**, karena driver xamonxx crash): avg **27.6 fps**.

| Pass | Avg | Min | Max | ≥30fps | 99% frame < |
|---|---|---|---|---|---|
| 1 | 28.6 | 6.3 | 63.6 | 35% | 55 ms |
| 2 | 30.1 | 22.3 | 41.9 | 41% | 39 ms |
| 3 | 22.7 | 3.5 | 51.3 | 22% | 144 ms |
| 4 | 29.4 | 14.3 | 94.0 | 38% | 66 ms |

**Analisis:** baseline buruk (frame time sangat tidak rata). Target V0.2: driver jalan dulu, baru kestabilan.
