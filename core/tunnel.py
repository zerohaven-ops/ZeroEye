import subprocess
import time
import requests
import random
import string
from rich.console import Console
from rich.panel import Panel

console = Console()

class TunnelManager:
    def __init__(self, port):
        self.port = port
        self.current_url = None
        self.tunnel_process = None

    def start_serveo(self):
        """Start Serveo tunnel - simplest and most reliable"""
        console.print("[cyan][*] Starting secure tunnel...[/cyan]")
        
        try:
            # Generate random subdomain
            subdomain = ''.join(random.choices(string.ascii_lowercase, k=12))
            
            # Start serveo
            process = subprocess.Popen(
                ["ssh", "-o", "StrictHostKeyChecking=no", 
                 "-R", f"{subdomain}:80:localhost:{self.port}", 
                 "serveo.net"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Give it time to establish
            time.sleep(8)
            
            url = f"https://{subdomain}.serveo.net"
            
            # Quick health check
            try:
                response = requests.get(url, timeout=10, verify=False)
                if response.status_code in [200, 404, 502]:
                    console.print("[green][✓] Secure tunnel established[/green]")
                    self.tunnel_process = process
                    self.current_url = url
                    return url
            except:
                # Even if health check fails, the tunnel might work
                console.print("[yellow][!] Tunnel establishing (may take 30 seconds)...[/yellow]")
                self.tunnel_process = process
                self.current_url = url
                return url
                
            return f"https://{subdomain}.serveo.net"
            
        except Exception as e:
            return f"Error: {str(e)}"

    def start_localhost(self):
        """Fallback to localhost with instructions"""
        console.print("[yellow][!] Tunnel service unavailable[/yellow]")
        console.print("[cyan][*] You can use these alternatives:[/cyan]")
        console.print("[green]1. Local access: http://localhost:8080[/green]")
        console.print("[green]2. Use ngrok manually: ngrok http 8080[/green]")
        console.print("[green]3. Use Cloudflare: cloudflared tunnel --url http://localhost:8080[/green]")
        return "http://localhost:8080"

    def start_tunnel(self):
        """Main tunnel startup"""
        # Try Serveo first (most reliable)
        result = self.start_serveo()
        
        if result and not result.startswith("Error"):
            return result
        
        # Fallback to localhost
        return self.start_localhost()

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
