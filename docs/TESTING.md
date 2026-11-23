# 🧪 TESTING: protokol uji di HP

1. **Load:** import zip, lalu pastikan nama driver tampil dan game tidak crash di menu.
2. **Baseline:** Benchmark Runs dengan **driver bawaan Mali** (setting sama), lalu screenshot.
3. **stable30:** Benchmark Runs, lalu screenshot. Lihat avg, min, "% frames at 30 fps or better", dan "99% under X ms".
4. **stable60:** ulangi (opsional).
5. Catat kondisi: baterai %, charging/bypass, suhu ruangan, casing, refresh layar.

Target lulus "stabil 30": avg ≈ 30, **≥99% frame ≥30 fps**, 99% frame time < 34 ms, tidak crash 15 menit.

Hasil dicatat agent ke `memory/test-results.md` dengan format tabel per pass.
