# AGENTS.md: aturan wajib untuk semua AI agent di project ini

> Berlaku untuk Claude Code, OpenCode, Codex, Cursor, Gemini CLI, Copilot, dan agent lain.
> Baca file ini **utuh** sebelum bekerja. Jika ada konflik, aturan di file ini yang dipakai.

## 0. Ringkasan project
- **Nama:** xamonxx mali7300, driver Vulkan **Mesa PanVK on mali_kbase** custom.
- **Target tunggal:** Infinix Note 50X 5G (X6857) · Dimensity 7300 (MT6878) · **Mali-G615 MC2** (pan arch v11, CSF) ·
  CPU 4×A78 + 4×A55 (ARMv8.2-A) · Android 16 (SDK 36) · LCD 720p 120 Hz.
- **Pemakaian utama:** launcher GTA V ("Import driver (.zip)"), lalu Winlator/GameHub.
- **Tujuan owner:** FPS **30–60 stabil** dan suhu terkendali.
- **Repo:** https://github.com/xamonxx/driver_dimensity7300 (publik, `master`). Owner: xamonxx. Bahasa: **Indonesia**.

## 1. Urutan baca wajib (setiap sesi)
1. `AGENTS.md`
2. `memory/MEMORY.md`, lalu file memory yang relevan
3. `docs/DEVICE_INFO.md` bila tugas menyentuh performa atau kompatibilitas
4. `docs/BUILD.md` bila tugas menyentuh build, patch, atau flag

## 2. Struktur
```
README.md · AGENTS.md · CLAUDE.md · NOTICE.md · LICENSES/
build_mali7300.sh           ← build lengkap (dipakai CI)
patches/xamonxx/            ← patch milik project (Python, anchor ketat)
.github/workflows/build.yml ← CI build + audit + release
tools/audit_mali_driver.py  ← audit zip (ELF, NEEDED, ekspor ICD, string kbase/Mali)
docs/  DEVICE_INFO · CANDIDATES · BUILD · INSTALL · TESTING · COMMANDLINE
memory/                     ← memory lintas sesi
candidates/ dist/ work/     ← lokal, tidak di-commit
```

## 3. Kejujuran (WAJIB)
- Pakai label: `VERIFIED` · `OFFICIAL` · `DERIVED` · `ESTIMATED` · `UNKNOWN` · `NOT TESTED`.
- Jangan klaim FPS atau suhu tanpa data di `memory/test-results.md`.
- Driver **tidak** menambah core atau clock GPU. Frame pacer membuat frame time rata dan mengurangi panas, bukan menaikkan FPS puncak.
- PanVK-kbase = **eksperimental**. Basis diuji di G615 MC6, sedangkan **MC2 belum diuji** sampai owner melapor.
- Build sukses di CI tidak sama dengan driver jalan di HP.

## 4. Build & versi
- **Pin selalu:** commit zenithblue (`ZB_COMMIT`), Mesa (`5a07217f…` dari `sources.lock` mereka), NDK. Catat di `docs/BUILD.md` dan `memory/build-history.md`.
- **Nama zip:** `xamonxx_mali7300V<MAJOR>.<MINOR>-<varian>[-freedreno].zip`. Varian: `stable30`, `stable60`.
- `meta.json`: `name` = "xamonxx mali7300 V<ver> <Varian>", `author` = "xamonxx", `minApi` 29, `libraryName` sesuai isi zip.
- Setiap zip wajib lolos `python -I tools/audit_mali_driver.py dist/ --expect "xamonxx mali7300: frame pacer"`.
- Naikkan versi bila patch, flag, atau commit basis berubah.
- Jangan menjalankan script hasil download di PC owner. Patch basis diterapkan di CI, atau secara lokal sebagai data (`git apply` / `git am`).

## 5. Patch
- Patch basis dari zenithblue diambil saat build dan tidak di-vendor. Jangan diedit.
- Patch milik project ditaruh di `patches/xamonxx/NNNN_nama.py`. Script ini idempoten dan gagal keras bila anchor tidak cocok.
- Setiap patch baru dicatat di `memory/decisions.md` (tujuan, risiko, cara mematikan).

## 6. Batasan
- **Dilarang** menyarankan root, unlock bootloader, ubah thermal/governor, mematikan proteksi termal, APK game palsu, atau game bajakan.
- **Dilarang** mengakses `/dev/ged` (MediaTek) atau antarmuka vendor yang tidak terdokumentasi tanpa rencana uji di perangkat.
- Jangan commit binary (`.so`/`.zip`), token, atau data pribadi (IMEI/serial/MAC/IP/email). Binary hanya lewat GitHub Releases.

## 7. Memory (`memory/`)
- `MEMORY.md` adalah indeks. Setiap file memakai frontmatter `name`, `description`, `updated: YYYY-MM-DD`, `type`.
- File: `project-overview` · `user-preferences` · `decisions` · `build-history` · `test-results` · `known-issues`.
- Tanggal ditulis absolut, entri baru di atas, tanpa duplikasi. Di akhir sesi, update `project-overview` lalu commit `docs(memory): ...`.

## 8. Git
- Branch `master`. Pesan commit: `feat:` `fix:` `build:` `ci:` `docs:` `docs(memory):`.
- Push ke `build_mali7300.sh`, `patches/**`, atau workflow **memicu build CI**.

## 9. Definition of Done (rilis)
1. CI hijau, Release `v<ver>` berisi semua varian.
2. Zip diunduh ke `dist/` dan lolos audit (aarch64, ekspor ICD, string kbase/Mali-G615, string pacer, NEEDED hanya lib sistem).
3. `memory/build-history.md` diupdate (SHA256, flag, commit).
4. Status tetap `NOT TESTED` sampai owner mengirim hasil benchmark.
