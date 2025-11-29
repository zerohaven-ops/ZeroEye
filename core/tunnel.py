import subprocess
import time
import os
import shutil
import re
import threading
from rich.console import Console

console = Console()

class TunnelManager:
    def __init__(self, port):
        self.port = port
        self.found_url = None
        self.process = None

    def check_cloudflared(self):
        if shutil.which("cloudflared"): 
            return "cloudflared"
        if os.path.exists("./cloudflared"): 
            return "./cloudflared"
        return None

    def _read_stderr(self):
        """Read stderr in background to find URL"""
        while self.process and self.process.poll() is None:
            line = self.process.stderr.readline()
            if not line:
                break
                
            # Regex to find the trycloudflare url
            match = re.search(r'https://[-a-z0-9]+\.trycloudflare\.com', line)
            if match:
                self.found_url = match.group(0)
                break

    def start_cloudflared(self):
        cmd = self.check_cloudflared()
        if not cmd: 
            return "❌ Failed - cloudflared not found. Install from: https://github.com/cloudflare/cloudflared"

        console.print("[cyan][*] Starting Cloudflare Tunnel (Silent Mode)...[/cyan]")
        console.print("[yellow][*] Please wait 10-15 seconds for link generation...[/yellow]")
        
        try:
            # Run cloudflared and capture stderr (where it prints the link)
            self.process = subprocess.Popen(
                [cmd, "tunnel", "--url", f"http://localhost:{self.port}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Start background thread to read stderr
            reader_thread = threading.Thread(target=self._read_stderr)
            reader_thread.daemon = True
            reader_thread.start()
            
            # Wait for URL with timeout
            timeout = 25  # seconds
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if self.found_url:
                    break
                time.sleep(0.5)
            
            # Give it a moment to ensure the URL is ready
            time.sleep(2)
            
            if self.found_url:
                console.print("[green][✓] Tunnel established successfully![/green]")
                return self.found_url
            else:
                return "❌ Error: Could not generate link. Check your internet connection."
                
        except Exception as e:
            return f"❌ Tunnel error: {str(e)}"
