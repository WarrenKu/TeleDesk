@echo off
title TeleDesk-Controller - Setup
color 0B

echo.
echo  ████████╗███████╗██╗     ███████╗██████╗ ███████╗███████╗██╗  ██╗
echo  ╚══██╔══╝██╔════╝██║     ██╔════╝██╔══██╗██╔════╝██╔════╝██║ ██╔╝
echo     ██║   █████╗  ██║     █████╗  ██║  ██║█████╗  ███████╗█████╔╝
echo     ██║   ██╔══╝  ██║     ██╔══╝  ██║  ██║██╔══╝  ╚════██║██╔═██╗
echo     ██║   ███████╗███████╗███████╗██████╔╝███████╗███████║██║  ██╗
echo     ╚═╝   ╚══════╝╚══════╝╚══════╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝
echo.
echo              Desktop Controller via Telegram
echo              by Warren ^& Claude (Anthropic)
echo.
echo ============================================================

:: Cek Python
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [ERROR] Python tidak ditemukan!
    echo  Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo  [1/3] Install Python packages dari requirements.txt ...
echo ------------------------------------------------------------
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo  [ERROR] Gagal install. Coba jalankan sebagai Administrator.
    pause
    exit /b 1
)

echo.
echo  [2/3] Install Playwright Chromium...
echo ------------------------------------------------------------
playwright install chromium
if errorlevel 1 (
    python -m playwright install chromium
)

echo.
echo ============================================================
echo  [3/3] Setup selesai!
echo ============================================================
echo.
echo  Langkah selanjutnya:
echo  1. Buka bot_controller.py
echo  2. Isi BOT_TOKEN  = "token dari @BotFather"
echo  3. Isi OWNER_ID   = user ID kamu (dari @userinfobot)
echo  4. Jalankan: python bot_controller.py
echo.
echo  Ketik .help di Telegram setelah bot online.
echo ============================================================
echo.
pause
