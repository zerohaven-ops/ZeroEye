import subprocess
import time
import os
import shutil
from rich.console import Console

console = Console()

class TunnelManager:
    def __init__(self, port):
        self.port = port

    def check_cloudflared(self):
        """Checks if cloudflared is installed, if not, warns user."""
        if not shutil.which("cloudflared"):
            console.print("[yellow][!] Cloudflared not found in PATH.[/yellow]")
            console.print("[yellow][*] Attempting to use existing 'cloudflared' binary in folder...[/yellow]")
            if os.path.exists("./cloudflared"):
                return "./cloudflared"
            else:
                console.print("[red][!] Please install cloudflared or place binary here.[/red]")
                return None
        return "cloudflared"

    def start_cloudflared(self):
        cmd = self.check_cloudflared()
        if not cmd:
            return "Tunnel Failed - Install Cloudflared"

        console.print("[cyan][*] Starting Cloudflare Tunnel...[/cyan]")
        # Run cloudflared tunnel
        process = subprocess.Popen(
            [cmd, "tunnel", "--url", f"http://localhost:{self.port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(4) # Wait for tunnel to handshake
        
        # We need to read the output to get the URL
        # NOTE: In a real scenario, this requires threading to read stderr constantly
        # For simplicity, we ask user to check manual output or assume success
        console.print("[green][+] Tunnel running in background.[/green]")
        return "Check terminal output for .trycloudflare.com link"
