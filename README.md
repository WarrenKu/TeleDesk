<div align="center">

# 🤖 TeleDesk Controller

**Kendalikan PC kamu dari mana saja — lewat Telegram.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Browser-45BA4B?style=for-the-badge&logo=playwright&logoColor=white)
![License](https://img.shields.io/badge/License-Personal-orange?style=for-the-badge)

> *Remote desktop control via Telegram — buka browser, putar musik, ambil screenshot, baca file, semua dari HP kamu.*

[![typing-svg](https://readme-typing-svg.herokuapp.com?size=22&duration=4000&center=true&vCenter=true&lines=Hello+world!;I'm+Rick+Warren;Welcome+to+scripping+broo!)](https://github.com/WarrenKu)

</div>

---

## 📖 Tentang Project

**TeleDesk Controller** adalah bot Telegram yang berjalan di PC Windows kamu dan memungkinkan kamu mengontrol desktop dari jarak jauh — cukup lewat chat Telegram di HP. Tidak perlu software remote desktop mahal, tidak perlu buka port, cukup Python dan koneksi internet.

Cocok untuk:
- 🏠 Kontrol PC rumah waktu kamu lagi di luar
- 🎵 Remote play musik / YouTube dari kasur
- 📁 Ambil file dari PC tanpa harus duduk di depan komputer
- 👨‍💻 Automation & scripting dari mana saja

---

## ✨ Fitur

| Kategori | Fitur |
|---|---|
| 🌐 **Browser** | Buka YouTube + skip iklan otomatis, Google search, buka URL sembarang |
| 🎵 **Spotify** | Auto-detect Spotify.exe, launch & search langsung |
| 💻 **CMD Manager** | Buka CMD dengan tema warna, inject perintah ke tab tertentu |
| 🪟 **Window Manager** | List, tutup window yang dibuka bot secara remote |
| 📸 **Screenshot** | Ambil screenshot, simpan ke list, kirim ulang kapanpun |
| 📡 **Live Screen** | Stream layar PC ke Telegram tiap 2.5 detik |
| 📝 **Notepad** | Buka Notepad langsung atau dengan efek animasi mengetik |
| 📂 **File Manager** | Browse folder, baca isi file, download file ke Telegram |
| 🗣️ **Text-to-Speech** | Bicara lewat speaker PC |
| 🔊 **Audio Control** | Set volume, mute, unmute dari HP |

---

## ⚡ Quick Start

```bash
# 1. Clone repo
git clone https://github.com/WarrenKu/TeleDesk-Controller.git
cd TeleDesk-Controller

# 2. Install otomatis (double-click atau jalankan di CMD)
setup.bat

# 3. Isi token di bot_controller.py, lalu jalankan
python bot_controller.py
```

> Butuh Python 3.10+ — download di [python.org](https://www.python.org/downloads/)

---

## 🚀 Cara Install (Detail)

**Step 1 — Buat bot Telegram**

1. Buka [@BotFather](https://t.me/BotFather) di Telegram
2. Kirim `/newbot` → ikuti instruksi → copy **token**
3. Dapatkan **user ID** kamu dari [@userinfobot](https://t.me/userinfobot)

**Step 2 — Clone & install**

```bash
git clone https://github.com/WarrenKu/TeleDesk-Controller.git
cd TeleDesk-Controller
```

Jalankan `setup.bat` (double-click) — akan otomatis install semua dependencies dan browser Playwright.

Atau manual:
```bash
pip install -r requirements.txt
playwright install chromium
```

**Step 3 — Konfigurasi**

Buka `bot_controller.py`, edit baris ini:
```python
BOT_TOKEN = "1234567890:AAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
OWNER_ID  = 987654321
```

**Step 4 — Jalankan**
```bash
python bot_controller.py
```

Bot online! Ketik `.help` di Telegram untuk mulai.

---

## 📋 Daftar Perintah

### 🌐 Browser & Media
```
>run open youtube and play <judul>       Cari & putar di YouTube (skip iklan otomatis)
>run open spotify and play <judul>       Buka Spotify exe atau browser
>run search google <query>               Google search
>run open <url>                          Buka URL sembarang
```

### 💻 CMD Manager
```
>run open cmd <warna>                    Buka CMD dengan tema warna
>run open cmd blue and Hello Bro!        CMD biru + tampilkan teks
>run open cmd <tab#> and exec <cmd>      Inject perintah ke CMD tab ke-N
>run exec <perintah>                     Jalankan perintah, output ke Telegram
```

Warna tersedia: `black` `blue` `green` `cyan` `red` `magenta` `pink` `yellow` `white` `gray` `lightblue` `lightgreen` `lightcyan` `lightred` `orange` `purple`

### 🪟 Window Manager
```
.s                   List semua window yang dibuka bot
.s 2                 Tutup window nomor 2
.s all               Tutup semua window sekaligus
```

### 📸 Screenshot Manager
```
.ss                  Ambil screenshot + simpan ke list
.s sc                Lihat daftar semua screenshot
.s sc 1              Kirim ulang screenshot nomor 1
.s sc all            Hapus semua screenshot dari list
```

### 📂 File Manager
```
.seefile C:\Users\hp\Desktop     List isi folder
.seefile C:\file.txt             Baca isi file (maks 500KB)
.getfile C:\file.zip             Download file ke Telegram (maks 50MB)
```

### 📝 Notepad & TTS
```
.text Halo dunia!                Buka Notepad dengan teks
.text [20] Judul\nIsi teks       Notepad dengan ukuran font + baris baru
.textrun Halo!                   Notepad dengan efek animasi mengetik
.say Halo semuanya!              Text-to-Speech lewat speaker PC
```

### 🎵 Media & Audio
```
.play / .p           Play video/media
.vol 70              Set volume sistem ke 70%
.m                   Mute
.unm                 Unmute
```

### 📡 Live Screen
```
.live                Mulai stream layar ke Telegram (tiap 2.5 detik)
.stoplive            Hentikan live screen
```

### ℹ️ Lainnya
```
.status              Status bot, browser, live, window aktif
.lisensi             Info & credits
.help                Tampilkan semua perintah (dengan tombol)
```

---

## 📁 Struktur Project

```
TeleDesk-Controller/
├── bot_controller.py    # Source utama
├── requirements.txt     # Daftar dependencies
├── setup.bat            # Auto-installer Windows
├── .gitignore
└── README.md
```

---

## 🔒 Keamanan

- Bot **hanya merespons** dari `OWNER_ID` yang kamu set sendiri
- Tidak ada data yang dikirim ke pihak ketiga
- Semua aksi berjalan **lokal di PC kamu**
- **Jangan commit token** ke repo — simpan di `.env` atau environment variable

---

## 🛠️ Tech Stack

| Library | Fungsi |
|---|---|
| [python-telegram-bot](https://python-telegram-bot.org/) | Telegram Bot API |
| [Playwright](https://playwright.dev/python/) | Browser automation |
| [pycaw](https://github.com/AndreMiras/pycaw) | Windows audio control |
| [pygetwindow](https://github.com/asweigart/PyGetWindow) | Window manager |
| [pyautogui](https://pyautogui.readthedocs.io/) | GUI automation |
| [psutil](https://psutil.readthedocs.io/) | Process & system |
| [pyttsx3](https://pyttsx3.readthedocs.io/) | Text-to-Speech |
| [Pillow](https://pillow.readthedocs.io/) | Image processing |

---

## ❓ FAQ

**Q: Apakah ini aman?**
Bot hanya bisa dikontrol oleh kamu sendiri lewat `OWNER_ID`. Tidak ada backdoor, tidak ada data yang dikirim ke mana pun.

**Q: Kenapa harus Windows?**
Beberapa fitur seperti audio control (pycaw) dan window manager (pygetwindow) hanya support Windows. Browser automation dan fitur lain bisa jalan di OS lain dengan modifikasi.

**Q: Apakah perlu Chrome terinstall?**
Tidak wajib — kalau Chrome tidak ditemukan, bot otomatis pakai Chromium bawaan Playwright.

**Q: Spotify tidak terbuka?**
Bot akan cari Spotify.exe di beberapa lokasi umum. Kalau tidak ketemu, otomatis buka di browser. Pastikan Spotify sudah terinstall di lokasi default.

**Q: Bot tidak merespons perintah?**
Pastikan `OWNER_ID` sudah diisi dengan benar. Cek dengan kirim pesan apapun dan lihat log di terminal.

---

## 📝 Changelog

### v3.2 — Latest
- ✅ Skip iklan YouTube otomatis (deteksi JS akurat)
- ✅ `.textrun` — efek animasi mengetik di Notepad
- ✅ `.seefile` support list folder + baca file
- ✅ `.getfile` download file langsung ke Telegram
- ✅ `.s sc` screenshot manager
- ✅ Inline keyboard tombol `.help` & GitHub di setiap pesan
- ✅ Spotify auto-detect exe

### v3.1
- ✅ Fix skip iklan tidak loop
- ✅ Window manager `.s`
- ✅ Live screen `.live`

### v3.0
- ✅ Initial release

---

## 📄 Lisensi

Project ini dibuat untuk keperluan **personal & testing**.

```
Ini bukan virus atau remote malware.
Hanya owner yang bisa mengontrol bot ini.
Gunakan dengan bijak dan bertanggung jawab.
```

---

<div align="center">

Made with ❤️ by **[Warren](https://github.com/WarrenKu)** & **Claude (Anthropic AI)**

⭐ *Kalau project ini bermanfaat, kasih star ya!*

</div>
