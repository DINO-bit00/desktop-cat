# 🐱 NyangBuddy (Desktop Cat Companion)

Aplikasi **Desktop Companion / Virtual Pet Kucing** berbasis Python yang dibuat dari nol (*from scratch*). Terinspirasi dari konsep *cozy productivity* seperti Comnyang, namun dirancang dengan prinsip **100% Aman, Transparan, Offline, dan Zero Telemetry/Spyware**.

---

## 🛡️ Mengapa Ini Jauh Lebih Aman dari BonziBUDDY / Aplikasi Tertutup?

1. **Zero Network Requests (100% Offline):** Tidak ada kode yang menghubungi server eksternal atau mengirim data pribadi kamu ke internet.
2. **Open Source & Local Code:** Semua kode sumber dapat kamu periksa dan kustomisasi sendiri di folder `src/`.
3. **Tanpa Hak Akses Administrator:** Berjalan murni di ruang user biasa tanpa mengotak-atik sistem registry atau file Windows sensitif.

---

## ✨ Fitur-Fitur Utama

* **🐾 Karakter & Pixel Art Kucing:**
  * Pilihan Skin: **Si Oyen (Orange Tabby)**, **Belang Tiga (Calico)**, **Si Tuxedo (Black & White)**, **Abu-Abu (Grey Tabby)**, dan **Si Putih (Snow White)**.
  * Ragam Animasi: *Idle*, *Jalan (Wander)*, *Tidur (Sleep)*, *Ngoding/Kneading (Work)*, *Dielus (Pet/Purr)*, *Melompat Senang (Celebrate)*, *Berpikir (Thinking)*.
* **✨ Interaksi Mengambang, Bebas & Transparan:**
  * Jendela tanpa bingkai (*frameless*), latar transparan, dan **Always on Top** (menggunakan Win32 API).
  * **Bebas Diletakkan di Mana Saja:** Kucing bisa kamu taruh di pojok atas, tengah layar, atas browser, samping IDE, atau di atas taskbar (posisi tersimpan otomatis!).
  * **Animasi Saat Digeser / Pindah (*Dangling & Landing*):** Saat kamu klik dan geser (*drag*), kucing akan bergelantungan dengan kaki mengayun lucu dan ekor bergoyang. Saat dilepas (*drop*), kucing akan mendarat dengan animasi membal (*squish bounce*).
  * Klik kiri biasa untuk mengelus (*petting*) memunculkan balon dialog lucu.
* **⏱️ Produktivitas & Kesehatan:**
  * **Pomodoro Focus Timer (25m / 50m / Custom):** Saat mode fokus aktif, kucing akan berubah ke animasi mengetik/bekerja (*work mode*). Ketika selesai, kucing akan melompat gembira (*celebrate*)!
  * **Health & Hydration Reminders:** Pengingat minum air putih dan peregangan postur tubuh berkala.
  * **Pinned Focus Goal:** Catat satu target pentingmu untuk ditampilkan oleh si kucing.
* **🤖 Integrasi CLI / Script / AI Agent (Offline Watcher):**
  * Kamu bisa memicu reaksi kucing dari terminal, script build, git hook, atau AI coding tool dengan perintah sederhana:
    ```bash
    python notify.py "Halo! Sedang deploy project..."
    python notify.py --state thinking --msg "Menjalankan unit test..."
    python notify.py --state celebrate --msg "Semua test berhasil! 🎉"
    ```

---

## 🚀 Cara Menjalankan

### Cara 1: Menggunakan File Batch (Paling Mudah)
Cukup **double-click** file `run.bat` di dalam folder `desktop-cat/`.

### Cara 2: Melalui Terminal (PowerShell / CMD)
```powershell
# Buka direktori desktop-cat
cd desktop-cat

# Jalankan menggunakan virtual environment
.\.venv\Scripts\python main.py
```

---

## 🎮 Kontrol & Navigasi

| Aksi | Kontrol |
| :--- | :--- |
| **Elus Kucing** | Klik Kiri (*Left Click*) |
| **Pindah Posisi** | Klik Kiri & Geser (*Drag & Drop*) |
| **Buka Menu Kontrol** | Klik Kanan (*Right Click*) |
| **Mulai / Stop Pomodoro Cepat** | Dobel Klik Kiri (*Double Click*) |
| **Tutup Balon Dialog** | Klik pada balon dialog |

---

## 🎨 Menambah / Mengubah Kostum & Animasi
Semua logika pembuatan sprite pixel art ada di [`src/sprites.py`](src/sprites.py). Kamu bisa menambahkan warna palette baru di kamus `PALETTES` sesuai dengan kucing kesayanganmu!
