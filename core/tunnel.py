import subprocess
import time
import requests
import os
import shutil
from rich.console import Console
from rich.panel import Panel

console = Console()

class TunnelManager:
    def __init__(self, port):
        self.port = port
        self.current_url = None
        self.tunnel_process = None

    def install_ngrok(self):
        """Install ngrok automatically"""
        console.print("[cyan][*] Setting up ngrok...[/cyan]")
        
        try:
            # Download ngrok
            import platform
            arch = platform.machine().lower()
            
            if 'arm' in arch or 'aarch' in arch:
                url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz"
            else:
                url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
            
            # Download and extract
            import tempfile
            import tarfile
            
            response = requests.get(url, stream=True, timeout=30)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tgz")
            
            with open(temp_file.name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract
            with tarfile.open(temp_file.name, 'r:gz') as tar:
                tar.extractall()
            
            # Clean up
            os.remove(temp_file.name)
            
            # Make executable
            if os.path.exists("ngrok"):
                os.chmod("ngrok", 0o755)
                console.print("[green][✓] Ngrok installed successfully[/green]")
                return "./ngrok"
            else:
                console.print("[red][!] Ngrok extraction failed[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red][!] Ngrok installation failed: {e}[/red]")
            return None

    def start_ngrok(self):
        """Start ngrok tunnel - most reliable method"""
        console.print("[cyan][*] Starting ngrok tunnel...[/cyan]")
        
        # Find ngrok executable
        ngrok_cmd = None
        if shutil.which("ngrok"):
            ngrok_cmd = "ngrok"
        elif os.path.exists("./ngrok"):
            ngrok_cmd = "./ngrok"
        else:
            ngrok_cmd = self.install_ngrok()
        
        if not ngrok_cmd:
            return None, "Failed to setup ngrok"

        try:
            # Start ngrok
            process = subprocess.Popen(
                [ngrok_cmd, "http", str(self.port), "--log=stdout"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Wait for ngrok to start
            time.sleep(3)
            
            # Get ngrok status
            try:
                response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    tunnels = data.get("tunnels", [])
                    for tunnel in tunnels:
                        if tunnel.get("proto") == "https":
                            url = tunnel.get("public_url")
                            if url:
                                console.print("[green][✓] Ngrok tunnel established[/green]")
                                return process, url
            except:
                pass
            
            # If API fails, try to parse output
            console.print("[yellow][!] Waiting for ngrok URL (may take 10-15 seconds)...[/yellow]")
            time.sleep(10)
            
            try:
                response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    tunnels = data.get("tunnels", [])
                    for tunnel in tunnels:
                        if tunnel.get("proto") == "https":
                            url = tunnel.get("public_url")
                            if url:
                                console.print("[green][✓] Ngrok tunnel established[/green]")
                                return process, url
            except:
                pass
                
            return None, "Failed to get ngrok URL"
            
        except Exception as e:
            return None, f"Error: {str(e)}"

    def start_localhost_run(self):
        """Alternative: localhost.run (SSH based)"""
        console.print("[cyan][*] Trying localhost.run...[/cyan]")
        
        try:
            process = subprocess.Popen(
                ["ssh", "-o", "StrictHostKeyChecking=no", 
                 "-R", "80:localhost:8080", "nokey@localhost.run"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Wait for URL
            time.sleep(8)
            
            # Try to read output
            import select
            import sys
            
            start_time = time.time()
            while time.time() - start_time < 10:
                # Check if there's output
                ready, _, _ = select.select([process.stdout], [], [], 0.1)
                if ready:
                    line = process.stdout.readline()
                    if "localhost.run" in line:
                        # Extract URL
                        import re
                        match = re.search(r'https://[a-zA-Z0-9\-]+\.localhost\.run', line)
                        if match:
                            url = match.group(0)
                            console.print("[green][✓] localhost.run tunnel established[/green]")
                            return process, url
                time.sleep(0.5)
                
            return None, "Timeout waiting for localhost.run"
            
        except Exception as e:
            return None, f"Error: {str(e)}"

    def start_tunnel(self):
        """Main tunnel startup - tries multiple reliable methods"""
        
        # Method 1: Ngrok (most reliable)
        console.print("[cyan][*] Starting secure tunnel (Method 1: Ngrok)...[/cyan]")
        process, url = self.start_ngrok()
        
        if url and not url.startswith("Error") and not url.startswith("Failed"):
            self.tunnel_process = process
            self.current_url = url
            return url
        
        # Method 2: localhost.run
        console.print("[yellow][!] Ngrok failed, trying localhost.run...[/yellow]")
        process, url = self.start_localhost_run()
        
        if url and not url.startswith("Error") and not url.startswith("Failed"):
            self.tunnel_process = process
            self.current_url = url
            return url
        
        # Method 3: Manual instructions
        console.print("[red][!] All tunnel methods failed[/red]")
        console.print("[cyan][*] You can use these alternatives:[/cyan]")
        console.print("[green]1. Local access: http://localhost:8080[/green]")
        console.print("[green]2. Manual ngrok: Download from ngrok.com, then run: ngrok http 8080[/green]")
        console.print("[green]3. Manual cloudflare: cloudflared tunnel --url http://localhost:8080[/green]")
        
        return "http://localhost:8080 (use manual tunneling methods above)"

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

    def start_cloudflared(self):
        """Public method for compatibility"""
        return self.start_tunnel()
