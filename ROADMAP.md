# 🗺️ Master Roadmap NyangBuddy (Desktop Cat Companion)

Dokumen ini adalah panduan referensi utama pengembangan **NyangBuddy** dari awal hingga rilis penuh (Fase 1 sampai Fase 5).

---

## 📋 Ringkasan Status Tiap Fase

| Fase | Fokus Utama | Status |
| :--- | :--- | :---: |
| **Fase 1** | Core Engine, 7 Karakter Pixel Art, Jendela Transparan & Fisika Dasar | ✅ Selesai (Merged to `main`) |
| **Fase 2** | Interaksi Dinamis: 8-Arah Pandangan Mata, Kejar Kursor, Mengetik & Scroll | ✅ Selesai (Merged to `main`) |
| **Fase 3** | Health & Productivity: Pomodoro Multi-Siklus, Regang & Minum Air, Sticky Note, Alarm | ✅ Selesai (Merged to `main`) |
| **Fase 4** | Integrasi AI & Mode Khusus (Thinking, Celebrate Jump, Peek Mode, 8-Bit Meow) | 🎯 **Tahap Selanjutnya** |
| **Fase 5** | Gamifikasi (Aksesoris/Makan), Ambient Hub, & Standalone EXE Packaging | 🔮 Tahap Masa Depan |

---

## 🐾 Detail Fase 1: Core Engine & Aesthetics (✅ SELESAI)
1. **Floating Window Engine:** Jendela tanpa bingkai (*frameless*), latar transparan, dukungan High-DPI Windows, dan Win32 Always-on-Top.
2. **7 Pilihan Skin Pixel Art:**
   - Si Kalung Biru (Mochi)
   - Boss Oyen (Kacamata Hitam)
   - Si Oyen (Orange Tabby)
   - Belang Tiga (Calico / Mi-ke)
   - Si Tuxedo (Black & White)
   - Abu-Abu (Grey Tabby)
   - Si Putih (Snow White)
3. **Fisika Sub-Pixel & Animasi Dasar:** Koordinat pergerakan berbasis *float*, animasi bergelantungan saat digeser (*dangling drag*), dan animasi membal saat mendarat (*squish bounce*).
4. **Interaksi & Suara Prosedural:** Balon dialog teks otomatis (*speech bubble*) dan efek audio blip sintetis ringan.
5. **System Tray Integration:** Ikon di tray Windows untuk pengaturan cepat, ganti karakter, dan keluar.

---

## ⚡ Detail Fase 2: Interaksi Dinamis & Comnyang Dynamics (✅ SELESAI)
6. **8-Direction Eye Tracking:** Bola mata kucing mengikuti pergerakan kursor mouse secara *real-time* (36 frame ter-cache $O(1)$).
7. **Mouse Hunt & Pounce:** Gerakan kursor cepat memicu kucing berlari mengejar kursor, menerkam, lalu masuk mode dielus.
8. **Mochi Inertia Wobble:** Efek goyangan inersia berbasis pegas (*damped spring*) saat kucing digeser kursor.
9. **Global Keyboard Kneading & Overheat:** Kucing otomatis mengetik laptop mini saat pengguna mengetik, dengan efek uap panas (*steam puffs*) jika mengetik sangat cepat.
10. **Paper Unroll Scroll Reaction:** Menggulung roda mouse/touchpad membuat kucing menggelar gulungan kertas dengan cakarnya.
11. **Sistem Skala Bebas & Ctrl+Scroll Zoom:** Pilihan ukuran 48px - 256px serta zoom dinamis menggunakan shortcut `Ctrl + Mouse Wheel`.
12. **CLI Notification Watcher:** Skrip `notify.py` berbasis soket lokal untuk integrasi dengan terminal, skrip build, atau AI coding agent.

---

## ⏱️ Detail Fase 3: Health, Wellness & Productivity (✅ SELESAI)
13. **Multi-Cycle Auto Pomodoro Engine:** Sesi fokus & break otomatis (Standar 25/5x4, Sprint 50/10x2, dan Custom Dialog).
14. **Floating Pixel Pomodoro Badge:** Mini badge retro di samping kucing dengan hitung mundur, progress bar, dan label siklus `[2/4]`.
15. **Transisi Tengah Layar (Center-Screen Glide):**
    - **Peregangan Yoga Postur:** Kucing membesar 1.5x dan memperagakan pose yoga dengan lonceng meditasi.
    - **Minum Air (Hydration):** Kucing meminum mangkuk air keramik dengan efek gelembung air segar.
    - **Rutinitas Kombinasi (Combo):** Menjalankan peregangan + minum air berurutan tanpa bentrok.
16. **Persistent Sticky Note:** Catatan tempel kuning pastel mengambang di sebelah kiri kucing untuk target harian.
17. **Custom Alarm Dialog:** Timer hitung mundur dengan pesan kustom dan peringatan layar tengah.
18. **Personalisasi & Anti-Clutter:** Sapaan nama pengguna dan penyembunyian badge otomatis saat balon kata muncul.
19. **Optimasi Performa & Topmost:** Z-order anti-tertimpa yang tangguh, startup instan non-blocking, dan fisika 60 FPS murni.

---

## 🤖 Detail Fase 4: Integrasi AI & Mode Khusus (🎯 TAHAP BERIKUTNYA)
20. **15. AI Agent Thinking Mode:**
    - Mendeteksi aktivitas tool AI/coding (`notify.py --state thinking`).
    - Pose kucing berpikir dengan titik-titik melayang (*floating thought bubble* `...`).
21. **16. AI Agent Done Jump (Celebrate):**
    - Memicu perayaan saat AI / tugas coding selesai (`notify.py --state celebrate`).
    - Kucing melompat gembira dengan partikel bintang (*sparkles*) dan suara ceria.
22. **17. Peek Mode (Mode Mengintip Tepi Layar):**
    - Saat pengguna menonton video *fullscreen* atau bermain game, kucing tidak menutupi layar.
    - Kucing bergeser ke tepi layar monitor (*screen edge*) dan mengintipkan kepala/matanya dari samping/bawah.
23. **18. Sound FX & 8-Bit Meow Bervariasi:**
    - Efek suara meow 8-bit retro yang lebih bervariasi (suara manja saat dielus, bangun tidur, kaget saat berburu, dan alarm selesai).

---

## 🔮 Detail Fase 5: Gamifikasi, Productivity Hub & Distribusi (🔮 TAHAP MASA DEPAN)
24. **Gamifikasi & Pet Care (Aksesoris & Kasih Makan):**
    - **Feeding System:** Lempar ikan/snack ke kucing dengan animasi mengunyah dan partikel cinta.
    - **Mainan Interaktif:** Bola benang wol (*yarn ball*) atau mode *Laser Pointer*.
    - **Sistem Wardrobe / Aksesoris:** Kucing bisa memakai topi penyihir, mahkota, pita, atau syal di atas skin apa pun.
    - **Mood & Affection Meter:** Bar kesenangan kucing yang bertambah saat dirawat.
25. **Productivity Hub & Ambient Sound:**
    - **Cozy Lofi/Ambient Generator:** Suara santai hujan, perapian, atau kafe lokal yang ringan.
    - **Daily Productivity Summary:** Rekap statistik harian (jumlah siklus Pomodoro & minum air) dengan grafik pixel retro.
    - **Mini Break Games:** Game mini 1 menit saat jeda istirahat Pomodoro.
26. **Standalone EXE Packaging & Distribusi:**
    - Build file `.exe` mandiri (portable & installer) tanpa dependensi Python eksternal.
    - Ikon aplikasi resmi Windows dan rilis final.
