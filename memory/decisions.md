---
name: decisions
description: Log keputusan teknis (terbaru di atas)
updated: 2026-11-23
type: decision
---

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
