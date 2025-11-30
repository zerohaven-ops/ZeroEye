import requests
import os
from rich.console import Console

console = Console()

class TelegramSender:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        # Test connection
        self.test_connection()

    def test_connection(self):
        """Test Telegram connection"""
        try:
            console.print("[cyan][*] Testing Telegram connection...[/cyan]")
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    console.print("[green][✓] Telegram connected[/green]")
                    return True
            console.print("[yellow][!] Telegram configuration issue[/yellow]")
            return False
        except Exception:
            console.print("[yellow][!] Telegram connection failed[/yellow]")
            return False

    def send_message(self, message):
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            requests.post(f"{self.base_url}/sendMessage", json=payload, timeout=10)
        except Exception:
            pass  # Silent fail

    def send_photo(self, photo_path, caption=""):
        try:
            if not os.path.exists(photo_path): 
                return
                
            with open(photo_path, 'rb') as photo_file:
                requests.post(
                    f"{self.base_url}/sendPhoto",
                    data={'chat_id': self.chat_id, 'caption': caption},
                    files={'photo': photo_file},
                    timeout=30
                )
        except Exception:
            pass  # Silent fail

    def send_audio(self, audio_path, caption=""):
        try:
            if not os.path.exists(audio_path): 
                return
                
            with open(audio_path, 'rb') as audio_file:
                requests.post(
                    f"{self.base_url}/sendAudio",
                    data={'chat_id': self.chat_id, 'caption': caption},
                    files={'audio': audio_file},
                    timeout=30
                )
        except Exception:
            pass  # Silent fail
