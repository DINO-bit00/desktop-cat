# 🐱 NyangBuddy (Desktop Cat Companion)

> **Virtual Pet & Productivity Companion untuk Desktop Windows**  
> 100% Offline, Transparan, Bebas Telemetri, Ringan, dan Dibuat dari Nol (*From Scratch*) dengan Python & PyQt6.

Inspired by cozy virtual pets (seperti *Comnyang* & *Oneko*), **NyangBuddy** adalah teman kucing pixel-art interaktif yang menemani aktivitas harianmu di layar monitor. Dilengkapi fisika 60 FPS, pelacakan mata dinamis, interaksi mengetik & scrolling, asisten fokus Pomodoro multi-siklus, pengingat peregangan postur & minum air, sticky note target, hingga integrasi CLI untuk AI Coding Agent.

---

## 🛡️ Jaminan Privasi & Keamanan (100% Offline & Aman)

1. 🔒 **Zero Network Requests (100% Offline):** Tidak ada koneksi internet sama sekali. Tidak ada analitik, pelacak, ataupun telemetri.
2. 📖 **Open Source & Transparan:** Seluruh kode sumber di folder `src/` dapat diaudit, dimodifikasi, dan dikembangkan secara bebas.
3. 🛡️ **Tanpa Hak Akses Administrator:** Berjalan sepenuhnya di *user space* tanpa memerlukan izin Administrator.
4. ⚙️ **Penyimpanan Lokal:** Konfigurasi tersimpan rapi dalam format JSON lokal (`settings.json`).

---

## ✨ Fitur-Fitur Unggulan

### 🐾 1. Karakter & Pixel Art Kucing (7 Pilihan Skin)
Pilih kucing favoritmu melalui klik kanan:
* 🐱 **Si Kalung Biru (Mochi)**: Kucing abu-abu chibi dengan kepala miring menggemaskan dan kalung biru toska cerah.
* 🕶️ **Boss Oyen (Kacamata Hitam)**: Kucing oyen gembul bergaya keren dengan kacamata hitam *swag*.
* 🦁 **Si Oyen (Orange Tabby)**: Kucing oyen klasik yang ceria dan aktif.
* 🎨 **Belang Tiga (Calico / Mi-ke)**: Kucing tiga warna pembawa keberuntungan.
* 🎩 **Si Tuxedo (Black & White)**: Kucing hitam elegan dengan dada dan kaos kaki putih.
* 🩶 **Abu-Abu (Grey Tabby)**: Kucing abu-abu lembut bermata biru.
* ❄️ **Si Putih (Snow White)**: Kucing putih salju bersih dan anggun.

---

### 🎮 2. Fisika & Animasi Interaktif (Comnyang Physics Engine 60 FPS)
* **👀 8-Direction Eye Tracking:** Mata kucing mengikuti pergerakan kursor mouse secara *real-time* (didukung 36 state frame cache berkecepatan $O(1)$).
* **🎯 Mouse Hunt & Pounce:** Gerakan kursor mouse yang cepat akan memicu kucing berlari mengejar kursor, menerkam membal (*squish bounce*), lalu beralih ke mode dielus (*petting*).
* **🎈 Mochi Inertia Wobble:** Saat digeser (*drag & drop*), kucing bergelantungan dengan fisika pegas *damped inertia* dan mendarat dengan lentur.
* **💻 Global Keyboard Kneading (Work Mode):** Kucing otomatis mengaduk/mengetik di laptop mini saat kamu sedang mengetik di aplikasi apa pun.
* **♨️ Overheat Mode:** Ketikan sangat cepat memicu efek uap panas (*steam puffs*) dan pesan penyemangat lucu.
* **📜 Paper Unroll Scroll Reaction:** Menggulung *mouse wheel* atau *touchpad* 2-jari membuat kucing menggelar gulungan kertas dengan cakarnya.
* **🚶 Autonomous Wander & Sleep:** Kucing dapat berjalan santai di layar atau tidur pulas ketika tidak ada aktivitas.
* **🔍 Ukuran Bebas & Ctrl+Scroll Zoom:** Pilihan ukuran Mini (64px) hingga Raksasa (256px), dialog ukuran kustom, atau *zoom in/out* langsung menggunakan shortcut `Ctrl + Scroll`.

---

### ⏱️ 3. Produktivitas & Kesehatan (Phase 3 Engine)
* **🍅 Multi-Cycle Auto Pomodoro Timer:**
  * **Mulai Standar:** 25 menit Fokus / 5 menit Break (4 Siklus otomatis).
  * **Mulai Sprint:** 50 menit Fokus / 10 menit Break (2 Siklus).
  * **Atur Sesi Kustom:** Dialog modern untuk mengatur durasi fokus, break, dan jumlah siklus dengan estimasi total waktu real-time.
  * **Floating Pixel Pomodoro Badge:** Mini badge retro di samping kucing yang menampilkan sisa waktu, progress bar, dan label siklus aktif `[2/4]`.
* **🧘 Pengingat Regang & Postur (Cat Yoga):** Kucing meluncur halus (*cubic ease-in-out glide*) ke tengah layar, membesar 1.5x, dan memandu pose yoga peregangan kucing lengkap dengan suara bel meditasi.
* **💧 Pengingat Minum Air (Hydration):** Kucing meluncur ke tengah layar, memunculkan mangkuk keramik, meminum air dengan animasi lidah dan efek suara gelembung air segar.
* **🧘💧 Rutinitas Lengkap (Combo Routine):** Menjalankan peregangan postur dan minum air secara berurutan dengan antrean cerdas (*smart reminder queue*).
* **📌 Persistent Sticky Note:** Catatan tempel kuning pastel mengambang di sebelah kiri kucing untuk mencatat target kerja atau *to-do list* harianmu.
* **⏰ Custom Alarm:** Pasang timer hitung mundur dengan pesan pengingat khusus (misal: *"Meeting jam 2"*, *"Cek oven"*).
* **👤 Personalisasi Nama:** Kucing akan mengingat namamu dan menyapa dengan ramah saat aplikasi pertama kali dijalankan.
* **✨ Anti-Clutter Notification System:** Balon kata (*speech bubble*) otomatis menyembunyikan Sticky Note & Pomodoro Badge sementara agar tidak saling bertabrakan, lalu menampilkannya kembali setelah selesai.

---

### ⚡ 4. Performa & Integrasi Windows
* **🔝 Robust Always-On-Top:** Integrasi API Win32 memastikan kucing dan widget pendukungnya tetap berada di layer teratas layar tanpa *flicker*.
* **🚀 Instant Startup (<80ms):** Sistem *deferred pre-caching* memastikan jendela kucing langsung muncul tanpa *lag*.
* **🪟 Windows Startup Registry:** Opsi jalankan otomatis saat Windows *booting* (`pythonw.exe`) dengan *startup delay* 5 detik agar tidak membebani sistem.
* **🔔 Smart Audio Blips:** Efek audio prosedural murni tanpa dependensi file eksternal yang berat.

---

### 🤖 5. Integrasi CLI & AI Coding Agent (Offline Watcher)
Kamu bisa memicu respon dan dialog kucing langsung dari terminal, script build CI/CD, git hook, atau AI coding tool:

```bash
# Menampilkan pesan biasa
python notify.py "Deploy production selesai!"

# Menampilkan pesan dengan animasi tertentu
python notify.py --state thinking --msg "Sedang menjalankan unit test..."
python notify.py --state celebrate --msg "Semua test berhasil! 🎉"
python notify.py --state work --msg "Mulai kompilasi source code..."
```

---

## 🚀 Cara Menjalankan

### Cara 1: Menggunakan `run.bat` (Paling Mudah)
Cukup **double-click** file `run.bat` yang ada di dalam folder proyek.

### Cara 2: Melalui Terminal (PowerShell / CMD)
```powershell
# Buka direktori proyek
cd desktop-cat

# Jalankan dengan virtual environment
.\.venv\Scripts\python main.py
```

---

## 🎮 Panduan Kontrol & Navigasi

| Aksi | Kontrol |
| :--- | :--- |
| **Elus Kucing** | Klik Kiri (*Left Click*) pada kucing |
| **Pindah Posisi Bebas** | Klik Kiri & Geser (*Drag & Drop*) ke area layar mana saja |
| **Buka Menu Kontrol Lengkap** | Klik Kanan (*Right Click*) pada kucing |
| **Zoom Ukuran Karakter** | Tahan `Ctrl` + Gulir Roda Mouse (*Ctrl + Mouse Wheel*) |
| **Tutup Balon Percakapan** | Klik langsung pada balon kata |
| **Hentikan Sesi Pomodoro** | Klik langsung pada mini badge Pomodoro |

---

## 📂 Struktur Proyek

```
desktop-cat/
├── src/
│   ├── alarm_dialog.py      # Dialog alarm & pengingat kustom
│   ├── autostart.py         # Integrasi registry startup Windows (HKCU Run)
│   ├── global_hooks.py      # Global keyboard & mouse scroll watcher
│   ├── local_watcher.py     # Local socket listener untuk CLI notify.py
│   ├── pet_window.py        # Core engine: 60 FPS physics, state machine, z-order
│   ├── pomodoro.py          # Logika Pomodoro multi-cycle & reminder timer
│   ├── pomodoro_badge.py    # Mini widget badge Pomodoro retro pixel
│   ├── pomodoro_dialog.py   # Dialog kustomisasi sesi Pomodoro
│   ├── settings.py          # Manajemen konfigurasi JSON lokal
│   ├── speech_bubble.py     # Balon kata dengan auto-wrap & tail dinamis
│   ├── sprites.py           # Pixel art procedural renderer & 7 skin palettes
│   ├── sticky_note.py       # Floating sticky note widget target fokus
│   └── tray.py              # System tray icon & background menu
├── main.py                  # Entry point aplikasi & Windows multimedia timer init
├── notify.py                # CLI trigger untuk automasi & AI agent
├── run.bat                  # One-click launcher untuk Windows
├── requirements.txt         # Daftar pustaka Python (PyQt6, pynput, pillow, numpy)
└── README.md                # Dokumentasi lengkap proyek
```

---

## 📜 Lisensi & Kontribusi
Proyek ini bersifat open-source di bawah lisensi MIT. Silakan fork, tambahkan skin kustom, atau kembangkan fitur baru sesuai kebutuhanmu! 🐾
