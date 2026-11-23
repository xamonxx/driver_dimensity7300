# 🛠️ BUILD: xamonxx mali7300

## Pin versi (V0.1)
| Komponen | Nilai |
|---|---|
| Lapisan build/patch | zenithblue-oss/panvk-kbase-android `3c82008657f3edd44cc5fbed4c2f80f8a29c90fc` (tag `panvk-kbase-v26.3.1`) |
| Mesa | `5a07217f034b3e50d8c7c7794f97a2df1742613b` (26.3.0-devel, dari `sources.lock` zenithblue) |
| Seri patch | `prepare-rc5-tree.sh`: common · android · kbase-common · app-loader · wsi · csf · csf-v11 ≤233 · jm-v9 · jm-v7, lalu jm-v7-wip 0006–0175 → **p0175** (sama dengan rilis resmi) |
| Profil | `g615-v11-csf` (Mali-G615, pan arch v11, CSF) |
| Toolchain | Android NDK r29 (clang), API 29; host tools `mesa_clc`/`vtn_bindgen2`/`panfrost_compile` dengan LLVM 18 |

Uji lokal 2026-11-23: 228 patch dasar dan 170 patch WIP diterapkan bersih pada Mesa 5a07217f (patch level p0175),
lalu patch `xamonxx/0001` diterapkan bersih (+82 baris, idempoten).

## Alur `build_mali7300.sh`
1. **fetch_sources**: NDK r29, sparse checkout zenithblue (commit di-pin), Mesa shallow (commit di-pin).
2. **prepare_tree**: `prepare-rc5-tree.sh` (strict: berhenti bila ada offset/fuzz), cek `p0175`, lalu `patches/xamonxx/*.py`.
3. **inject_flags**: menambah `[built-in options]` ke cross-file template:
   - `-DXAMONXX_FPS_CAP=<30|60|0>`
   - bila `TUNE=1`: `-march=armv8.2-a+crypto+dotprod+fp16+rcpc -mtune=cortex-a78`
     (fitur persis dari `/proc/cpuinfo` perangkat: aes pmull sha1 sha2 atomics fphp asimdhp asimdrdm lrcpc asimddp; aman di A55 dan A78).
   - Optimasi `-O3` sudah datang dari `buildtype=release`.
4. **build_driver**: `build-android.sh --profile g615-v11-csf --api 29` (libdrm statis NDK, header X11 untuk WSI yang di-dlopen), lalu strip.
   Cek binary mengandung `xamonxx mali7300: frame pacer`.
5. **package**: 2 layout per varian, lalu audit otomatis.

## Varian
| VARIANT | Pacer | Zip |
|---|---|---|
| `stable30` | 30 fps | `xamonxx_mali7300V0.1-stable30.zip`, `…-stable30-freedreno.zip` |
| `stable60` | 60 fps | `xamonxx_mali7300V0.1-stable60.zip`, `…-stable60-freedreno.zip` |
| `nocap` | mati | hanya untuk build lokal/debug |

Override saat runtime (Winlator env var / properti `debug.mesa.*`): `XAMONXX_FPS_CAP=0` (mati) atau `10..240`.

## Patch `xamonxx/0001_frame_pacer.py`
- Titik pasang: `panvk_QueuePresentKHR` (X11/Wayland/swapchain Android PanVK) dan `panvk_QueueSignalReleaseImageANDROID`
  (swapchain loader Android). Kedua jalur tidak saling memanggil, sehingga setiap frame di-pace tepat sekali.
- Algoritma: deadline absolut `CLOCK_MONOTONIC` dan `clock_nanosleep(TIMER_ABSTIME)` tanpa busy-wait.
  Frame yang telat ≤1 interval mempertahankan cadence. Frame yang telat lebih dari itu memicu re-sync (tanpa burst). Lock tidak dipegang saat tidur.
- Thread-safe: inisialisasi sekali dengan `simple_mtx`, state dibaca dengan acquire (`p_atomic_read`).

## Cara build
- **CI (disarankan):** push ke `master`, atau Actions → *Build xamonxx mali7300 driver* → Run workflow. Hasilnya di Release `v0.1`.
- **Lokal:** Linux x86_64 dengan dependensi seperti di workflow, lalu `VARIANT=stable30 bash build_mali7300.sh`.
  PC owner tidak bisa (virtualisasi BIOS mati), jadi pakai CI.
