---
name: build-history
description: Riwayat build (terbaru di atas)
updated: 2026-11-23
type: build
---

| Tanggal | Versi | Run CI | Basis | Varian | Hasil | SHA256 |
|---|---|---|---|---|---|---|
| 2026-11-24 | V0.3 | 45231212776 | zb 3c82008 + Mesa 5a07217f p0175 + xamonxx 0001-0004 | stable30, stable60, safe30, debug30 | **SUKSES**: release v0.3, 8 zip, audit PASS + expect string 0004 ("swapchain dma-buf = gralloc fd") ter-link | lihat SHA256SUMS.txt rilis v0.3 |
| 2026-11-24 | V0.2 | 45226695057 | zb 3c82008 + Mesa 5a07217f p0175 + xamonxx 0001-0003 | stable30, stable60, safe30, debug30 (TUNE=1) | **SUKSES**: release v0.2, 8 zip + SHA256SUMS, audit PASS (cek pacer + heap "10,400"); hanya debug30 berisi kode diagnostik. Artifact `symbols-debug30` (unstripped .so, 11349 fungsi, retensi 90 hari) terverifikasi dengan tools/symbolize_crash.py | lihat SHA256SUMS.txt rilis v0.2 |
| 2026-11-23 | V0.1 | 45212424366 | zb 3c82008 + Mesa 5a07217f p0175 | stable30, stable60 (TUNE=1 sukses, fallback tidak dipakai) | **SUKSES**: release v0.1, 4 zip, audit PASS (checksum, aarch64, HMI/vk_icd, Mali-G615, string pacer, NEEDED sistem saja). .so 34.6 MB. driverInfo `Mesa 26.3.0-devel (git-<sha>, p0175, 2026-11-23)`. Sha tree berbeda per job (commit git am diberi timestamp CI). | stable30 `42b1a2d1…`, stable30-freedreno `56d9bf5f…`, stable60 `aa426745…`, stable60-freedreno `8a43ce38…` (lengkap di SHA256SUMS.txt rilis) |
| 2026-11-23 | V0.1 | 45209976842 | zb 3c82008 + Mesa 5a07217f p0175 | stable30, stable60 | GAGAL: patch series + pacer + host tools OK; compile target gagal `xcb/shm.h` not found (header host X11 kurang di runner) → tambah paket libxcb-*-dev | — |
