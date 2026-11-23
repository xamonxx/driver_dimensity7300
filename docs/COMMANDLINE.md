# 🎮 GTA V Command Line: Infinix Note 50X (Mali-G615 MC2)

Panduan argumen **Command line** di launcher GTA V. Profil disusun untuk GPU 2-core, LCD 720p, RAM 8 GB,
dan driver `xamonxx mali7300` (frame pacer 30/60).

> [!NOTE]
> **Format launcher:** satu argumen per baris (atau dipisah spasi). `#` hanya untuk mengomentari **satu baris penuh**,
> tidak bisa di ujung baris. Perubahan berlaku saat game dijalankan berikutnya.
>
> **Sumber:** daftar resmi Rockstar *Full list of command line parameters for GTA V on PC*
> (diverifikasi lewat mirror Citadel Servers, 2026-11-23). Nilai rekomendasi = **ESTIMATED** sampai ada benchmark di HP.

---

## ⚡ Profil siap salin

### 🥇 Profil A: Stabil 30 (disarankan untuk GTA V)
Pasangkan dengan driver **stable30** dan Target FPS **30** di launcher.
```
# xamonxx mali7300 - Profil A: stabil 30 fps
-shaderQuality 0
-shadowQuality 1
-reflectionQuality 0
-waterQuality 0
-SSAO 0
-postFX 0
-tessellation 0
-grassQuality 0
-particleQuality 0
-textureQuality 0
-anisotropicQualityLevel 2
-fxaa 1
-noInGameDOF
-lodScale 0.4
-cityDensity 0.35
-pedLodBias 0.1
-vehicleLodBias 0.2
```

### 🥈 Profil B: Ultra hemat 30 (HP panas / adegan ramai / baterai rendah)
```
# xamonxx mali7300 - Profil B: ultra hemat 30 fps
-shaderQuality 0
-shadowQuality 0
-reflectionQuality 0
-waterQuality 0
-SSAO 0
-postFX 0
-tessellation 0
-grassQuality 0
-particleQuality 0
-textureQuality 0
-anisotropicQualityLevel 0
-fxaa 0
-noInGameDOF
-lodScale 0.25
-cityDensity 0.2
-pedLodBias 0.0
-vehicleLodBias 0.0
```

### 🥉 Profil C: Coba 60 (hanya bila Profil A sudah ≥45 fps tanpa cap)
Pasangkan dengan driver **stable60** dan resolusi lebih rendah (lihat bagian resolusi).
```
# xamonxx mali7300 - Profil C: coba 60 fps
-shaderQuality 0
-shadowQuality 0
-reflectionQuality 0
-waterQuality 0
-SSAO 0
-postFX 0
-tessellation 0
-grassQuality 0
-particleQuality 0
-textureQuality 0
-anisotropicQualityLevel 0
-fxaa 0
-noInGameDOF
-lodScale 0.2
-cityDensity 0.15
-pedLodBias 0.0
-vehicleLodBias 0.0
```

---

## 📐 Resolusi render

Atur resolusi lewat menu **RESOLUTION** di launcher. Jika launcher tidak punya menu itu, pakai `-width` / `-height`
(jangan memakai keduanya bersamaan). Layar HP 1600×720 (20:9).

| Target | Resolusi | Piksel vs 1600×720 | Catatan |
|---|---|---:|---|
| Tajam | `-width 1280` `-height 576` | 64% | Profil A bila GPU masih longgar |
| **Seimbang** | `-width 1066` `-height 480` | 44% | **Titik awal yang disarankan** |
| Ringan | `-width 960` `-height 432` | 36% | Profil B |
| Sangat ringan | `-width 854` `-height 384` | 28% | Profil C (60 fps) |

---

## 📋 Daftar lengkap parameter grafis dan performa

Kolom **Rekomendasi** berlaku untuk Mali-G615 MC2. **Beban** = dampak ke GPU/CPU bila nilainya dinaikkan.

| Parameter | Nilai resmi | Fungsi | Beban | Rekomendasi |
|---|---|---|:-:|---|
| `-shaderQuality` | 0–2 | Kualitas shader (pencahayaan dan efek) | 🔴 Sangat tinggi | **0** |
| `-shadowQuality` | 0–3 | Kualitas bayangan | 🔴 Tinggi | 0–1 |
| `-reflectionQuality` | 0–3 | Kualitas pantulan (kaca, air, mobil) | 🔴 Tinggi | **0** |
| `-SSAO` | 0–2 | Ambient occlusion | 🔴 Tinggi | **0** |
| `-postFX` | 0–3 | Post-processing (bloom, motion blur) | 🟠 Sedang–tinggi | **0** |
| `-grassQuality` | 0–5 | Kerapatan dan kualitas rumput | 🟠 Sedang–tinggi | **0** |
| `-tessellation` | 0–3 | Teselasi geometri | 🟠 Sedang | **0** |
| `-waterQuality` | 0–1 | Kualitas air | 🟠 Sedang | **0** |
| `-particleQuality` | 0–2 | Partikel (asap, ledakan) | 🟠 Sedang | **0** |
| `-textureQuality` | 0–2 | Resolusi tekstur (RAM/VRAM) | 🟡 Memori | **0** (RAM tersedia ±2,2 GiB) |
| `-anisotropicQualityLevel` | 0–16 | Filter tekstur miring | 🟡 Bandwidth | 0–2 |
| `-fxaa` | 0–3 | Anti-aliasing FXAA (murah) | 🟡 Ringan | 0–1 |
| `-lodScale` | 0.0–1.0 | Jarak detail objek | 🟠 CPU+GPU | 0.2–0.4 |
| `-cityDensity` | 0.0–1.0 | Kepadatan kota (NPC, mobil) | 🔴 **CPU** | 0.15–0.35 |
| `-pedLodBias` | 0.0–1.0 | Jarak detail pejalan kaki | 🟡 CPU | 0.0–0.1 |
| `-vehicleLodBias` | 0.0–1.0 | Jarak detail kendaraan | 🟡 CPU | 0.0–0.2 |
| `-noInGameDOF` | flag | Matikan efek depth of field | 🟢 Hemat | **Pakai** |
| `-width` / `-height` | angka | Resolusi render | 🔴 Sangat tinggi | Lihat tabel resolusi |
| `-fullscreen` / `-windowed` / `-borderless` | flag | Mode jendela | – | Biarkan launcher yang mengatur |

### 🧰 Parameter utilitas yang berguna
| Parameter | Fungsi | Kapan dipakai |
|---|---|---|
| `-benchmark` | Menjalankan benchmark bawaan GTA V | Uji performa (sementara) |
| `-benchmarkIterations` | Jumlah putaran benchmark | Bersama `-benchmark` |
| `-benchmarkFrameTimes` | Simpan frame time per frame | Analisis stutter |
| `-benchmarknoaudio` | Benchmark tanpa audio | Hasil grafis lebih murni |
| `-useMinimumSettings` | Reset semua setting ke minimum | Sekali saja bila setting kacau |
| `-safemode` | Jalankan dengan setting minimum tanpa menyimpan | Bila game crash saat start |
| `-ignoreprofile` | Abaikan setting profil tersimpan | Bila setting lama terus kembali |

### ⛔ Jangan dipakai di HP ini
| Parameter | Alasan |
|---|---|
| `-frameLimit` | Membatasi berdasarkan kelipatan vsync, bisa bentrok dengan frame pacer driver |
| `-multiSample` (>1) | MSAA sangat berat untuk GPU 2-core |
| `-txaa` | Khusus NVIDIA |
| `-hdr` | Pipeline 16-bit penuh: bandwidth dan memori naik |
| `-HDStreamingInFlight` | Streaming HD saat terbang: RAM dan I/O naik, memicu stutter |
| `-shadowLongShadows` | Bayangan panjang senja/fajar, berat |
| `-reflectionBlur` | Blur pantulan, berat |
| `-SSA` | Efek tambahan, berat |
| `-fogVolumes` / `-particleShadows` | Ini flag untuk *menyalakan* efek. Cukup jangan ditulis (`… 0` belum terverifikasi mematikan) |
| `-shadowSoftness` | Pemetaan angkanya tidak didokumentasikan |
| `-DX10` / `-DX10_1` | Hanya untuk troubleshooting crash. Default DX11 lewat DXVK lebih kompatibel |
| `-GPUCount`, `-adapter`, `-disableHyperthreading` | Tidak relevan di ARM/Mali |

---

## 🔁 Cara tuning yang benar
1. Mulai dari **Profil A**, resolusi **1066×480**, driver **stable30**, Target FPS 30.
2. Jalankan **Benchmark Runs**. Target: **≥99% frame ≥30 fps** dan 99% frame time < 34 ms.
3. Masih drop? Turunkan `-cityDensity` dulu (beban CPU), lalu resolusi (beban GPU), lalu pindah ke **Profil B**.
4. Sangat longgar (≥45 fps tanpa cap)? Naikkan resolusi ke 1280×576, atau coba **Profil C + stable60**.
5. Ubah **satu hal per benchmark**, lalu kirim screenshot supaya dicatat di `memory/test-results.md`.
