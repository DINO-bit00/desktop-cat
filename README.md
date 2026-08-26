# 🐱 NyangBuddy (Desktop Cat Companion)

<div align="center">

![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?style=for-the-badge&logo=windows)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)
![Architecture](https://img.shields.io/badge/Architecture-x64%20Standalone-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)

**Virtual Pet & Productivity Companion untuk Desktop Windows**  
*100% Offline, Transparan, Bebas Telemetri, Ringan, dan Dibuat dari Nol (From Scratch) dengan Python & PyQt6.*

[📥 **Download NyangBuddy.exe (Rilis Terbaru)**](https://github.com/DINO-bit00/desktop-cat/releases/latest) • [✨ Fitur](#-fitur-fitur-unggulan) • [🎮 Kontrol](#-panduan-kontrol--navigasi) • [🛠️ Build dari Source](#-cara-menjalankan-dari-source-code)

---

</div>

Inspired by cozy virtual pets (seperti *Comnyang* & *Oneko*), **NyangBuddy** adalah teman kucing pixel-art interaktif yang menemani aktivitas harianmu di layar monitor. Dilengkapi fisika 60 FPS, pelacakan mata dinamis, interaksi mengetik & scrolling, asisten fokus Pomodoro multi-siklus, pengingat peregangan postur & minum air, sticky note target, hingga integrasi otomatis dengan AI Coding Agent.

---

## 📥 Download & Instalasi Cepat

Tidak perlu install Python atau mengunduh dependency rumit! Kamu bisa langsung mengunduh file `.exe` mandiri (*standalone*):

### 👉 [**Unduh NyangBuddy v1.0.0 (NyangBuddy.exe)**](https://github.com/DINO-bit00/desktop-cat/releases/latest)

1. Unduh **`NyangBuddy.exe`** dari halaman [GitHub Releases](https://github.com/DINO-bit00/desktop-cat/releases/latest).
2. Pindahkan file `.exe` ke folder favoritmu (misal: `C:\Users\NamaKamu\NyangBuddy\`).
3. **Klik 2x `NyangBuddy.exe`** dan kucing kesayanganmu langsung hadir di layar! 🐾

> [!TIP]
> **Autostart saat Windows Nyala:** Klik kanan pada kucing atau ikon di System Tray (dekat jam taskbar) -> pilih **⚙️ Pengaturan & Perilaku** -> centang **🚀 Jalankan saat Startup**.

---

## 🛡️ Jaminan Privasi & Keamanan (100% Offline & Aman)

1. 🔒 **Zero Network Requests (100% Offline):** Tidak ada koneksi internet sama sekali. Tidak ada analitik, pelacak, ataupun telemetri.
2. 📖 **Open Source & Transparan:** Seluruh kode sumber di folder `src/` dapat diaudit, dimodifikasi, dan dikembangkan secara bebas.
3. 🛡️ **Tanpa Hak Akses Administrator:** Berjalan sepenuhnya di *user space* tanpa memerlukan izin Administrator.
4. ⚙️ **Penyimpanan Lokal:** Konfigurasi tersimpan rapi dalam format JSON lokal (`settings.json`).
5. 🔇 **Mode Senyap (Zero Disk & Audio Overload):** Ringan, tidak memakan penyimpanan, dan hening tanpa mengganggu fokus kerja.

---

## ✨ Fitur-Fitur Unggulan

### 🐾 1. Karakter & Pixel Art Kucing (7 Pilihan Skin)
Pilih kucing favoritmu melalui menu klik kanan:
* 🐱 **Si Kalung Biru (Mochi)**: Kucing abu-abu chibi dengan kepala miring menggemaskan dan kalung biru toska cerah.
* 🕶️ **Boss Oyen (Kacamata Hitam)**: Kucing oyen gembul bergaya keren dengan kacamata hitam *swag*.
* 🦁 **Si Oyen (Orange Tabby)**: Kucing oyen klasik yang ceria dan aktif.
* 🎨 **Belang Tiga (Calico / Mi-ke)**: Kucing tiga warna pembawa keberuntungan.
* 🎩 **Si Tuxedo (Black & White)**: Kucing hitam elegan dengan dada dan kaos kaki putih.
* 🩶 **Abu-Abu (Grey Tabby)**: Kucing abu-abu lembut bermata biru.
* ❄️ **Si Putih (Snow White)**: Kucing putih salju bersih dan anggun.

---

### 👑 2. Koleksi Aksesoris & Topi (Wardrobe System)
Hiasi kucingmu dengan berbagai aksesoris pixel-art yang menempel presisi di atas kepala:
* 👑 **Mahkota Kerajaan (Royal Crown)**: Mahkota emas megah dengan permata merah ruby.
* 🧙 **Topi Penyihir (Wizard Hat)**: Topi ungu misterius dengan gesper emas bercahaya.
* 🕶️ **Kacamata Hitam (Sunglasses)**: Kacamata gaya gelap *cool & stylish*.
* 🧣 **Syal Musim Dingin (Winter Scarf)**: Syal rajut merah hangat di leher kucing.
* 🎀 **Pita Lucu (Cute Ribbon)**: Pita merah muda manis di atas telinga.
* 🌸 **Pin Bunga Sakura (Flower Pin)**: Bunga mekar cantik beraksen lembut.

---

### 🎮 3. Fisika & Animasi Interaktif (Comnyang Physics Engine 60 FPS)
* **👀 8-Direction Eye Tracking:** Mata kucing mengikuti pergerakan kursor mouse secara *real-time* (didukung 36 state frame cache berkecepatan $O(1)$).
* **🎯 Mouse Hunt & Pounce:** Gerakan kursor mouse yang cepat akan memicu kucing berlari mengejar kursor, menerkam membal (*squish bounce*), lalu beralih ke mode dielus (*petting*).
* **🎈 Mochi Inertia Wobble:** Saat digeser (*drag & drop*), kucing bergelantungan dengan fisika pegas *damped inertia* dan mendarat dengan lentur.
* **💻 Global Keyboard Kneading (Work Mode):** Kucing otomatis mengaduk/mengetik di laptop mini saat kamu sedang mengetik di aplikasi apa pun.
* **♨️ Overheat Mode:** Ketikan sangat cepat memicu efek uap panas (*steam puffs*) dan pesan penyemangat lucu.
* **📜 Paper Unroll Scroll Reaction:** Menggulung *mouse wheel* atau *touchpad* 2-jari membuat kucing menggelar gulungan kertas dengan cakarnya.
* **🚶 Autonomous Wander & Sleep:** Kucing dapat berjalan santai di layar atau tidur pulas ketika tidak ada aktivitas.
* **👁️ Mode Mengintip (Peek Mode):** Kucing meluncur ke tepi layar (Kiri, Kanan, atau Bawah) dan mengintip santai saat kamu butuh layar bersih.
* **📺 Auto-Peek Fullscreen:** Kucing otomatis minggir ke tepi layar saat kamu membuka game atau video fullscreen!
* **🔍 Ukuran Bebas & Ctrl+Scroll Zoom:** Pilihan ukuran Mini (64px) hingga Raksasa (256px), dialog ukuran kustom, atau *zoom in/out* langsung menggunakan shortcut `Ctrl + Scroll`.

---

### ⏱️ 4. Produktivitas & Kesehatan (Focus & Health Hub)
* **🍅 Multi-Cycle Auto Pomodoro Timer:**
  * **Mulai Standar:** 25 menit Fokus / 5 menit Break (4 Siklus otomatis).
  * **Mulai Sprint:** 50 menit Fokus / 10 menit Break (2 Siklus).
  * **Atur Sesi Kustom:** Dialog modern untuk mengatur durasi fokus, break, dan jumlah siklus dengan estimasi total waktu real-time.
  * **Floating Pixel Pomodoro Badge:** Mini badge retro di samping kucing yang menampilkan countdown waktu, progress bar, dan label siklus aktif `[2/4]`.
* **🧘 Pengingat Regang & Postur (Cat Yoga):** Kucing meluncur halus (*cubic ease-in-out glide*) ke tengah layar, membesar 1.5x, dan memandu pose yoga peregangan kucing.
* **💧 Pengingat Minum Air (Hydration):** Kucing meluncur ke tengah layar, memunculkan mangkuk keramik, dan meminum air dengan animasi lidah.
* **🧘💧 Rutinitas Lengkap (Combo Routine):** Menjalankan peregangan postur dan minum air secara berurutan dengan antrean cerdas (*smart reminder queue*).
* **📌 Persistent Sticky Note:** Catatan tempel kuning pastel mengambang di sebelah kiri kucing untuk mencatat target kerja atau *to-do list* harianmu.
* **⏰ Custom Alarm:** Pasang timer hitung mundur dengan pesan pengingat khusus (misal: *"Meeting jam 2"*, *"Cek oven"*).
* **👤 Personalisasi Nama:** Kucing akan mengingat namamu dan menyapa dengan ramah saat aplikasi pertama kali dijalankan.
* **✨ Anti-Clutter Notification System:** Balon kata (*speech bubble*) otomatis menyembunyikan Sticky Note & Pomodoro Badge sementara agar tidak saling bertabrakan, lalu menampilkannya kembali setelah selesai.

---

### 🤖 5. Integrasi Cerdas AI Coding Assistant
NyangBuddy secara otomatis tersinkronisasi dengan AI Assistant (Antigravity, Gemini CLI, Cursor, Claude, ChatGPT):
* **Mode Berpikir (Thinking Mode):** Saat kamu mengirim perintah ke AI atau AI sedang berpikir menghasilkan kode, kucing akan otomatis menampilkan animasi berpikir (*bubble thought* & *sparkle*).
* **Mode Selebrasi (Task Done):** Saat AI selesai mengeksekusi tugas, kucing akan melompat gembira merayakan keberhasilan tugasmu! 🎉

Kamu juga bisa memicu respon dan dialog kucing secara manual dari terminal / CI/CD:
```bash
# Menampilkan pesan biasa
python notify.py "Deploy production selesai!"

# Menampilkan pesan dengan animasi tertentu
python notify.py --state thinking --msg "Sedang menjalankan test suite..."
python notify.py --state celebrate --msg "Build production berhasil! 🎉"
python notify.py --state work --msg "Mulai kompilasi source code..."
```

---

## 🎮 Panduan Kontrol & Navigasi

| Aksi | Kontrol |
| :--- | :--- |
| **Elus Kucing** | Klik Kiri (*Left Click*) pada kucing |
| **Pindah Posisi Bebas** | Klik Kiri & Geser (*Drag & Drop*) ke area layar mana saja |
| **Buka Menu Kontrol Lengkap** | Klik Kanan (*Right Click*) pada kucing atau ikon Tray |
| **Zoom Ukuran Karakter** | Tahan `Ctrl` + Gulir Roda Mouse (*Ctrl + Mouse Wheel*) |
| **Tutup Balon Percakapan** | Klik langsung pada balon kata |
| **Hentikan Sesi Pomodoro** | Klik langsung pada mini badge Pomodoro |

### 🧭 Struktur Menu Klik Kanan
Menu klik kanan dirancang rapi dalam 3 kategori utama:
1. 🐱 **Karakter & Kostum:**
   - Pilih 7 Skin Kucing
   - Pilih 6 Aksesoris & Topi
   - Mode Mengintip (Tepi Kanan, Kiri, Bawah)
   - Mode Berjalan Bebas (Wander on/off)
2. ⏱️ **Produktivitas & Kesehatan:**
   - Mulai Pomodoro (Standar 25m, Sprint 50m, Atur Kustom)
   - Pasang Target Kerja (*Sticky Note*)
   - Set Alarm & Pengingat
   - Latihan Regang Postur & Minum Air
3. ⚙️ **Pengaturan & Perilaku:**
   - Ubah Ukuran Kucing (Kecil, Sedang, Besar, Raksasa, Kustom)
   - Otomatis Mengintip saat Game/Video Fullscreen
   - Jalankan saat Windows Startup
   - Pengaturan Nama & Preferensi Suara
   - 📂 Buka Folder Aplikasi & Rilis Executable
4. ❌ **Keluar**

---

## 🛠️ Cara Menjalankan dari Source Code

Jika kamu ingin memodifikasi atau mengembangkan kodenya sendiri:

### 1. Prasyarat
- Python 3.10 atau lebih baru
- Windows 10 / 11

### 2. Clone Repositori & Setup Virtual Environment
```powershell
# Clone repositori
git clone https://github.com/DINO-bit00/desktop-cat.git
cd desktop-cat

# Buat virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependensi
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi
```powershell
python main.py
```
*(Atau cukup klik 2x `run.bat`)*

### 4. Build Ulang File `.exe` Mandiri
Untuk mengompilasi ulang kode menjadi satu file executable mandiri:
```powershell
python build.py
```
*(Hasil build akan tersedia di folder `dist/NyangBuddy.exe`)*

---

## 📂 Struktur Folder Proyek

```
desktop-cat/
├── dist/
│   └── NyangBuddy.exe       # Standalone executable siap pakai (~42 MB)
├── src/
│   ├── ai_watcher.py        # Sinkronisasi status AI Agent (Antigravity/Gemini/Web AI)
│   ├── alarm_dialog.py      # Dialog alarm & pengingat kustom
│   ├── audio.py             # Zero-disk procedural sound & silent engine
│   ├── autostart.py         # Integrasi registry startup Windows (HKCU Run)
│   ├── global_hooks.py      # Thread-safe global keyboard & mouse scroll watcher
│   ├── local_watcher.py     # Local socket listener untuk CLI notify.py
│   ├── pet_window.py        # Core engine: 60 FPS physics, state machine, window z-order
│   ├── pomodoro.py          # Logika Pomodoro multi-cycle & reminder timer
│   ├── pomodoro_badge.py    # Mini widget badge Pomodoro retro pixel
│   ├── pomodoro_dialog.py   # Dialog kustomisasi sesi Pomodoro
│   ├── settings.py          # Manajemen konfigurasi JSON lokal
│   ├── speech_bubble.py     # Balon kata dengan auto-wrap & tail dinamis
│   ├── sprites.py           # Pixel art procedural renderer, 7 skin palettes & accessories
│   ├── sticky_note.py       # Floating sticky note widget target fokus
│   └── tray.py              # System tray icon & background menu
├── build.py                 # Script PyInstaller otomatis untuk build .exe
├── build_exe.bat            # One-click build script
├── main.py                  # Entry point aplikasi & Windows multimedia timer init
├── notify.py                # CLI trigger untuk automasi & AI agent
├── run.bat                  # One-click developer launcher
├── requirements.txt         # Daftar pustaka Python (PyQt6, pynput, Pillow)
└── README.md                # Dokumentasi lengkap proyek
```

---

## 📜 Lisensi & Kontribusi

Proyek ini bersifat open-source di bawah lisensi [MIT](LICENSE). Silakan berkontribusi, membuka issue, atau mengajukan pull request!

Dibuat dengan ❤️ untuk menemani hari-harimu di depan komputer! 🐾✨
