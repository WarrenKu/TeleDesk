<div align="center">

# 🤖 TeleDesk Controller

**Kendalikan PC kamu dari mana saja — lewat Telegram.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Browser-45BA4B?style=for-the-badge&logo=playwright&logoColor=white)

> *Remote desktop control via Telegram — buka browser, putar musik, ambil screenshot, baca file, semua dari HP kamu.*

</div>

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

## 🚀 Cara Install

**1. Clone repo**
```bash
git clone https://github.com/WarrenKu/TeleDesk-Controller.git
cd TeleDesk-Controller
```

**2. Install dependencies**
```bash
pip install python-telegram-bot playwright pycaw comtypes pyautogui Pillow requests pyttsx3 pygetwindow psutil pyperclip
```

**3. Install browser Playwright**
```bash
playwright install chromium
```

**4. Konfigurasi token**

Buka `bot_controller.py`, isi bagian ini:
```python
BOT_TOKEN = "token_bot_telegram_kamu"
OWNER_ID  = 123456789  # user ID Telegram kamu
```

> Dapatkan token dari [@BotFather](https://t.me/BotFather) dan user ID dari [@userinfobot](https://t.me/userinfobot)

**5. Jalankan**
```bash
python bot_controller.py
```

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

Warna yang tersedia: `black` `blue` `green` `cyan` `red` `magenta` `pink` `yellow` `white` `gray` `lightblue` `lightgreen` `lightcyan` `lightred` `orange` `purple`

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
.live                Mulai kirim screenshot tiap 2.5 detik
.stoplive            Hentikan live screen
```

### ℹ️ Lainnya
```
.status              Status bot, browser, live, window aktif
.lisensi             Info & credits
.help                Tampilkan semua perintah
```

---

## 🔒 Keamanan

- Bot **hanya merespons** dari `OWNER_ID` yang kamu set — orang lain tidak bisa kontrol
- Tidak ada data yang dikirim ke pihak ketiga
- Semua aksi berjalan **lokal di PC kamu**
- Token bot **jangan di-commit** ke repo — pakai `.env` atau environment variable

---

## 🛠️ Tech Stack

- **[python-telegram-bot](https://python-telegram-bot.org/)** — Telegram Bot API
- **[Playwright](https://playwright.dev/python/)** — Browser automation
- **[pycaw](https://github.com/AndreMiras/pycaw)** — Windows audio control
- **[pygetwindow](https://github.com/asweigart/PyGetWindow)** — Window manager
- **[pyautogui](https://pyautogui.readthedocs.io/)** — GUI automation
- **[psutil](https://psutil.readthedocs.io/)** — Process & system utilities
- **[pyttsx3](https://pyttsx3.readthedocs.io/)** — Text-to-Speech

---

## 📄 Lisensi

Project ini dibuat untuk keperluan **personal & testing**.

> Ini bukan virus atau remote malware.
> Hanya owner yang bisa mengontrol bot ini.

---

<div align="center">

Made with ❤️ by **Warren** & **Claude (Anthropic AI)**

⭐ *Star repo ini kalau bermanfaat!*

</div>
