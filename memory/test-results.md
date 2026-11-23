---
name: test-results
description: Hasil uji di Infinix Note 50X (terbaru di atas)
updated: 2026-11-23
type: test
---

### 2026-11-24 00:39: V0.2 Stable30 di launcher GTA V: FORCE CLOSE, **root cause ditemukan**
- Sumber: `log/GameCrash-20261124-003913.txt` (crash report launcher `com.thegwchr.fuzzy` 1.61.1).
- Driver **ter-load** lewat hook AdrenoTools `vulkan.mali.so` ("182 of 182 entry points"). kbase CSF uAPI 1.21,
  `gpu_id 0xb8a31030 ... Mali-G615`. Profil 0002 **aktif**: "tiler heaps 10 initial / 400 max chunks".
- Gagal: `E MESA: GetMemoryFdPropertiesKHR failed`, lalu `vkCreateSwapchainKHR ... VkResult -1000072003`
  (INVALID_EXTERNAL_HANDLE), lalu game `diagTerminate()` SIGTRAP. Bukan crash di dalam driver.
- Gralloc: aimapper mediatek v5, buffer 1088×480 AB24, modifier AFBC `0x0800000000000072`, stride 4352, alloc 2121728.
  Juga error non-fatal "Usage not permitted ... 0x800" untuk format 0x38/0x3b.
- **Penyebab:** `vk_android_import_anb_memory()` memakai `handle->data[0]` sebagai dma-buf. Di kbase,
  GetMemoryFdProperties menolak fd yang tidak bisa `lseek(SEEK_END)`. Diperbaiki di patch 0004 (V0.3).

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
