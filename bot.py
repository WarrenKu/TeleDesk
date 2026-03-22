"""
╔══════════════════════════════════════════════════════════════╗
║         BOT TELEGRAM - DESKTOP CONTROLLER v3.2              ║
║         Created by Claude (Anthropic) & Warren              ║
║         github.com/WarrenKu                                 ║
╚══════════════════════════════════════════════════════════════╝

SEMUA PERINTAH:
  >run open youtube and play <judul>
  >run search google <query>
  >run open <url>
  >run open spotify and play <judul>
  >run exec <perintah>
  >run open cmd <warna> and <teks>
  >run open cmd <tab#> and exec <cmd>
  .s / .s <nomor> / .s all
  .s sc / .s sc <nomor> / .s sc all
  .seefile <path>   .getfile <path>
  .play/.p  .vol  .m  .unm
  .ss  .live  .stoplive
  .say <teks>
  .text [size] <teks>
  .textrun [size] <teks>
  .lisensi  .status  .help

Requirements:
  pip install python-telegram-bot playwright pycaw comtypes pyautogui
              Pillow requests pyttsx3 pygetwindow psutil pyperclip
  playwright install chromium
"""

import asyncio
import io
import logging
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import urllib.request
import webbrowser
from datetime import datetime
from io import BytesIO
from pathlib import Path

import psutil
import pyautogui
import requests
from PIL import Image, ImageGrab, ImageTk, ImageSequence
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler,
    MessageHandler, filters, ContextTypes,
)

try:
    import pygetwindow as gw
    HAS_GW = True
except Exception:
    HAS_GW = False

# ══════════════════════════════════════════════
#  KONFIGURASI
# ══════════════════════════════════════════════
BOT_TOKEN = os.getenv("BOT_TOKEN", "ISI_TOKEN_BARU_KAMU_DISINI")
OWNER_ID  = int(os.getenv("OWNER_ID", "TOKEN_ID_OWNER"))

SPOTIFY_PATHS = [
    os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\Spotify.exe"),
    r"C:\Program Files\Spotify\Spotify.exe",
    r"C:\Program Files (x86)\Spotify\Spotify.exe",
]


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ── State global ──────────────────────────────
browser_instance  = None
page_instance     = None
playwright_ctx    = None
live_running      = False
bot_global: Bot   = None
_skip_in_progress = False

opened_windows:  list = []
screenshot_list: list = []

CMD_COLORS = {
    "black":"00","blue":"01","green":"02","cyan":"03",
    "red":"04","magenta":"05","pink":"05","yellow":"06",
    "white":"07","gray":"08","grey":"08",
    "lightblue":"09","lightgreen":"0A","lightcyan":"0B",
    "lightred":"0C","lightmagenta":"0D","lightpink":"0D",
    "lightyellow":"0E","brightwhite":"0F",
    "orange":"06","purple":"05",
}


# ══════════════════════════════════════════════
#  LOG REALTIME → TELEGRAM
# ══════════════════════════════════════════════
async def tlog(msg: str):
    try:
        now = datetime.now().strftime("%H:%M:%S")
        await bot_global.send_message(
            chat_id=OWNER_ID,
            text=f"🖥 `[{now}]` {msg}",
            parse_mode="Markdown",
        )
    except Exception as e:
        log.error(f"tlog: {e}")


# ══════════════════════════════════════════════
#  VOLUME CONTROL
# ══════════════════════════════════════════════
def set_volume(level: int):
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        iface   = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        vol     = cast(iface, POINTER(IAudioEndpointVolume))
        vol.SetMasterVolumeLevelScalar(max(0.0, min(1.0, level / 100)), None)
        return True, f"🔊 Volume → {level}%"
    except Exception as e:
        try:
            subprocess.run(["nircmd","setsysvolume",str(int(level*655.35))],capture_output=True)
            return True, f"🔊 Volume → {level}%"
        except Exception:
            return False, f"❌ Volume gagal: {e}"


def mute_system(mute: bool):
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        iface   = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        vol     = cast(iface, POINTER(IAudioEndpointVolume))
        vol.SetMute(1 if mute else 0, None)
        return True, "🔇 Muted" if mute else "🔊 Unmuted"
    except Exception as e:
        return False, f"❌ Mute error: {e}"


# ══════════════════════════════════════════════
#  TEXT-TO-SPEECH
# ══════════════════════════════════════════════
def speak(text: str):
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 155)
        engine.say(text)
        engine.runAndWait()
        return True, f"🗣 Berkata: {text}"
    except Exception:
        try:
            ps = (
                f'Add-Type -AssemblyName System.Speech;'
                f'$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;'
                f'$s.Speak("{text}")'
            )
            subprocess.Popen(["powershell", "-Command", ps])
            return True, f"🗣 Berkata: {text}"
        except Exception as e2:
            return False, f"❌ TTS error: {e2}"


# ══════════════════════════════════════════════
#  NOTEPAD — .text (langsung)
# ══════════════════════════════════════════════
def _set_notepad_font(font_size: int):
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Notepad", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "lfHeight", 0, winreg.REG_DWORD, -(font_size + 5))
        winreg.CloseKey(key)
    except Exception:
        pass


def open_notepad(content: str, font_size: int = 14):
    content = content.replace("\\n", "\n").replace("/n", "\n")
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
    tmp.write(content)
    tmp.close()
    _set_notepad_font(font_size)
    proc = subprocess.Popen(["notepad.exe", tmp.name])
    opened_windows.append({"title":"Notepad","pid":proc.pid,"type":"notepad","path":tmp.name})
    return True, f"📝 Notepad dibuka (font ~{font_size}px)"


# ══════════════════════════════════════════════
#  TEXTRUN — .textrun (animasi mengetik)
# ══════════════════════════════════════════════
def open_notepad_typewriter(content: str, font_size: int = 14, delay: float = 0.05):
    """
    Buka Notepad kosong lalu simulate ketik karakter per karakter.
    Efek typewriter / animasi ngetik pakai pyautogui.
    """
    content = content.replace("\\n", "\n").replace("/n", "\n")
    _set_notepad_font(font_size)

    proc = subprocess.Popen(["notepad.exe"])
    opened_windows.append({"title":"Notepad","pid":proc.pid,"type":"notepad"})
    time.sleep(1.8)  # tunggu Notepad terbuka penuh

    # Fokus ke Notepad
    if HAS_GW:
        for title_kw in ["Untitled - Notepad", "Notepad", "Untitled"]:
            wins = gw.getWindowsWithTitle(title_kw)
            if wins:
                try:
                    wins[0].activate()
                    time.sleep(0.5)
                    break
                except Exception:
                    pass

    # Klik area teks
    pyautogui.click(pyautogui.size()[0]//2, pyautogui.size()[1]//2)
    time.sleep(0.2)

    # Ketik karakter per karakter
    for char in content:
        if char == "\n":
            pyautogui.press("enter")
        elif char == "\t":
            pyautogui.press("tab")
        elif ord(char) < 128:
            pyautogui.typewrite(char, interval=0)
        else:
            # Karakter unicode → clipboard paste
            try:
                import pyperclip
                pyperclip.copy(char)
                pyautogui.hotkey("ctrl", "v")
            except Exception:
                pass
        time.sleep(delay)

    return True, f"⌨️ Textrun selesai ({len(content)} karakter)"


def _fmt_size(size: int) -> str:
    for unit in ["B","KB","MB","GB"]:
        if size < 1024:
            return f"{size:.0f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def browse_path(path: str):
    p = Path(path.strip().strip('"'))
    if not p.exists():
        return False, f"❌ Path tidak ditemukan: `{path}`"
    if p.is_dir():
        items = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        if not items:
            return True, f"📂 *{p}*\n_Folder kosong_"
        lines = [f"📂 *{p}*\n"]
        for item in items[:50]:
            icon = "📁" if item.is_dir() else "📄"
            size = f" `({_fmt_size(item.stat().st_size)})`" if item.is_file() else ""
            lines.append(f"{icon} `{item.name}`{size}")
        if len(items) > 50:
            lines.append(f"\n_... dan {len(items)-50} item lagi_")
        return True, "\n".join(lines)
    if p.is_file():
        if p.stat().st_size > 500_000:
            return False, "❌ File terlalu besar (>500KB). Pakai `.getfile` untuk download."
        try:
            return True, p.read_text(encoding="utf-8", errors="replace")[:3000]
        except Exception as e:
            return False, f"❌ Gagal baca: {e}"
    return False, "❌ Path tidak dikenali"


def get_file_bytes(path: str):
    p = Path(path.strip().strip('"'))
    if not p.exists():
        return False, f"❌ File tidak ditemukan: `{path}`", ""
    if not p.is_file():
        return False, f"❌ Bukan file: `{path}`", ""
    if p.stat().st_size > 50_000_000:
        return False, "❌ File terlalu besar (>50MB)", ""
    try:
        return True, p.read_bytes(), p.name
    except Exception as e:
        return False, f"❌ Gagal baca: {e}", ""


# ══════════════════════════════════════════════
#  CMD WINDOW MANAGER
# ══════════════════════════════════════════════
def open_cmd(color_name: str = "white", message: str = ""):
    color_code = CMD_COLORS.get(color_name.lower(), "07")
    cmd_num    = len([w for w in opened_windows if w["type"] == "cmd"]) + 1
    label      = f"CMD-{cmd_num}"
    bat_lines  = [
        "@echo off", f"color {color_code}",
        f"title {label} [{color_name.upper()}] - Bot Controller",
    ]
    if message:
        bat_lines += ["echo.", f"echo  {message}", "echo."]
    bat_lines.append("cmd /k")
    bat_path = os.path.join(tempfile.gettempdir(), f"_bot_{label}.bat")
    with open(bat_path, "w") as f:
        f.write("\r\n".join(bat_lines))
    proc = subprocess.Popen(f'start "{label}" cmd /c "{bat_path}"', shell=True)
    opened_windows.append({"title":label,"pid":proc.pid,"type":"cmd",
                            "color":color_name,"bat":bat_path})
    return True, f"💻 `{label}` [#{len(opened_windows)}] — tema: *{color_name}*"


def exec_in_cmd_tab(tab_number: int, command: str):
    cmd_wins = [w for w in opened_windows if w["type"] == "cmd"]
    if not cmd_wins:
        return False, "❌ Tidak ada CMD window aktif"
    idx = tab_number - 1
    if idx < 0 or idx >= len(cmd_wins):
        return False, f"❌ Tab CMD {tab_number} tidak ada. Total: {len(cmd_wins)}"
    win_title = cmd_wins[idx]["title"]
    if HAS_GW:
        wins = gw.getWindowsWithTitle(win_title)
        if wins:
            try:
                wins[0].activate()
                time.sleep(0.5)
                pyautogui.typewrite(command, interval=0.04)
                pyautogui.press("enter")
                return True, f"✅ `{command}` → `{win_title}`"
            except Exception:
                pass
    ok, out = run_cmd_exec(command)
    return ok, out


def run_cmd_exec(command: str):
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True,
            text=True, timeout=20, encoding="utf-8", errors="replace",
        )
        out = (result.stdout or "") + (result.stderr or "")
        return True, out.strip()[:2000] or "(no output)"
    except subprocess.TimeoutExpired:
        return False, "❌ Timeout (>20 detik)"
    except Exception as e:
        return False, f"❌ Error: {e}"


# ══════════════════════════════════════════════
#  WINDOW LIST & CLOSE
# ══════════════════════════════════════════════
def list_opened_windows() -> str:
    if not opened_windows:
        return "📭 Tidak ada window yang dibuka bot"
    icons = {"cmd":"💻","notepad":"📝","browser":"🌐","spotify":"🎵"}
    lines = ["📋 *Window aktif:*\n"]
    for i, w in enumerate(opened_windows, 1):
        icon  = icons.get(w["type"], "🪟")
        color = f" `[{w['color']}]`" if w.get("color") else ""
        lines.append(f"`{i}.` {icon} `{w['title']}`{color}")
    lines.append("\n_`.s <nomor>` tutup · `.s all` tutup semua_")
    return "\n".join(lines)


def close_window_by_index(idx: int):
    if idx < 1 or idx > len(opened_windows):
        return False, f"❌ Nomor {idx} tidak valid"
    w = opened_windows[idx - 1]
    try:
        if HAS_GW:
            for win in gw.getWindowsWithTitle(w["title"]):
                try: win.close()
                except Exception: pass
        try:
            proc = psutil.Process(w["pid"])
            for c in proc.children(recursive=True): c.kill()
            proc.kill()
        except Exception:
            pass
        title = w["title"]
        opened_windows.pop(idx - 1)
        return True, f"✅ `{title}` ditutup"
    except Exception as e:
        return False, f"❌ Gagal: {e}"


def close_all_windows() -> str:
    if not opened_windows:
        return "📭 Tidak ada window"
    count = len(opened_windows)
    for w in opened_windows[:]:
        try:
            if HAS_GW:
                for win in gw.getWindowsWithTitle(w["title"]):
                    try: win.close()
                    except Exception: pass
            try:
                proc = psutil.Process(w["pid"])
                for c in proc.children(recursive=True): c.kill()
                proc.kill()
            except Exception: pass
        except Exception: pass
    opened_windows.clear()
    return f"✅ {count} window ditutup semua"


# ══════════════════════════════════════════════
#  SPOTIFY
# ══════════════════════════════════════════════
def find_spotify_exe():
    for path in SPOTIFY_PATHS:
        if os.path.exists(path):
            return path
    try:
        r = subprocess.run(["where","spotify"],capture_output=True,text=True)
        if r.returncode == 0:
            return r.stdout.strip().split("\n")[0]
    except Exception:
        pass
    return None


async def open_spotify(query: str = ""):
    exe = find_spotify_exe()
    if exe:
        await tlog(f"🎵 Spotify.exe: `{exe}`")
        running = any("spotify" in p.name().lower()
                      for p in psutil.process_iter(["name"]))
        if not running:
            proc = subprocess.Popen([exe])
            opened_windows.append({"title":"Spotify","pid":proc.pid,"type":"spotify"})
            await tlog("🎵 Spotify diluncurkan...")
            await asyncio.sleep(5)
        if query:
            try:
                os.startfile(f"spotify:search:{requests.utils.quote(query)}")
                await tlog(f"🔍 Spotify search: *{query}*")
            except Exception:
                pass
        return True, "✅ Spotify dibuka"
    else:
        await tlog("⚠️ Spotify.exe tidak ditemukan → browser")
        url = (f"https://open.spotify.com/search/{requests.utils.quote(query)}"
               if query else "https://open.spotify.com")
        webbrowser.open(url)
        return False, "⚠️ Spotify tidak terinstall, dibuka di browser"


# ══════════════════════════════════════════════
#  BROWSER — PLAYWRIGHT
# ══════════════════════════════════════════════
async def get_browser():
    global browser_instance, page_instance, playwright_ctx
    if browser_instance and page_instance:
        try:
            await page_instance.title()
            return browser_instance, page_instance
        except Exception:
            pass

    await tlog("🌐 Membuka browser...")
    from playwright.async_api import async_playwright
    playwright_ctx = await async_playwright().start()

    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    chrome_exe = next((p for p in chrome_paths if os.path.exists(p)), None)
    kwargs = dict(headless=False, args=["--start-maximized"])
    if chrome_exe:
        kwargs["executable_path"] = chrome_exe
        await tlog(f"✅ Chrome: `{chrome_exe}`")
    else:
        await tlog("⚠️ Pakai Chromium Playwright")

    browser_instance = await playwright_ctx.chromium.launch(**kwargs)
    context          = await browser_instance.new_context(no_viewport=True)
    page_instance    = await context.new_page()
    opened_windows.append({"title":"Browser","pid":0,"type":"browser"})
    await tlog("✅ Browser siap")
    return browser_instance, page_instance


async def close_browser():
    global browser_instance, page_instance, playwright_ctx
    try:
        if browser_instance: await browser_instance.close()
        if playwright_ctx:   await playwright_ctx.stop()
    except Exception:
        pass
    browser_instance = None
    page_instance    = None
    playwright_ctx   = None
    for i, w in enumerate(opened_windows):
        if w["type"] == "browser":
            opened_windows.pop(i)
            break


# ══════════════════════════════════════════════
#  SKIP IKLAN YOUTUBE
# ══════════════════════════════════════════════
async def _get_page_status(page) -> dict:
    try:
        return await page.evaluate("""
            (() => {
                const vid = document.querySelector('video');
                const s1 = document.body.classList.contains('ad-showing');
                const s2 = !!document.querySelector('.ytp-ad-duration-remaining');
                const s3 = !!document.querySelector('.ytp-ad-player-overlay-instream-info');
                const s4 = !!document.querySelector('.ytp-ad-module');
                const canSkip = !!(
                    document.querySelector('button.ytp-skip-ad-button') ||
                    document.querySelector('.ytp-ad-skip-button') ||
                    document.querySelector('.ytp-skip-intro-button')
                );
                return {
                    adScore:   [s1,s2,s3,s4].filter(Boolean).length,
                    canSkip:   canSkip,
                    vidPaused: vid ? vid.paused : true,
                    vidTime:   vid ? vid.currentTime : 0,
                };
            })()
        """)
    except Exception:
        return {"adScore": 0, "canSkip": False, "vidPaused": True, "vidTime": 0}


async def _ensure_playing(page):
    try:
        resumed = await page.evaluate("""
            (() => {
                const v = document.querySelector('video');
                if (v && v.paused && !v.ended) { v.play(); return true; }
                return false;
            })()
        """)
        if resumed:
            await asyncio.sleep(0.8)
            return
    except Exception:
        pass
    try:
        pb = page.locator("button.ytp-play-button")
        await pb.wait_for(state="visible", timeout=3000)
        if "Play" in (await pb.get_attribute("aria-label") or ""):
            await pb.click()
    except Exception:
        pass


async def skip_yt_ad(page):
    """
    1. Cek status iklan+video via JS.
    2. Tombol Skip ada  -> klik -> pastikan video play.
    3. Iklan main, belum bisa skip -> tunggu, watcher cek lagi 2 detik.
    4. Tidak ada iklan, video pause -> langsung play.
    """
    global _skip_in_progress
    if not page or page.is_closed() or _skip_in_progress:
        return
    try:
        st = await _get_page_status(page)

        if st["canSkip"]:
            _skip_in_progress = True
            try:
                btn = page.locator(
                    "button.ytp-skip-ad-button, .ytp-ad-skip-button, .ytp-skip-intro-button"
                )
                await btn.first.click()
                await tlog("⏭ Skip Ad diklik")
                await asyncio.sleep(1.5)
                await _ensure_playing(page)
            finally:
                await asyncio.sleep(5)
                _skip_in_progress = False
            return

        if st["adScore"] >= 2:
            return  # iklan main, belum bisa skip, tunggu saja

        if st["vidPaused"] and "youtube.com" in page.url:
            await _ensure_playing(page)

    except Exception:
        pass


async def watch_and_skip_ads(page):
    """Background loop cek tiap 2 detik."""
    while True:
        try:
            if not page or page.is_closed():
                break
            await skip_yt_ad(page)
        except Exception:
            break
        await asyncio.sleep(2)

# ══════════════════════════════════════════════
#  COMMAND PARSER — >run
# ══════════════════════════════════════════════
async def run_ai_command(command: str):
    cmd_lower = command.lower().strip()
    cmd_orig  = command.strip()

    tab_exec = re.search(r"open\s+cmd\s+(\d+)\s+and\s+exec\s+(.+)$", cmd_lower)
    if tab_exec:
        tab_n, cmd_run = int(tab_exec.group(1)), tab_exec.group(2).strip()
        await tlog(f"💻 Inject CMD tab {tab_n}: `{cmd_run}`")
        ok, result = exec_in_cmd_tab(tab_n, cmd_run)
        await tlog(result); return result

    cmd_open = re.search(r"open\s+cmd\s*([a-z]*)\s*(?:and\s+(.+))?$", cmd_lower)
    if cmd_open:
        color  = cmd_open.group(1).strip() or "white"
        orig_m = re.search(r"open\s+cmd\s*[a-zA-Z]*\s*(?:and\s+(.+))?$",
                           cmd_orig, re.IGNORECASE)
        msg    = (orig_m.group(1).strip() if orig_m and orig_m.group(1) else "") or ""
        await tlog(f"💻 CMD tema *{color}*" + (f" → `{msg}`" if msg else ""))
        ok, result = open_cmd(color, msg)
        await tlog(result); return result

    exec_m = re.search(r"(?:exec|jalankan|cmd run)\s+(.+)$", cmd_lower)
    if exec_m:
        cmd_run = exec_m.group(1).strip()
        await tlog(f"⚙️ Exec: `{cmd_run}`")
        ok, output = run_cmd_exec(cmd_run)
        result = f"```\n{output}\n```"
        await tlog(f"📤 Output:\n{result}"); return result

    if "spotify" in cmd_lower:
        query = re.sub(r"(?:open spotify and play|spotify play|play on spotify|spotify)\s*",
                       "", cmd_lower).strip()
        await tlog(f"🎵 Spotify: *{query or '(home)'}*")
        ok, result = await open_spotify(query); return result

    yt_m = re.search(
        r"(?:open youtube and play|play on youtube|youtube play|putar di youtube)"
        r"\s+[\"']?(.+?)[\"']?\s*$", cmd_lower,
    )
    query_yt = yt_m.group(1) if yt_m else None
    if query_yt is None and "youtube" in cmd_lower and ("play" in cmd_lower or "putar" in cmd_lower):
        query_yt = re.sub(r"(?:open youtube and play|youtube|play|putar|cari)\s*",
                          "", cmd_lower).strip().strip("\"'")

    if query_yt:
        await tlog(f"🎯 YouTube: *{query_yt}*")
        _, page = await get_browser()
        await tlog("🔗 Membuka YouTube...")
        await page.goto("https://www.youtube.com", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        try:
            btn = page.locator(
                "button:has-text('Reject all'), button:has-text('Accept all'), "
                "button:has-text('Tolak semua'), button:has-text('I agree')"
            )
            if await btn.count() > 0:
                await btn.first.click(); await asyncio.sleep(1)
        except Exception:
            pass

        await tlog(f"🔍 Mencari: *{query_yt}*")
        search_box = None
        for sel in ["input#search","input[name='search_query']","ytd-searchbox input",
                    "input[placeholder*='Search']","input[aria-label*='Search']"]:
            try:
                loc = page.locator(sel)
                await loc.wait_for(state="visible", timeout=5000)
                search_box = loc; break
            except Exception:
                continue

        if not search_box:
            await page.goto(
                f"https://www.youtube.com/results?search_query={requests.utils.quote(query_yt)}",
                wait_until="domcontentloaded")
            await asyncio.sleep(3)
        else:
            await search_box.click(); await asyncio.sleep(0.3)
            await search_box.fill(query_yt); await asyncio.sleep(0.3)
            await page.keyboard.press("Enter"); await asyncio.sleep(3)

        await tlog("🎵 Pilih video pertama...")
        first_video = None
        for sel in ["ytd-video-renderer a#video-title","a#video-title","ytd-video-renderer h3 a"]:
            try:
                loc = page.locator(sel).first
                await loc.wait_for(state="visible", timeout=5000)
                first_video = loc; break
            except Exception:
                continue

        if not first_video:
            await tlog("❌ Video tidak ditemukan"); return "❌ Video tidak ditemukan"

        video_title = await first_video.get_attribute("title") or "Unknown"
        await first_video.click(); await asyncio.sleep(3)
        asyncio.ensure_future(watch_and_skip_ads(page))
        try:
            pb = page.locator("button.ytp-play-button")
            await pb.wait_for(state="visible", timeout=5000)
            if "Play" in (await pb.get_attribute("aria-label") or ""):
                await pb.click()
        except Exception:
            pass
        await tlog(f"▶️ Memutar: *{video_title}*")
        return f"▶️ Memutar: *{video_title}*"

    gm = re.search(r"(?:search google|google|cari)\s+[\"']?(.+?)[\"']?\s*$", cmd_lower)
    if gm:
        q = gm.group(1).strip()
        await tlog(f"🔍 Google: *{q}*")
        _, page = await get_browser()
        await page.goto(f"https://www.google.com/search?q={requests.utils.quote(q)}")
        await tlog("✅ Google selesai"); return f"✅ Google: {q}"

    um = re.search(r"(?:open|buka|goto|ke)\s+(https?://\S+|www\.\S+|\S+\.\S+)", cmd_lower)
    if um:
        url = um.group(1)
        if not url.startswith("http"): url = "https://" + url
        await tlog(f"🌐 Membuka: {url}")
        _, page = await get_browser()
        await page.goto(url, wait_until="domcontentloaded")
        await tlog(f"✅ Terbuka: {url}"); return f"✅ Terbuka: {url}"

    await tlog(f"❓ Tidak dikenali: `{command}`")
    return "❓ Tidak dikenali. Ketik `.help` untuk daftar perintah."


# ══════════════════════════════════════════════
#  LIVE SCREEN
# ══════════════════════════════════════════════
async def live_screen_loop():
    global live_running
    await tlog("📡 *Live screen dimulai!* Ketik `.stoplive` untuk berhenti.")
    while live_running:
        try:
            img = ImageGrab.grab()
            img = img.resize((1280, 720))
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=55)
            buf.seek(0)
            await bot_global.send_photo(
                chat_id=OWNER_ID, photo=buf,
                caption=f"📡 `{datetime.now().strftime('%H:%M:%S')}`",
                parse_mode="Markdown",
            )
        except Exception as e:
            log.error(f"live: {e}")
        await asyncio.sleep(2.5)
    await tlog("📡 Live dihentikan.")


# ══════════════════════════════════════════════
#  TEKS HELP & LISENSI
# ══════════════════════════════════════════════
HELP_TEXT = """
╔══════════════════════════════════╗
║  🤖  BOT CONTROLLER  v3.2  🤖   ║
╚══════════════════════════════════╝

🌐 *BROWSER*
`>run open youtube and play <judul>`
`>run search google <query>`
`>run open <url>`
`>run open spotify and play <judul>`

💻 *CMD MANAGER*
`>run open cmd <warna> and <teks>`
`>run open cmd blue and Hello Bro!`
`>run open cmd red`
`>run open cmd <tab#> and exec <cmd>`
`>run exec <perintah>`

🪟 *WINDOW MANAGER*
`.s` — list window  `.s 2` — tutup #2
`.s all` — tutup semua

📸 *SCREENSHOT*
`.ss` — ambil + simpan
`.s sc` — list  `.s sc 1` — kirim ulang
`.s sc all` — hapus semua

📂 *FILE MANAGER*
`.seefile C:\\Users\\hp\\Desktop` — list folder
`.seefile C:\\file.txt` — baca file
`.getfile C:\\file.txt` — download

🗣 *SUARA*
`.say Halo semuanya!`

📝 *NOTEPAD*
`.text Halo!`
`.text [20] Besar\\nBaris 2`
`.textrun Halo!` — animasi ngetik
`.textrun [16] Teks\\nBaris 2` — animasi + size

🎵 *MEDIA*
`.play` / `.p`  `.vol 70`  `.m`  `.unm`

📡 *LAYAR*
`.ss`  `.live`  `.stoplive`

ℹ️ *INFO*
`.status`  `.lisensi`  `.help`
"""

LISENSI_NOTE = (
    "╔══════════════════════════════════════╗\n"
    "║        BOT CONTROLLER v3.2           ║\n"
    "╚══════════════════════════════════════╝\n\n"
    "Create by Claude (Anthropic AI) and Warren\n\n"
    "Ini bukan virus atau remote malware.\n"
    "Hanya untuk keperluan testing & personal.\n\n"
    "GitHub  : github.com/WarrenKu\n"
    "Powered : Python + Playwright + PTB\n\n"
    "=== Keamanan ===\n"
    "- Hanya owner (OWNER_ID) yang bisa kontrol\n"
    "- Tidak ada data dikirim ke pihak ketiga\n"
    "- Semua aksi berjalan lokal di PC ini\n\n"
    "=== Special Thanks ===\n"
    "- Anthropic Claude  — AI Brain\n"
    "- python-telegram-bot — Telegram API\n"
    "- Playwright        — Browser Automation\n"
    "- pycaw             — Windows Audio Control\n"
    "- pygetwindow       — Window Manager\n"
    "- psutil            — Process Manager\n"
)

LISENSI_TG = """
🔐 *Lisensi & Info*

✨ *Dibuat oleh:*
Claude (Anthropic AI) & Warren

🔗 *GitHub:* [github.com/WarrenKu](https://github.com/WarrenKu)

⚠️ *Disclaimer:*
• Ini BUKAN virus atau remote malware
• Hanya untuk testing & personal use
• Hanya owner yang bisa kontrol bot

🛡️ *Keamanan:*
• Hanya respons dari `OWNER_ID` kamu
• Tidak ada data dikirim ke pihak ketiga
• Semua berjalan lokal di PC

💙 *Powered by:*
Python • Playwright • python-telegram-bot
pycaw • pygetwindow • psutil
"""


# ══════════════════════════════════════════════
#  INLINE KEYBOARD
# ══════════════════════════════════════════════
def make_help_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 .help",  callback_data="cmd:.help"),
            InlineKeyboardButton("🔗 GitHub", url="https://github.com/WarrenKu"),
        ]
    ])


# ══════════════════════════════════════════════
#  TELEGRAM HANDLERS
# ══════════════════════════════════════════════
def is_owner(update: Update) -> bool:
    u = getattr(update, "effective_user", None) or getattr(
        update.callback_query, "from_user", None)
    return u is not None and u.id == OWNER_ID


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_owner(update):
        return
    if query.data == "cmd:.help":
        await query.message.reply_text(HELP_TEXT, parse_mode="Markdown",
                                       reply_markup=make_help_keyboard())


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global live_running
    if not is_owner(update):
        return

    text = update.message.text.strip()
    msg  = update.message
    low  = text.lower()

    # ── >run ──────────────────────────────────────────────────
    if low.startswith(">run "):
        command = text[5:].strip()
        await msg.reply_text(f"⚙️ `{command}`", parse_mode="Markdown")
        try:
            result = await run_ai_command(command)
            await msg.reply_text(result, parse_mode="Markdown")
        except Exception as e:
            await tlog(f"❌ Error:\n```{traceback.format_exc()[-500:]}```")
            await msg.reply_text(f"❌ Error: {e}")
        return

    # ── .say ──────────────────────────────────────────────────
    if low.startswith(".say "):
        say_text = text[5:].strip()
        if not say_text:
            await msg.reply_text("Usage: `.say Halo!`", parse_mode="Markdown"); return
        await tlog(f"🗣 TTS: *{say_text}*")
        ok, result = await asyncio.get_event_loop().run_in_executor(None, speak, say_text)
        await msg.reply_text(result)
        return

    # ── .text ─────────────────────────────────────────────────
    if low.startswith(".text") and not low.startswith(".textrun"):
        rest = text[5:].strip()
        font_size = 14
        fm = re.match(r"^\[(\d+)\]\s*(.+)$", rest, re.DOTALL)
        if fm:
            font_size = int(fm.group(1)); content = fm.group(2)
        else:
            content = rest
        if not content:
            await msg.reply_text("Usage: `.text Halo!` atau `.text [18] Besar`",
                                 parse_mode="Markdown"); return
        await tlog(f"📝 Notepad (font {font_size})")
        ok, result = open_notepad(content, font_size)
        await msg.reply_text(result)
        return

    # ── .textrun ──────────────────────────────────────────────
    if low.startswith(".textrun"):
        rest = text[8:].strip()
        font_size = 14
        delay = 0.05
        fm = re.match(r"^\[(\d+)\]\s*(.+)$", rest, re.DOTALL)
        if fm:
            font_size = int(fm.group(1)); content = fm.group(2)
        else:
            content = rest
        if not content:
            await msg.reply_text(
                "Usage: `.textrun Halo!` atau `.textrun [16] Teks\\nBaris 2`",
                parse_mode="Markdown"); return
        await tlog(f"⌨️ Textrun (font {font_size}, delay {delay}s)")
        await msg.reply_text(f"⌨️ Mengetik animasi... ({len(content)} karakter)")
        # Jalankan di thread agar tidak block
        await asyncio.get_event_loop().run_in_executor(
            None, open_notepad_typewriter, content, font_size, delay
        )
        await tlog("⌨️ Textrun selesai")
        return

    # ── .seefile ──────────────────────────────────────────────
    if low.startswith(".seefile"):
        path = text[8:].strip()
        if not path:
            await msg.reply_text(
                "Usage:\n`.seefile C:\\Users\\hp\\Desktop` — folder\n"
                "`.seefile C:\\file.txt` — isi file",
                parse_mode="Markdown"); return
        await tlog(f"📂 Browse: `{path}`")
        ok, content = browse_path(path)
        if ok:
            if len(content) > 3500:
                buf = BytesIO(content.encode("utf-8")); buf.name = "result.txt"
                await msg.reply_document(document=buf, caption=f"📂 `{path}`",
                                         parse_mode="Markdown")
            else:
                await msg.reply_text(content, parse_mode="Markdown")
        else:
            await msg.reply_text(content, parse_mode="Markdown")
        return

    # ── .getfile ──────────────────────────────────────────────
    if low.startswith(".getfile"):
        path = text[8:].strip()
        if not path:
            await msg.reply_text("Usage: `.getfile C:\\path\\to\\file`",
                                 parse_mode="Markdown"); return
        await tlog(f"📥 Download: `{path}`")
        ok, data, fname = get_file_bytes(path)
        if ok:
            buf = BytesIO(data); buf.name = fname
            await msg.reply_document(document=buf, caption=f"📥 `{fname}`",
                                     parse_mode="Markdown")
            await tlog(f"✅ `{fname}` terkirim")
        else:
            await msg.reply_text(data, parse_mode="Markdown")
        return

    # ── .vol ──────────────────────────────────────────────────
    if low.startswith(".vol"):
        parts = text.split()
        if len(parts) < 2 or not parts[1].isdigit():
            await msg.reply_text("Usage: `.vol 50` (0–100)", parse_mode="Markdown"); return
        level = max(0, min(100, int(parts[1])))
        ok, result = set_volume(level)
        await tlog(result); await msg.reply_text(result)
        return

    if low == ".m":
        ok, result = mute_system(True)
        await tlog(result); await msg.reply_text(result); return

    if low == ".unm":
        ok, result = mute_system(False)
        await tlog(result); await msg.reply_text(result); return

    if low in (".play", ".p"):
        await tlog("▶️ Play...")
        try:
            if page_instance:
                await page_instance.evaluate("document.querySelector('video')?.play()")
                await msg.reply_text("▶️ Play!")
            else:
                pyautogui.press("playpause")
                await msg.reply_text("▶️ Media key dikirim")
        except Exception as e:
            await msg.reply_text(f"❌ {e}")
        return

    # ── .s window manager ─────────────────────────────────────
    if low == ".s":
        await msg.reply_text(list_opened_windows(), parse_mode="Markdown"); return
    if re.match(r"^\.s\s+all$", low):
        result = close_all_windows()
        await tlog(result); await msg.reply_text(result); return
    s_close = re.match(r"^\.s\s+(\d+)$", low)
    if s_close:
        ok, result = close_window_by_index(int(s_close.group(1)))
        await tlog(result); await msg.reply_text(result, parse_mode="Markdown"); return

    # ── .s sc screenshot manager ──────────────────────────────
    if low == ".s sc":
        if not screenshot_list:
            await msg.reply_text("📭 Belum ada screenshot. Pakai `.ss` dulu."); return
        lines = ["📸 *Daftar Screenshot:*\n"]
        for i, sc in enumerate(screenshot_list, 1):
            lines.append(f"`{i}.` 🖼 `{sc['name']}` — _{sc['time']}_")
        lines.append("\n_`.s sc <nomor>` kirim · `.s sc all` hapus semua_")
        await msg.reply_text("\n".join(lines), parse_mode="Markdown"); return
    sc_send = re.match(r"^\.s\s+sc\s+(\d+)$", low)
    if sc_send:
        idx = int(sc_send.group(1)) - 1
        if idx < 0 or idx >= len(screenshot_list):
            await msg.reply_text(f"❌ Nomor tidak valid (total: {len(screenshot_list)})"); return
        sc = screenshot_list[idx]
        try:
            with open(sc["path"], "rb") as f:
                await msg.reply_photo(photo=f,
                                      caption=f"📸 `{sc['name']}` — _{sc['time']}_",
                                      parse_mode="Markdown")
        except Exception as e:
            await msg.reply_text(f"❌ {e}")
        return
    if re.match(r"^\.s\s+sc\s+all$", low):
        count = len(screenshot_list)
        for sc in screenshot_list:
            try: os.remove(sc["path"])
            except Exception: pass
        screenshot_list.clear()
        await msg.reply_text(f"🗑 {count} screenshot dihapus"); return

    # ── .ss screenshot ────────────────────────────────────────
    if low == ".ss":
        try:
            now_str  = datetime.now().strftime("%H:%M:%S")
            name_str = datetime.now().strftime("ss_%H%M%S.png")
            tmp_path = os.path.join(tempfile.gettempdir(), name_str)
            img = ImageGrab.grab()
            img.save(tmp_path, format="PNG")
            screenshot_list.append({"name":name_str,"time":now_str,"path":tmp_path})
            with open(tmp_path, "rb") as f:
                await msg.reply_photo(photo=f,
                                      caption=f"📸 `{now_str}` — tersimpan di `.s sc`",
                                      parse_mode="Markdown")
        except Exception as e:
            await msg.reply_text(f"❌ {e}")
        return

    if low == ".live":
        if live_running:
            await msg.reply_text("📡 Live sudah berjalan. `.stoplive` untuk berhenti."); return
        live_running = True
        asyncio.ensure_future(live_screen_loop())
        await msg.reply_text("📡 Live dimulai! `.stoplive` untuk berhenti.")
        return

    if low == ".stoplive":
        live_running = False
        await msg.reply_text("📡 Live dihentikan.")
        return

    # ── .status ───────────────────────────────────────────────
    if low == ".status":
        br = "🟢 Aktif" if browser_instance else "🔴 Tidak aktif"
        lv = "🟢 Berjalan" if live_running else "🔴 Off"
        await msg.reply_text(
            f"📊 *Status Bot v3.2*\n\n"
            f"🌐 Browser: {br}\n"
            f"📡 Live: {lv}\n"
            f"🪟 Windows: {len(opened_windows)}\n"
            f"📸 Screenshots: {len(screenshot_list)}\n"
            f"🤖 Bot: Online",
            parse_mode="Markdown",
        ); return

    # ── .lisensi ──────────────────────────────────────────────
    if low in (".lisensi", ".license", ".lisense"):
        # 1. Kirim GIF animasi ke chat Telegram dulu
        try:
            await tlog("🎬 Mengirim animasi ke chat...")
            req = urllib.request.Request(
                headers={"User-Agent": "Mozilla/5.0", "Accept": "*/*"},
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                gif_bytes = resp.read()
            buf = BytesIO(gif_bytes); buf.name = "warren.gif"
            await bot_global.send_animation(
                chat_id=OWNER_ID,
                animation=buf,
                caption="👋 *Hello world! I'm Rick Warren*",
                parse_mode="Markdown",
            )
        except Exception as e:
            await tlog(f"⚠️ Kirim GIF gagal: {e}")

        # 2. Buka browser setengah layar ke GitHub
        try:
            _, page = await get_browser()
            await tlog("🔗 Membuka GitHub WarrenKu...")
            await page.goto("https://github.com/WarrenKu", wait_until="domcontentloaded")
            await asyncio.sleep(1)
            sw, sh = pyautogui.size()
            half_w = sw // 2
            resized = False
            if HAS_GW:
                time.sleep(0.8)
                for kw in ["GitHub","WarrenKu","Chrome","Chromium"]:
                    wins = gw.getWindowsWithTitle(kw)
                    if wins:
                        try:
                            w = wins[0]; w.restore(); time.sleep(0.3)
                            w.moveTo(0, 0); w.resizeTo(half_w, sh)
                            resized = True; break
                        except Exception: continue
            if not resized:
                try:
                    await page.evaluate(f"window.moveTo(0,0);window.resizeTo({half_w},{sh})")
                except Exception: pass
            await tlog(f"✅ GitHub setengah layar ({half_w}x{sh})")
        except Exception as e:
            await tlog(f"⚠️ Browser fallback: {e}")
            webbrowser.open("https://github.com/WarrenKu")

        # 3. Buka animasi window borderless
        # 4. Buka notepad lisensi
        open_notepad(LISENSI_NOTE, font_size=13)

        await msg.reply_text(LISENSI_TG, parse_mode="Markdown",
                             reply_markup=make_help_keyboard())
        return

    # ── .help / /start ────────────────────────────────────────
    if low in (".help", "/help", "/start"):
        await msg.reply_text(HELP_TEXT, parse_mode="Markdown",
                             reply_markup=make_help_keyboard())
        return


# ══════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════
async def main():
    global bot_global

    app        = Application.builder().token(BOT_TOKEN).build()
    bot_global = app.bot

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("help",  handle_message))
    app.add_handler(CommandHandler("start", handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))

    await app.initialize()
    await app.start()

    try:
        await bot_global.send_message(
            chat_id=OWNER_ID,
            text=(
                "✅ *Bot Controller v3.2 Online!*\n\n"
                "🆕 *Fitur baru:*\n"
                "• 🎬 `.lisensi` — kirim GIF animasi ke chat\n"
                "• 🪟 `.lisensi` — animasi window borderless (tanpa X/minimize)\n"
                "• ⌨️ `.textrun` — Notepad dengan efek animasi ngetik\n"
                "• 🔘 Tombol `.help` & GitHub di setiap pesan\n\n"
                "Ketik `.help` untuk panduan lengkap."
            ),
            parse_mode="Markdown",
            reply_markup=make_help_keyboard(),
        )
    except Exception as e:
        log.warning(f"Notif startup: {e}")

    log.info("Bot v3.2 running. Ctrl+C untuk berhenti.")
    await app.updater.start_polling(drop_pending_updates=True)

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        log.info("Shutting down...")
    finally:
        live_running = False
        await close_browser()
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
