<div align="center">

# ⚡ xamonxx mali7300 · V0.3

**Driver Vulkan Mesa PanVK untuk Mali-G615 MC2 · Infinix Note 50X 5G (Dimensity 7300)**

![GPU](https://img.shields.io/badge/GPU-Mali--G615_MC2-00a3e0?style=flat-square)
![Mesa](https://img.shields.io/badge/Mesa-26.3_PanVK_p0175-6e4c9a?style=flat-square)
![Pacer](https://img.shields.io/badge/Frame_Pacer-30_%2F_60_fps-success?style=flat-square)
![Fix](https://img.shields.io/badge/Fix-MC2_GPU_loss-blue?style=flat-square)
![Status](https://img.shields.io/badge/Status-Eksperimental-orange?style=flat-square)

</div>

---

## 🆕 Apa yang baru di V0.3
- 🩹 **FIX force close saat game dibuka** (patch `xamonxx/0004`). Dari log crash launcher GTA V:
  `GetMemoryFdPropertiesKHR failed` lalu `vkCreateSwapchainKHR ... VkResult -1000072003` (INVALID_EXTERNAL_HANDLE).
  Driver mengambil `data[0]` dari handle gralloc sebagai dma-buf layar, padahal di gralloc Mali/MediaTek dma-buf
  **tidak selalu** di posisi itu. Sekarang driver mencari dma-buf yang benar di semua fd handle (aturan yang sama dengan
  jalur AHB yang sudah ada di driver basis).

## Dari V0.2 (tetap ada)
- 🩹 **Profil perangkat MC2 tertanam** (patch `xamonxx/0002`): *incremental rendering* kbase **dimatikan** dan tiler heap
  **10 awal / 400 maks chunk**. Ini perbaikan yang sudah terverifikasi untuk G615 **MC2** yang kehilangan GPU
  di v26.3.1 ([zenithblue#54](https://github.com/zenithblue-oss/panvk-kbase-android/issues/54)).
  Sebelumnya hanya bisa lewat env var, yang tidak tersedia di launcher GTA V.
- 🔬 **Varian baru `debug30`** (patch `xamonxx/0003`): sama dengan stable30, tapi **menulis log sendiri** ke
  `/sdcard/Android/media/<aplikasi>/`: `xamonxx_mali7300_crash.log` (lokasi crash di dalam driver) dan
  `xamonxx_mali7300_mesa.log` (log Mesa: probe kbase, gpu_id, pembuatan device).
- 🛟 **Varian baru `safe30`**: profil MC2 plus jalur present dan sync paling sederhana (tanpa present thread Android,
  semaphore ditunggu di CPU). Untuk menelusuri force close.
- 🎯 Frame pacer presisi dari V0.1 tetap ada (30/60 fps).

## 🧭 Pilih file yang mana?

| Situasi | Download ini |
|---|---|
| 🎮 **GTA V, coba pertama** | **`xamonxx_mali7300V0.3-stable30.zip`** ⭐ |
| 💥 `stable30` **force close** | `xamonxx_mali7300V0.3-safe30.zip` |
| 💥 Masih force close | versi `-freedreno.zip` dari varian yang sama |
| 🔬 **Semua force close** | **`xamonxx_mali7300V0.3-debug30.zip`**, lalu kirim file log-nya (lihat bawah) |
| 🏃 Game ringan, mau lebih mulus | `xamonxx_mali7300V0.3-stable60.zip` |
| 🎯 GameHub / BannerHub | `…-freedreno.zip` |

> [!IMPORTANT]
> **V0.1 force close?** Urutan coba: `stable30` → `safe30` → `safe30-freedreno`.
> Catat **kapan** force close terjadi (saat import zip, saat memilih driver, atau saat game mulai) dan laporkan di Issues.

## 🔬 Cara mengambil log (varian debug30)
1. Import dan pilih **xamonxx mali7300 V0.3 Debug30**, lalu buka game sampai force close.
2. Buka file manager, masuk ke **Internal storage → Android → media →** folder bernama paket launcher GTA V
   (bila tidak ada, cek **Download**).
3. Kirim dua file: `xamonxx_mali7300_crash.log` dan `xamonxx_mali7300_mesa.log`.
   - Kalau `crash.log` hanya berisi header tanpa blok `=== CRASH ===`, crash terjadi di luar driver (launcher atau loader).
   - Kalau ada blok `=== CRASH ===`, offset-nya diterjemahkan ke nama fungsi dengan `tools/symbolize_crash.py`.

## 🚀 Cara pasang (launcher GTA V)
1. Download zip, **jangan di-extract**.
2. Hapus driver lama (V0.1/V0.2): **Remove a driver**.
3. **Settings → Import driver (.zip)** lalu pilih zip V0.3.
4. Pilih **xamonxx mali7300 V0.3 Stable30** (atau Safe30) di Vulkan Driver.
5. Command line: **Profil A** ([`docs/COMMANDLINE.md`](https://github.com/xamonxx/driver_dimensity7300/blob/master/docs/COMMANDLINE.md)), resolusi 1066×480, Target FPS 30.
6. Jalankan **Benchmark Runs**, lalu kirim screenshot.

## 📁 Daftar file
| File | Pacer | Profil | Library |
|---|:-:|---|---|
| `xamonxx_mali7300V0.3-stable30.zip` | 30 | MC2 | `libvulkan_panfrost.so` |
| `xamonxx_mali7300V0.3-stable30-freedreno.zip` | 30 | MC2 | `libvulkan_freedreno.so` |
| `xamonxx_mali7300V0.3-safe30.zip` | 30 | MC2 safe | `libvulkan_panfrost.so` |
| `xamonxx_mali7300V0.3-safe30-freedreno.zip` | 30 | MC2 safe | `libvulkan_freedreno.so` |
| `xamonxx_mali7300V0.3-debug30.zip` | 30 | MC2 + log | `libvulkan_panfrost.so` |
| `xamonxx_mali7300V0.3-debug30-freedreno.zip` | 30 | MC2 + log | `libvulkan_freedreno.so` |
| `xamonxx_mali7300V0.3-stable60.zip` | 60 | MC2 | `libvulkan_panfrost.so` |
| `xamonxx_mali7300V0.3-stable60-freedreno.zip` | 60 | MC2 | `libvulkan_freedreno.so` |

## ⚠️ Catatan
- **Eksperimental** dan **belum diuji** di G615 MC2. V0.1 dilaporkan force close di launcher GTA V.
- Semua opsi profil bisa ditimpa lewat env var (Winlator): `PANVK_KBASE_TILER_IR`, `PANVK_KBASE_HEAP_CHUNKS`,
  `PANVK_ANDROID_PRESENT_THREAD`, `PANVK_KBASE_GPU_SEMAPHORE_WAITS`, `XAMONXX_FPS_CAP`.
- Driver tidak menambah core atau clock GPU. Fokusnya kestabilan frame time dan suhu.

<sub>Lisensi: Mesa MIT · header kbase GPL-2.0 WITH Linux-syscall-note · script MIT. Detail di NOTICE.md.</sub>
