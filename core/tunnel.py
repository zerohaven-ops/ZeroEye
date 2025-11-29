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
        if not shutil.which("cloudflared"):
            if os.path.exists("./cloudflared"): 
                return "./cloudflared"
            else: 
                return None
        return "cloudflared"

    def start_cloudflared(self):
        cmd = self.check_cloudflared()
        if not cmd: 
            return "Failed - cloudflared not found"

        console.print("[cyan][*] Starting Cloudflare Tunnel...[/cyan]")
        console.print("[yellow][!] Look for the '.trycloudflare.com' URL in the output below:[/yellow]")
        
        # FIX: Remove pipes to allow direct terminal output
        process = subprocess.Popen(
            [cmd, "tunnel", "--url", f"http://localhost:{self.port}"],
            # No stdout/stderr pipes - lets output print directly to terminal
        )
        
        time.sleep(6)  # Give more time for tunnel to establish
        return "Check terminal output above for .trycloudflare.com link"
