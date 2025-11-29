import requests
import os
from rich.console import Console

console = Console()

class TelegramSender:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        # Test connection on init
        self.test_connection()

    def test_connection(self):
        """Test if bot token and chat ID are valid"""
        try:
            console.print("[yellow][*] Connecting to Telegram...[/yellow]")
            response = requests.get(f"{self.base_url}/getMe", timeout=30)  # Increased timeout
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    console.print("[green][✓] Telegram Bot connected successfully[/green]")
                    return True
                else:
                    console.print(f"[red][!] Telegram API error: {data.get('description')}[/red]")
                    return False
            else:
                console.print(f"[red][!] Telegram connection failed: HTTP {response.status_code}[/red]")
                return False
        except requests.exceptions.Timeout:
            console.print("[red][!] Telegram connection timed out (30s)[/red]")
            return False
        except Exception as e:
            console.print(f"[red][!] Telegram connection error: {str(e)}[/red]")
            return False

    def send_message(self, message):
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(
                f"{self.base_url}/sendMessage", 
                json=payload, 
                timeout=30
            )
            if response.status_code != 200:
                console.print(f"[yellow][!] Telegram message send failed: {response.text}[/yellow]")
        except requests.exceptions.Timeout:
            console.print("[yellow][!] Telegram message timeout[/yellow]")
        except Exception as e:
            console.print(f"[yellow][!] Telegram Send Error: {e}[/yellow]")

    def send_photo(self, photo_path, caption=""):
        try:
            if not os.path.exists(photo_path): 
                console.print(f"[yellow][!] Photo file not found: {photo_path}[/yellow]")
                return
                
            with open(photo_path, 'rb') as photo_file:
                response = requests.post(
                    f"{self.base_url}/sendPhoto",
                    data={'chat_id': self.chat_id, 'caption': caption},
                    files={'photo': photo_file},
                    timeout=60  # Larger timeout for files
                )
                if response.status_code != 200:
                    console.print(f"[yellow][!] Telegram photo send failed[/yellow]")
        except requests.exceptions.Timeout:
            console.print("[yellow][!] Telegram photo timeout[/yellow]")
        except Exception as e:
            console.print(f"[yellow][!] Telegram Photo Error: {e}[/yellow]")

    def send_audio(self, audio_path, caption=""):
        try:
            if not os.path.exists(audio_path): 
                console.print(f"[yellow][!] Audio file not found: {audio_path}[/yellow]")
                return
                
            with open(audio_path, 'rb') as audio_file:
                response = requests.post(
                    f"{self.base_url}/sendAudio",
                    data={'chat_id': self.chat_id, 'caption': caption},
                    files={'audio': audio_file},
                    timeout=60
                )
                if response.status_code != 200:
                    console.print(f"[yellow][!] Telegram audio send failed[/yellow]")
        except requests.exceptions.Timeout:
            console.print("[yellow][!] Telegram audio timeout[/yellow]")
        except Exception as e:
            console.print(f"[yellow][!] Telegram Audio Error: {e}[/yellow]")
