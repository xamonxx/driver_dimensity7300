# NOTICE

Repositori ini memakai beberapa lisensi sekaligus.

1. **Script, workflow, tool, dan dokumen proyek ini** (`build_mali7300.sh`, `tools/`, `patches/xamonxx/`, `docs/`, `.github/`): MIT (`LICENSES/MIT.txt`).
2. **Mesa** (diambil saat build, tidak di-vendor): lisensi upstream Mesa, mayoritas MIT/X11.
3. **Patch PanVK-kbase** dari [zenithblue-oss/panvk-kbase-android](https://github.com/zenithblue-oss/panvk-kbase-android)
   (diambil saat build pada commit yang di-pin): turunan Mesa, tetap berlisensi Mesa. Script mereka MIT.
4. **Header UAPI Arm Mali kbase** (ikut masuk ke build lewat patch di atas): `GPL-2.0 WITH Linux-syscall-note`
   (`LICENSES/GPL-2.0.txt`, `LICENSES/Linux-syscall-note.txt`).

Setiap zip rilis menyertakan `NOTICE.txt`. Proyek ini tidak berafiliasi dengan Arm, MediaTek, Infinix, atau Mesa.
