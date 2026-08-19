# 📜 ATURAN & STANDAR PENGERJAAN PROYEK (RULES.md)
*Dokumen ini adalah sumber kebenaran (Single Source of Truth) untuk seluruh pengembangan NyangBuddy Desktop Pet.*
*Wajib dibaca dan dipatuhi oleh AI Assistant & Developer sebelum memulai setiap penambahan fitur atau perbaikan kode.*

---

## 1. 🛡️ PRINSIP KEAMANAN & PRIVASI (ANTI-BONZIBUDDY)
1. **100% Offline (Zero Telemetry / No Network Calls):**
   * Dilarang menambahkan request HTTP/koneksi keluar ke server luar atau mengumpulkan data pengguna.
   * Semua fitur integrasi harus menggunakan file lokal (`.cat_trigger.json`) atau IPC lokal tanpa membuka port jaringan luar.
2. **Transparansi & Open Source:**
   * Semua kode harus mudah dibaca, modular, dan bersih di folder `src/`.
3. **No Admin Privileges:**
   * Aplikasi tidak boleh meminta izin administrator (UAC) atau memodifikasi registry/file sistem Windows.

---

## 2. 📁 LINGKUNGAN KERJA & ENVIRONMENT
1. **Direktori Proyek:** Seluruh kode dan aset berada di dalam folder `desktop-cat/`.
2. **Virtual Environment (`.venv`):**
   * Semua package Python **WAJIB** diinstal dan dijalankan menggunakan `.venv` lokal (`.\.venv\Scripts\python.exe` / `pip.exe`).
   * Dilarang menginstall package ke Python global.
   * Dependensi utama saat ini: `PyQt6`, `Pillow`. Update `requirements.txt` jika ada penambahan library baru.

---

## 3. 🖥️ STANDAR ARSITEKTUR GUI & WINDOW BEHAVIOR
1. **Window Flags yang Diizinkan:**
   * `Qt.WindowType.FramelessWindowHint`
   * `Qt.WindowType.WindowStaysOnTopHint`
   * `Qt.WindowType.Tool`
   * ⚠️ **DILARANG MENGGUNAKAN `Qt.WindowType.SubWindow`** (karena menyebabkan bug jendela hilang/crash saat diklik).
2. **Always on Top (Win32 API Enforcement):**
   * Mempertahankan layer z-order teratas menggunakan `ctypes.windll.user32.SetWindowPos` (`HWND_TOPMOST = -1`, `SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE | SWP_SHOWWINDOW`) pada window kucing dan balon dialog.
3. **Penempatan Bebas (Freeform Screen Placement):**
   * Kucing bebas ditaruh di mana saja di seluruh area layar (pojok atas, tengah, atas browser/IDE, dsb).
   * **Tidak ada gravitasi paksa** yang menarik kucing ke dasar layar.
   * Posisi koordinat `pos_x` dan `pos_y` harus tersimpan otomatis di `settings.json`.
   * Mode *Auto-Wander* (jalan santai) hanya bergerak secara horizontal pada ketinggian (*Y-level*) tempat kucing diletakkan.

---

## 4. 🎨 STANDAR SISTEM SPRITE & KARAKTER PIXEL-ART
1. **Spesifikasi Teknis Sprite:**
   * Base canvas: **32x32 pixel**.
   * Scaling factor: **4x** (output crisp **128x128 pixel** menggunakan `Image.Resampling.NEAREST`).
2. **State Animasi Wajib (10 States per Karakter):**
   Setiap skin/karakter baru yang ditambahkan **WAJIB** memiliki seluruh 10 state berikut (masing-masing 4 frame `0..3`):
   1. `idle` (Duduk santai, berkedip, ekor bergerak)
   2. `walk_left` (Jalan ke kiri)
   3. `walk_right` (Jalan ke kanan)
   4. `sleep` (Tidur melingkar dengan partikel Zzz)
   5. `work` / `kneading` (Mengetik di laptop mini)
   6. `pet` (Mata tersenyum, pipi merona, partikel hati)
   7. `celebrate` / `jump` (Melompat senang dengan kilauan bintang)
   8. `thinking` (Kepala miring penasaran dengan titik animasi)
   9. `drag` (Bergelantungan dengan kaki mengayun saat digeser)
   10. `land` (Mendarat membal / squish bounce saat dilepas)
3. **Pendaftaran Skin:**
   * Definisikan palet dan atribut unik di dictionary `PALETTES` pada `src/sprites.py`.
   * Jalankan `python src/sprites.py` untuk menghasilkan cache gambar ke folder `assets/sprites/<nama_skin>/`.

---

## 5. 🔊 STANDAR ERROR-HANDLING & EVENT SAFETY
1. **Fungsi Suara (`_play_sound_blip`):**
   * Harus menerima parameter default `freq=1200, dur=60`.
   * Wajib dibungkus blok `try-except` agar jika OS tidak mendukung `winsound`, aplikasi tidak crash.
2. **Event Handler Qt:**
   * `mousePressEvent`, `mouseMoveEvent`, `mouseReleaseEvent`, dan `paintEvent` tidak boleh melempar unhandled exception yang dapat menghentikan event loop Qt.

---

## 6. 🌿 STANDAR VERSION CONTROL (GIT)
1. **Branch Utama:** Seluruh pengembangan aktif berada di branch `main`.
2. **Commit Rutin:**
   * Setiap penambahan fitur, perbaikan bug, atau penambahan karakter yang sudah teruji **WAJIB langsung di-commit**.
   * Format pesan commit menggunakan konvensi standar (e.g., `feat: ...`, `fix: ...`, `docs: ...`).
3. **Kebersihan Repo:**
   * `.gitignore` wajib selalu mengecualikan `.venv/`, `__pycache__/`, `.cat_trigger.json`, dan file konfigurasi runtime lokal.

---

## 7. 📋 CHECKLIST PROTOKOL SETIAP SESI PENGERJAAN
Setiap kali AI Assistant menerima instruksi pengembangan baru, lakukan alur kerja ini secara berurutan:
- [ ] **Langkah 1:** Baca dokumen `RULES.md` ini terlebih dahulu.
- [ ] **Langkah 2:** Pastikan modifikasi dilakukan di dalam `desktop-cat/` menggunakan virtual environment `.venv`.
- [ ] **Langkah 3:** Implementasikan kode dengan mematuhi standar Window Flags, Error-handling, dan Sprite States di atas.
- [ ] **Langkah 4:** Lakukan pengujian / dry-run menggunakan `.\.venv\Scripts\python -c "import ..."` atau script verifikasi.
- [ ] **Langkah 5:** Jika ada karakter baru, jalankan generator sprite `python src/sprites.py`.
- [ ] **Langkah 6:** Lakukan `git add .` dan `git commit -m "..."`.
- [ ] **Langkah 7:** Laporkan progres dan cara pengujian ke pengguna secara ringkas dan jelas.
