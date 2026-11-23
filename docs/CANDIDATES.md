# 🧪 Audit kandidat driver: Mali-G615 MC2 (Infinix Note 50X)

Tanggal audit: **2026-11-23** · Tool: [`tools/audit_mali_driver.py`](../tools/audit_mali_driver.py)

Konteks: GPU **Mali-G615 MC2** berarti pan arch **v11** dengan frontend **CSF**. Android stok memakai kernel `mali_kbase`,
jadi hanya **PanVK yang punya backend kbase** yang bisa jalan tanpa root. Turnip tidak berlaku karena khusus Adreno.

## Ringkasan

| Rank | Driver | Rilis | Mesa | Ukuran `.so` | Bukti G615 | Audit |
|:-:|---|---|---|---|---|:-:|
| 🥇 | [zenithblue-oss/panvk-kbase-android](https://github.com/zenithblue-oss/panvk-kbase-android) | `panvk-kbase-v26.3.1` (31 Okt 2026) | 26.3.0-devel `795ca7ff3e` p0175 | 34.9 MB | **Diuji di G615 MC6** (Poco X6 Pro): PanProbe 41/41, D3D11 cube +36% vs build 116 | ✅ PASS |
| 🥈 | [JimVulkan/mali-panvk](https://github.com/JimVulkan/mali-panvk) | `v1.6.0` r10 (4 Nov 2026) | 27.0.0-devel `58f2c55854` | 18.8 MB | G615 diuji 1 tester | ✅ PASS (1 catatan) |
| 🥉 | [MineGraph-bilibili/panvk-Android](https://github.com/MineGraph-bilibili/panvk-Android) | `Mesa.26.3.0-panvk.8` (19 Nov 2026) | 26.3.0-devel | 28.2 MB | Diklaim (fokus G720) | ✅ PASS |

**Ditolak:** FristOneRR PanVK (README-nya sendiri menulis G610/G615 CSF "not supported yet") dan PanVK-Mali-Android-Stubs (alpha Juli 2026, tidak aktif).

## Detail

### 🥇 zenithblue v26.3.1 (dipilih sebagai basis build)
| Cek | Hasil |
|---|---|
| SHA256 adrenotools.zip | `7e2e9987bbebefb06f52b2570e61e6208503d4d3a10a395b97aea9b6e1fad9e4`, **cocok** dengan `SHA256SUMS` resmi |
| SHA256 gamehub.zip | `06cc42ddc545d45f0f51c8698b8bc98b681df196d691603d9c50d28ac103993d`, **cocok** |
| Isi | `libvulkan_panfrost.so` (gamehub: `libvulkan_freedreno.so`), `meta.json`, `SHA256SUMS.txt` |
| ELF | 64-bit, aarch64, shared object |
| NEEDED | liblog, libnativewindow, libsync, libm, libz, libdl, libc (semua lib sistem Android) |
| Ekspor | `HMI`, `vk_icdGetInstanceProcAddr`, `vk_icdNegotiateLoaderICDInterfaceVersion` |
| String | `kbase` ✔ `/dev/mali%d` ✔ `Mali-G615` ✔ `panvk` ✔ `CSF` ✔ |
| Lisensi | Script MIT, Mesa MIT, header kbase GPL-2.0 WITH Linux-syscall-note, sehingga **boleh di-build ulang dan dirilis** |
| Kelebihan | Satu-satunya yang punya profil build `g615-v11-csf` dan data uji G615 yang terdokumentasi. Patch performa: semaphore ditunggu di GPU, tiler heap dibuat di worker thread, shadow BCn AFRC. |

### 🥈 JimVulkan v1.6.0 r10
| Cek | Hasil |
|---|---|
| SHA256 | `7e97db4d79d81ec9461d1e0676b62a865561cb56e21c151693aa25ffbe749f1c` (repo tidak menyediakan SHA256SUMS) |
| Isi | `libvulkan_panfrost.so`, `meta.json`, `NOTICE.txt` |
| NEEDED | libhardware, liblog, libnativewindow, libsync, libm, **libc++.so**, libdl, libc |
| Catatan | Link dinamis ke `libc++.so` milik platform. Biasanya bisa dimuat, tapi kurang portabel dibanding statis. `minApi` 31. |
| Kelebihan | Basis Mesa lebih baru (27.0), lisensi MIT murni, ukuran kecil |

### 🥉 MineGraph panvk.8
| Cek | Hasil |
|---|---|
| SHA256 | `e71e23cdd2ddf52f72d7c348b5754df323cd56fbe6e0087b4c5c9b116565be4b` |
| NEEDED | lib sistem Android saja |
| Catatan | Fork dari panvk-g720-kbase-csf, fokus Mali-G720. Batching draw-path dan heap tiler 8 MiB. Lisensi tidak dinyatakan, jadi tidak dipakai sebagai basis build. |

## Kesimpulan
Basis build = **zenithblue v26.3.1** (bukti G615 paling kuat, lisensi jelas, resep build bisa direproduksi).
Kandidat #2 dipakai sebagai **cadangan uji** bila build kita gagal dimuat di perangkat.
