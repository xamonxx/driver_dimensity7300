---
name: decisions
description: Log keputusan teknis (terbaru di atas)
updated: 2026-11-23
type: decision
---

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
