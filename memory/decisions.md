---
name: decisions
description: Log keputusan teknis (terbaru di atas)
updated: 2026-11-23
type: decision
---

### 2026-11-24: V0.3, cari dma-buf yang benar di handle ANB (patch xamonxx/0004)
- **Konteks:** log launcher menunjukkan swapchain gagal di `vk_android_import_anb_memory` (`data[0]` bukan dma-buf).
- **Keputusan:** iterasi `handle->data[]`, lalu fstat, lseek size>0, GetMemoryFdProperties OK. Pass 0 mensyaratkan size ≥ mem_reqs.size,
  pass 1 tanpa syarat ukuran (AFBC gralloc bisa beda ukuran). `data[0]` tetap kandidat pertama.
- **Sumber pola:** `panvk_android_find_dma_buf_fd()` dan probe AHB di tree basis ("Arm gralloc4 handles do not always put the dma-buf at data[0]").
- **Risiko lanjutan:** import buffer AFBC dari gralloc MediaTek belum terbukti. Uji di perangkat.

### 2026-11-24: Diagnostik on-device (patch xamonxx/0003, varian debug30)
- **Konteks:** owner: force close terjadi "saat membuka game". Tidak ada akses logcat/ADB.
- **Keputusan:** dengan `-DXAMONXX_DIAG`, constructor driver menulis header ke
  `/sdcard/Android/media/<pkg>/xamonxx_mali7300_crash.log` dan memasang handler SIGSEGV/SIGBUS/SIGILL/SIGFPE/SIGABRT/SIGTRAP
  (write() saja; PC/LR/SP/FP + offset driver + fp-walk; handler lama dipulihkan lalu fault berulang).
  Log Mesa lewat default `MESA_LOG_FILE`/`MESA_LOG_LEVEL=info` di tabel 0002. `.so` unstripped diunggah sebagai artifact
  CI `symbols-debug30`, lalu dibaca `tools/symbolize_crash.py`.

### 2026-11-24: V0.2, profil perangkat MC2 (patch xamonxx/0002)
- **Konteks:** V0.1 force close. Riset issue zenithblue: #20 (HP **sama**, X6857/MT6878, SIGSEGV 0x518 di
  vkCreateSemaphore pada build RC2/RC3 LukeValen. Jalur sync kbase v26.3.1 sudah ditulis ulang, CPU sync tanpa objek kernel)
  dan #54 (G615 **MC2** kehilangan GPU di v26.3.1; fix `PANVK_KBASE_TILER_IR=0 PANVK_KBASE_HEAP_CHUNKS=10,400`).
- **Keputusan:** tabel default di `os_get_option()` (src/util/os_misc.c), aktif dengan `-DXAMONXX_PROFILE`.
  Profil 1: IR off + heap 10,400. Profil 2 (safe30): + `PANVK_ANDROID_PRESENT_THREAD=0`, `PANVK_KBASE_GPU_SEMAPHORE_WAITS=0`.
  Env/properti user tetap menang.
- **Ditolak:** `setenv()` di constructor (tidak thread-safe, bisa memicu crash baru).

### 2026-11-23: Frame pacer di driver (patch xamonxx/0001)
- **Konteks:** owner minta 30–60 fps sangat stabil. kbase tidak punya ioctl userspace untuk floor clock GPU
  (beda dengan KGSL di Adreno), dan queue group CSF sudah prioritas HIGH di basis.
- **Keputusan:** pacer presisi di `panvk_QueuePresentKHR` dan `panvk_QueueSignalReleaseImageANDROID`
  (deadline absolut CLOCK_MONOTONIC, clock_nanosleep TIMER_ABSTIME, re-sync bila telat >1 frame).
- **Varian:** stable30, stable60. Override `XAMONXX_FPS_CAP`.
- **Ditolak:** hint MediaTek GED/FPSGO (`/dev/ged`) karena antarmuka tak terdokumentasi, SELinux tidak pasti, dan tidak bisa diuji.

### 2026-11-23: Basis = zenithblue v26.3.1, resep rilis persis
- **Alasan:** satu-satunya kandidat dengan bukti uji G615 (MC6) dan profil `g615-v11-csf`. Lisensinya jelas.
- **Tuning CPU:** `-march=armv8.2-a+crypto+dotprod+fp16+rcpc -mtune=cortex-a78`. LTO tidak dipakai di V0.1 (risiko pada patch stack besar).
- **Fallback CI:** TUNE=0 (flag upstream) bila build tuned gagal.
