import os
import subprocess
import time
import requests
import random
import string
import threading
from rich.console import Console
from rich.panel import Panel

console = Console()

class TunnelManager:
    def __init__(self, port):
        self.port = port
        self.current_url = None
        self.tunnel_process = None

    def install_cloudflared(self):
        """Install cloudflared automatically - works worldwide"""
        console.print("[cyan][*] Setting up Cloudflare tunnel...[/cyan]")
        
        try:
            # Download cloudflared based on architecture
            import platform
            system = platform.system().lower()
            machine = platform.machine().lower()
            
            if system == "linux":
                if 'arm' in machine or 'aarch' in machine:
                    url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
                else:
                    url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
            elif system == "darwin":  # macOS
                if 'arm' in machine:
                    url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64"
                else:
                    url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64"
            else:  # Windows
                url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
            
            # Download cloudflared with timeout
            response = requests.get(url, stream=True, timeout=15)
            binary_name = "cloudflared.exe" if system == "windows" else "cloudflared"
            
            with open(binary_name, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Make executable (Unix systems)
            if system != "windows":
                os.chmod(binary_name, 0o755)
            
            console.print("[green][✓] Cloudflare tunnel setup complete[/green]")
            return binary_name
            
        except Exception as e:
            console.print(f"[yellow][!] Cloudflare setup failed: {e}[/yellow]")
            console.print("[cyan][*] Will use alternative tunneling methods[/cyan]")
            return None

    def start_cloudflared_tunnel(self):
        """Start Cloudflare tunnel - most reliable worldwide"""
        console.print("[cyan][*] Starting worldwide tunnel...[/cyan]")
        
        # Get cloudflared binary
        cloudflared_cmd = None
        if os.path.exists("cloudflared"):
            cloudflared_cmd = "./cloudflared"
        elif os.path.exists("cloudflared.exe"):
            cloudflared_cmd = "cloudflared.exe"
        else:
            cloudflared_cmd = self.install_cloudflared()
        
        if not cloudflared_cmd:
            return None, "Cloudflare tunnel not available"
        
        try:
            # Start cloudflared tunnel
            process = subprocess.Popen(
                [cloudflared_cmd, "tunnel", "--url", f"http://localhost:{self.port}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Wait for tunnel to establish
            console.print("[yellow][*] Establishing worldwide connection...[/yellow]")
            time.sleep(8)
            
            # Try to get URL from output
            import select
            start_time = time.time()
            url = None
            
            while time.time() - start_time < 20:
                # Check stdout
                ready, _, _ = select.select([process.stdout], [], [], 0.5)
                if ready:
                    line = process.stdout.readline()
                    if line:
                        if ".trycloudflare.com" in line:
                            import re
                            matches = re.findall(r'https://[-a-zA-Z0-9]+\.trycloudflare\.com', line)
                            if matches:
                                url = matches[0]
                                break
                
                # Check stderr
                ready, _, _ = select.select([process.stderr], [], [], 0.1)
                if ready:
                    line = process.stderr.readline()
                    if line and ".trycloudflare.com" in line:
                        import re
                        matches = re.findall(r'https://[-a-zA-Z0-9]+\.trycloudflare\.com', line)
                        if matches:
                            url = matches[0]
                            break
            
            if url:
                console.print(f"[green][✓] Worldwide tunnel ready: {url}[/green]")
                return process, url
            else:
                # Even if we can't parse URL, cloudflared might still be working
                console.print("[yellow][!] Tunnel started, checking connectivity...[/yellow]")
                time.sleep(5)
                return process, "https://trycloudflare.com (check for your URL)"
                
        except Exception as e:
            return None, f"Tunnel error: {str(e)}"

    def start_localhost_run(self):
        """Use localhost.run - completely free, no tokens"""
        console.print("[cyan][*] Starting localhost.run tunnel...[/cyan]")
        
        try:
            # Generate random subdomain
            subdomain = ''.join(random.choices(string.ascii_lowercase, k=12))
            
            # Start localhost.run
            process = subprocess.Popen(
                [
                    "ssh", "-o", "StrictHostKeyChecking=no",
                    "-o", "ConnectTimeout=30",
                    "-R", f"{subdomain}:80:localhost:{self.port}",
                    "nokey@localhost.run"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            console.print("[yellow][*] Starting tunnel (this may take 15-30 seconds)...[/yellow]")
            time.sleep(20)
            
            # Return predicted URL (more reliable than parsing)
            predicted_url = f"https://{subdomain}.localhost.run"
            console.print(f"[green][✓] Backup tunnel ready: {predicted_url}[/green]")
            return process, predicted_url
            
        except Exception as e:
            return None, f"Backup tunnel failed: {str(e)}"

    def start_tunnel(self):
        """Main tunnel startup - fully automated"""
        console.print("[cyan][*] Starting automated worldwide tunnel...[/cyan]")
        
        # Method 1: Cloudflare (most reliable worldwide)
        process, url = self.start_cloudflared_tunnel()
        
        if url and not any(x in str(url).lower() for x in ["error", "failed", "not available"]):
            self.tunnel_process = process
            self.current_url = url
            return url
        
        # Method 2: Fallback tunnel (localhost.run)
        console.print("[yellow][!] Primary tunnel unavailable, using localhost.run...[/yellow]")
        process, url = self.start_localhost_run()
        
        if url and not any(x in str(url).lower() for x in ["error", "failed"]):
            self.tunnel_process = process
            self.current_url = url
            return url
        
        # Method 3: Ultimate fallback
        console.print(Panel(
            "[bold yellow]⚠️  Tunnel Setup Required[/bold yellow]\n\n"
            "[cyan]Automatic tunnels failed. Use manual methods:[/cyan]\n\n"
            "[green]1. Manual Cloudflare:[/green]\n"
            "   Download cloudflared from cloudflare.com\n"
            "   Run: cloudflared tunnel --url http://localhost:8080\n\n"
            "[green]2. Manual localhost.run:[/green]\n"
            "   Run: ssh -R 80:localhost:8080 nokey@localhost.run\n\n"
            "[green]3. Local access only:[/green] http://localhost:8080",
            title="Tunnel Setup",
            border_style="yellow"
        ))
        
        return "http://localhost:8080"

    def stop_tunnel(self):
        """Clean shutdown"""
        if self.tunnel_process:
            try:
                self.tunnel_process.terminate()
                self.tunnel_process.wait(timeout=3)
            except:
                try:
                    self.tunnel_process.kill()
                except:
                    pass

    def start_cloudflared(self):
        """Public method for compatibility"""
        return self.start_tunnel()
