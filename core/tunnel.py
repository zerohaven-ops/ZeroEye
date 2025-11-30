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

    def check_localxpose(self):
        """Check if localxpose is available"""
        if shutil.which("localxpose"):
            return "localxpose"
        if os.path.exists("./localxpose"):
            return "./localxpose"
        return None

    def download_localxpose(self):
        """Download localxpose automatically"""
        console.print("[cyan][*] Downloading LocalXpose...[/cyan]")
        try:
            # Download based on architecture
            import platform
            arch = platform.machine().lower()
            
            if 'arm' in arch or 'aarch' in arch:
                url = "https://github.com/LocalXpose/LocalXpose/releases/download/v2.0.0/localxpose-linux-arm64"
            else:
                url = "https://github.com/LocalXpose/LocalXpose/releases/download/v2.0.0/localxpose-linux-amd64"
            
            response = requests.get(url, stream=True)
            with open("localxpose", "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            os.chmod("localxpose", 0o755)
            console.print("[green][✓] LocalXpose downloaded successfully[/green]")
            return "./localxpose"
        except Exception as e:
            console.print(f"[red][!] Failed to download LocalXpose: {e}[/red]")
            return None

    def start_localxpose(self):
        """Start LocalXpose tunnel (clean and silent)"""
        cmd = self.check_localxpose()
        if not cmd:
            cmd = self.download_localxpose()
            if not cmd:
                return None, "Failed to setup LocalXpose"

        console.print("[cyan][*] Starting secure tunnel...[/cyan]")
        
        try:
            # Start localxpose with region selection for better performance
            process = subprocess.Popen(
                [cmd, "tunnel", "http", "--region", "eu", str(self.port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Wait for tunnel URL
            url = None
            start_time = time.time()
            
            while time.time() - start_time < 15:  # 15 second timeout
                line = process.stdout.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                
                # Extract URL from localxpose output
                match = re.search(r'https://[a-zA-Z0-9\-]+\.loca\.lt', line)
                if match:
                    url = match.group(0)
                    break
            
            if url:
                # Wait for tunnel to stabilize
                time.sleep(2)
                return process, url
            else:
                process.terminate()
                return None, "Failed to get tunnel URL"
                
        except Exception as e:
            return None, f"Tunnel start failed: {str(e)}"

    def is_tunnel_healthy(self, url, timeout=5):
        """Simple health check"""
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            return response.status_code in [200, 302, 404]
        except:
            return False

    def start_tunnel(self):
        """Main tunnel startup - clean and professional"""
        console.print("[cyan][*] Establishing secure connection...[/cyan]")
        
        # Try LocalXpose first (more reliable)
        process, url = self.start_localxpose()
        
        if url and not url.startswith("Failed"):
            self.tunnel_process = process
            self.current_url = url
            console.print("[green][✓] Secure tunnel established[/green]")
            return url
        
        # Fallback to Cloudflare if LocalXpose fails
        console.print("[yellow][!] Primary tunnel failed, trying backup...[/yellow]")
        return self.start_cloudflared_fallback()

    def start_cloudflared_fallback(self):
        """Fallback to Cloudflare with minimal logging"""
        cmd = self.check_cloudflared()
        if not cmd:
            return "Error: No tunneling service available"

        try:
            process = subprocess.Popen(
                [cmd, "tunnel", "--url", f"http://localhost:{self.port}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Extract URL quietly
            url = None
            start_time = time.time()
            
            while time.time() - start_time < 10:
                line = process.stderr.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                
                match = re.search(r'https://[-a-z0-9]+\.trycloudflare\.com', line)
                if match:
                    url = match.group(0)
                    break
            
            if url:
                time.sleep(2)
                self.tunnel_process = process
                self.current_url = url
                console.print("[green][✓] Backup tunnel established[/green]")
                return url
            else:
                return "Error: Could not establish tunnel connection"
                
        except Exception as e:
            return f"Error: {str(e)}"

    def check_cloudflared(self):
        """Check for cloudflared fallback"""
        if shutil.which("cloudflared"):
            return "cloudflared"
        if os.path.exists("./cloudflared"):
            return "./cloudflared"
        return None

    def stop_tunnel(self):
        """Clean shutdown"""
        if self.tunnel_process:
            try:
                self.tunnel_process.terminate()
                self.tunnel_process.wait(timeout=2)
            except:
                try:
                    self.tunnel_process.kill()
                except:
                    pass

    def start_cloudflared(self):
        """Public method for compatibility"""
        return self.start_tunnel()
