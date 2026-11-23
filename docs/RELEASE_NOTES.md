<div align="center">

# ⚡ xamonxx mali7300 · V0.1

**Driver Vulkan Mesa PanVK untuk Mali-G615 MC2 · Infinix Note 50X 5G (Dimensity 7300)**

![GPU](https://img.shields.io/badge/GPU-Mali--G615_MC2-00a3e0?style=flat-square)
![Mesa](https://img.shields.io/badge/Mesa-26.3_PanVK_p0175-6e4c9a?style=flat-square)
![Pacer](https://img.shields.io/badge/Frame_Pacer-30_%2F_60_fps-success?style=flat-square)
![Root](https://img.shields.io/badge/Root-Tidak_perlu-success?style=flat-square)
![Status](https://img.shields.io/badge/Status-Eksperimental-orange?style=flat-square)

</div>

---

## 🧭 Pilih file yang mana?

| Kebutuhan kamu | Download ini | Keterangan |
|---|---|---|
| 🎮 **Main GTA V** di launcher GTA V | **`xamonxx_mali7300V0.1-stable30.zip`** | ⭐ **Mulai dari sini.** Paling stabil, paling adem |
| 🏃 Game ringan–menengah, ingin lebih mulus | `xamonxx_mali7300V0.1-stable60.zip` | Butuh setting grafis rendah |
| ❌ File di atas **gagal dimuat** / crash saat start | `…-stable30-freedreno.zip` | Driver sama, nama file `libvulkan_freedreno.so` |
| 🎯 Pakai **GameHub / BannerHub** | `…-freedreno.zip` (stable30 atau stable60) | Loader GameHub mewajibkan nama ini |
| 🍷 Pakai **Winlator** | `…-stable30.zip` / `…-stable60.zip` | Bisa diubah lewat env var `XAMONXX_FPS_CAP` |

> [!TIP]
> **Ragu? Ambil `stable30`.** Untuk GPU 2-core di GTA V, 30 fps yang benar-benar rata terasa jauh lebih enak
> daripada 40–60 fps yang naik-turun.

## 🚀 Cara pasang (launcher GTA V)
1. Download zip, **jangan di-extract**.
2. **Settings → Import driver (.zip)** lalu pilih zip-nya.
3. **Vulkan Driver** → pilih `xamonxx mali7300 V0.1 Stable30`.
4. **Command line** → salin **Profil A** dari [`docs/COMMANDLINE.md`](https://github.com/xamonxx/driver_dimensity7300/blob/master/docs/COMMANDLINE.md).
5. Set **Target FPS 30**, lalu jalankan **Benchmark Runs**.
6. Gagal? Coba versi `-freedreno`, atau **Remove a driver** untuk kembali ke driver bawaan.

## ✨ Isi rilis ini
- 🎯 **Frame pacer presisi** (patch `xamonxx/0001`): jadwal frame absolut `CLOCK_MONOTONIC` dengan `clock_nanosleep`,
  tanpa busy-wait. Aktif di jalur present Android dan X11/Winlator. Frame time rata, GPU sempat istirahat, panas turun.
- 🧠 **PanVK on mali_kbase / CSF**: berbicara langsung ke `/dev/mali0`. Queue group prioritas HIGH,
  semaphore ditunggu di GPU, shadow tekstur BCn AFRC (hemat bandwidth). Tanpa root.
- 🛠️ **Dikompilasi khusus CPU**: `-march=armv8.2-a+crypto+dotprod+fp16+rcpc -mtune=cortex-a78` (fallback otomatis ke flag upstream bila gagal).
- 📦 Basis: zenithblue panvk-kbase **v26.3.1**, seri patch identik (p0175), Mesa `5a07217f`.

## 📁 Daftar file
| File | Pacer | Nama library |
|---|:-:|---|
| `xamonxx_mali7300V0.1-stable30.zip` | 30 fps | `libvulkan_panfrost.so` |
| `xamonxx_mali7300V0.1-stable30-freedreno.zip` | 30 fps | `libvulkan_freedreno.so` |
| `xamonxx_mali7300V0.1-stable60.zip` | 60 fps | `libvulkan_panfrost.so` |
| `xamonxx_mali7300V0.1-stable60-freedreno.zip` | 60 fps | `libvulkan_freedreno.so` |
| `SHA256SUMS.txt` | — | Checksum semua zip |

## ⚠️ Catatan penting
- **Eksperimental.** Basis diuji di Mali-G615 **MC6**. Varian **MC2** (Note 50X) **belum diuji**.
- Driver **tidak menambah** core atau clock GPU. Yang diperbaiki adalah **kestabilan** frame time dan suhu.
- Proteksi termal kernel tetap aktif. Tidak ada modifikasi sistem.

## 📣 Kirim hasil uji
Screenshot **Benchmark Runs** (driver bawaan vs `stable30`) sangat membantu untuk V0.2.

<sub>Lisensi: Mesa MIT · header kbase GPL-2.0 WITH Linux-syscall-note · script MIT. Detail di NOTICE.md.</sub>
