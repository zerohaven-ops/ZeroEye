import subprocess
import time
import os
import shutil
import re
import requests
import threading
from rich.console import Console
from rich.panel import Panel

console = Console()

class TunnelManager:
    def __init__(self, port):
        self.port = port
        self.current_url = None
        self.tunnel_process = None
        self.is_running = False
        self.health_check_thread = None

    def check_cloudflared(self):
        if shutil.which("cloudflared"):
            return "cloudflared"
        if os.path.exists("./cloudflared"):
            return "./cloudflared"
        return None

    def extract_tunnel_url(self, process):
        """Extract tunnel URL from cloudflared output with multiple patterns"""
        patterns = [
            r'https://[-a-z0-9]+\.trycloudflare\.com',
            r'https://[a-z0-9\-]+\.trycloudflare\.com',
            r'tunneled at: (https://[^\s]+)',
            r'Your tunnel is available at (https://[^\s]+)'
        ]
        
        start_time = time.time()
        while time.time() - start_time < 30:  # 30 second timeout
            try:
                line = process.stderr.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                
                console.print(f"[grey50][Tunnel] {line.strip()}[/grey50]")
                
                for pattern in patterns:
                    match = re.search(pattern, line)
                    if match:
                        url = match.group(1) if match.groups() else match.group(0)
                        console.print(f"[green][✓] Tunnel URL detected: {url}[/green]")
                        return url
            except:
                break
        
        return None

    def is_tunnel_healthy(self, url, timeout=10):
        """Check if tunnel is responding properly"""
        try:
            response = requests.get(url, timeout=timeout, verify=False)
            return response.status_code in [200, 404, 502]  # 502 means tunnel is up but app might be down
        except requests.exceptions.RequestException as e:
            return False

    def start_single_tunnel(self):
        """Start a single tunnel instance"""
        cmd = self.check_cloudflared()
        if not cmd:
            return None, "cloudflared not found"

        console.print("[cyan][*] Starting Cloudflare Tunnel...[/cyan]")
        
        try:
            process = subprocess.Popen(
                [cmd, "tunnel", "--url", f"http://localhost:{self.port}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Wait for tunnel to start and extract URL
            url = self.extract_tunnel_url(process)
            if url:
                # Wait a bit for tunnel to stabilize
                time.sleep(3)
                return process, url
            else:
                process.terminate()
                return None, "Failed to extract tunnel URL"
                
        except Exception as e:
            return None, f"Tunnel start failed: {str(e)}"

    def health_monitor(self):
        """Background thread to monitor tunnel health"""
        while self.is_running:
            try:
                if self.current_url and self.tunnel_process:
                    if not self.is_tunnel_healthy(self.current_url):
                        console.print("[yellow][!] Tunnel health check failed, restarting...[/yellow]")
                        self.restart_tunnel()
                time.sleep(10)  # Check every 10 seconds
            except:
                time.sleep(5)

    def restart_tunnel(self):
        """Restart the tunnel with new connection"""
        if self.tunnel_process:
            try:
                self.tunnel_process.terminate()
                self.tunnel_process.wait(timeout=5)
            except:
                try:
                    self.tunnel_process.kill()
                except:
                    pass
        
        console.print("[yellow][*] Attempting tunnel restart...[/yellow]")
        
        # Try up to 3 times to establish a new tunnel
        for attempt in range(3):
            console.print(f"[cyan][*] Tunnel attempt {attempt + 1}/3[/cyan]")
            
            process, url = self.start_single_tunnel()
            if url and not url.startswith("Failed"):
                self.tunnel_process = process
                self.current_url = url
                console.print(f"[green][✓] Tunnel restarted successfully: {url}[/green]")
                return True
            else:
                console.print(f"[red][!] Tunnel attempt {attempt + 1} failed[/red]")
                time.sleep(2)
        
        console.print("[red][!] All tunnel restart attempts failed[/red]")
        return False

    def start_cloudflared(self):
        """Main tunnel startup with auto-recovery"""
        self.is_running = True
        
        # First attempt to start tunnel
        process, url = self.start_single_tunnel()
        
        if not url or url.startswith("Failed"):
            console.print("[red][!] Initial tunnel startup failed, retrying...[/red]")
            if not self.restart_tunnel():
                return "Error: Could not establish tunnel connection"
        
        self.tunnel_process = process
        self.current_url = url
        
        # Start health monitoring in background
        self.health_check_thread = threading.Thread(target=self.health_monitor, daemon=True)
        self.health_check_thread.start()
        
        # Wait a bit to ensure tunnel is stable
        time.sleep(2)
        
        # Verify tunnel is actually working
        if self.is_tunnel_healthy(self.current_url):
            console.print("[green][✓] Tunnel is healthy and ready![/green]")
            return self.current_url
        else:
            console.print("[yellow][!] Tunnel started but health check failed, attempting recovery...[/yellow]")
            if self.restart_tunnel():
                return self.current_url
            else:
                return "Error: Tunnel started but not responding"

    def stop_tunnel(self):
        """Stop the tunnel and cleanup"""
        self.is_running = False
        if self.tunnel_process:
            try:
                self.tunnel_process.terminate()
                self.tunnel_process.wait(timeout=3)
            except:
                try:
                    self.tunnel_process.kill()
                except:
                    pass
        console.print("[yellow][!] Tunnel stopped[/yellow]")
