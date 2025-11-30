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

    def install_pagekite(self):
        """Install PageKite using system package manager"""
        console.print("[cyan][*] Installing PageKite...[/cyan]")
        try:
            # Install pagekite from repos
            result = subprocess.run(
                ["sudo", "apt-get", "update"],
                capture_output=True,
                text=True
            )
            
            result = subprocess.run(
                ["sudo", "apt-get", "install", "-y", "pagekite"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print("[green][✓] PageKite installed successfully[/green]")
                return True
            else:
                console.print("[yellow][!] Installing from package failed, trying pip...[/yellow]")
                # Try pip install as fallback
                result = subprocess.run(
                    ["pip", "install", "pagekite"],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
                
        except Exception as e:
            console.print(f"[red][!] PageKite installation failed: {e}[/red]")
            return False

    def start_pagekite(self):
        """Start PageKite tunnel (most reliable method)"""
        console.print("[cyan][*] Starting PageKite tunnel...[/cyan]")
        
        try:
            # Generate random subdomain
            import random
            import string
            subdomain = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
            pagekite_url = f"https://{subdomain}.pagekite.me"
            
            # Start pagekite
            process = subprocess.Popen(
                [
                    "pagekite", "8080", 
                    f"{subdomain}.pagekite.me",
                    "--frontend=pagekite.me:443"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Wait for tunnel to establish
            time.sleep(8)
            
            # Verify tunnel is working
            try:
                response = requests.get(pagekite_url, timeout=10, verify=False)
                if response.status_code in [200, 404, 502]:  # 502 means tunnel is up but our app might not be
                    self.tunnel_process = process
                    self.current_url = pagekite_url
                    console.print("[green][✓] PageKite tunnel established[/green]")
                    return pagekite_url
            except requests.exceptions.RequestException:
                # Even if health check fails, the tunnel might be establishing
                console.print("[yellow][!] Tunnel establishing, may take 30-60 seconds...[/yellow]")
                self.tunnel_process = process
                self.current_url = pagekite_url
                return pagekite_url
                
            return "Error: PageKite tunnel failed to start"
            
        except Exception as e:
            return f"Error: {str(e)}"

    def start_simple_cloudflared(self):
        """Simplified Cloudflare tunnel without complex parsing"""
        console.print("[cyan][*] Starting Cloudflare tunnel...[/cyan]")
        
        # Check for cloudflared
        cloudflared_cmd = None
        if shutil.which("cloudflared"):
            cloudflared_cmd = "cloudflared"
        elif os.path.exists("./cloudflared"):
            cloudflared_cmd = "./cloudflared"
        else:
            # Download cloudflared
            console.print("[yellow][*] Downloading cloudflared...[/yellow]")
            try:
                import platform
                arch = platform.machine().lower()
                
                if 'arm' in arch or 'aarch' in arch:
                    url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
                else:
                    url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
                
                response = requests.get(url, stream=True, timeout=30)
                with open("cloudflared", "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                os.chmod("cloudflared", 0o755)
                cloudflared_cmd = "./cloudflared"
                console.print("[green][✓] Cloudflared downloaded[/green]")
            except Exception as e:
                console.print(f"[red][!] Failed to download cloudflared: {e}[/red]")
                return None
        
        if not cloudflared_cmd:
            return None
        
        try:
            # Start cloudflared with simple approach
            process = subprocess.Popen(
                [cloudflared_cmd, "tunnel", "--url", f"http://localhost:{self.port}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Give it time to start
            time.sleep(10)
            
            # For cloudflared, we can't easily get the URL in code, so we'll use a different approach
            # We'll show instructions to the user
            console.print("[yellow][!] Cloudflare tunnel started but URL not captured automatically[/yellow]")
            console.print("[cyan][*] Check your terminal for the .trycloudflare.com URL[/cyan]")
            console.print("[cyan][*] Or visit: https://trycloudflare.com[/cyan]")
            
            self.tunnel_process = process
            return "Check terminal for Cloudflare URL or use PageKite method"
            
        except Exception as e:
            return f"Error: {str(e)}"

    def start_tunnel(self):
        """Main tunnel startup - tries multiple methods"""
        console.print("[cyan][*] Establishing secure tunnel...[/cyan]")
        
        # Method 1: Try PageKite (most reliable)
        console.print("[cyan][*] Trying PageKite (method 1)...[/cyan]")
        pagekite_url = self.start_pagekite()
        
        if pagekite_url and not pagekite_url.startswith("Error"):
            return pagekite_url
        
        # Method 2: Try simple cloudflared
        console.print("[yellow][!] PageKite failed, trying Cloudflare...[/yellow]")
        cloudflare_result = self.start_simple_cloudflared()
        
        if cloudflare_result and not cloudflare_result.startswith("Error"):
            return cloudflare_result
        
        # Method 3: Localhost with instructions
        console.print("[red][!] All tunnel methods failed[/red]")
        console.print("[cyan][*] You can still use ZeroEye locally:[/cyan]")
        console.print("[green]    http://localhost:8080[/green]")
        console.print("[cyan][*] Or use ngrok manually: ngrok http 8080[/cyan]")
        
        return "http://localhost:8080 (local access only)"

    def stop_tunnel(self):
        """Clean shutdown"""
        if self.tunnel_process:
            try:
                self.tunnel_process.terminate()
                self.tunnel_process.wait(timeout=5)
            except:
                try:
                    self.tunnel_process.kill()
                except:
                    pass
            console.print("[green][✓] Tunnel stopped[/green]")

    def start_cloudflared(self):
        """Public method for compatibility"""
        return self.start_tunnel()
