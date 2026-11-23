# 📦 INSTALL: Infinix Note 50X (Mali-G615 MC2)

## Launcher GTA V ("Import driver (.zip)")
1. Kirim zip ke HP. **Jangan di-extract.**
2. Buka **Settings → Import driver (.zip)** dan pilih `xamonxx_mali7300V0.1-stable30.zip`.
3. Di **Vulkan Driver** pilih `xamonxx mali7300 V0.1 Stable30`.
4. Jalankan **Benchmark Runs** dan simpan screenshot hasilnya.
5. Bila gagal dimuat (crash atau layar hitam), import `…-stable30-freedreno.zip`.
   Bila masih gagal, pakai **Remove a driver** untuk kembali ke driver bawaan Mali.

## Winlator / GameHub
- Winlator: Contents/Drivers lalu install zip (layout `libvulkan_panfrost.so`).
- GameHub/BannerHub: pakai `…-freedreno.zip` (loader-nya mewajibkan nama `libvulkan_freedreno.so`).
- Ubah target pacer lewat env var container: `XAMONXX_FPS_CAP=30` / `45` / `60`, atau `0` untuk mematikan.

## Setting HP untuk FPS stabil dan adem
- Refresh layar **60 Hz** untuk target 30/60 (120 Hz tidak memberi manfaat bila game ≤60 fps, malah boros).
- Aktifkan **Game Mode** XOS dan **bypass charging** bila tersedia.
- Tutup aplikasi latar (RAM yang tersedia saat audit hanya ±2,2 GiB).
- Lepas casing saat sesi panjang.
