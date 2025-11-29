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
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
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
                timeout=10
            )
            
            if response.status_code != 200:
                console.print(f"[red][!] Telegram send failed: {response.text}[/red]")
                
        except requests.exceptions.RequestException as e:
            console.print(f"[red][!] Telegram network error: {str(e)}[/red]")
        except Exception as e:
            console.print(f"[red][!] Unexpected Telegram error: {str(e)}[/red]")

    def send_photo(self, photo_path):
        try:
            if not os.path.exists(photo_path):
                console.print(f"[red][!] Photo file not found: {photo_path}[/red]")
                return

            with open(photo_path, 'rb') as photo_file:
                files = {'photo': photo_file}
                data = {'chat_id': self.chat_id}
                
                response = requests.post(
                    f"{self.base_url}/sendPhoto",
                    files=files,
                    data=data,
                    timeout=30
                )
                
            if response.status_code != 200:
                console.print(f"[red][!] Telegram photo send failed: {response.text}[/red]")
                
        except requests.exceptions.RequestException as e:
            console.print(f"[red][!] Telegram photo network error: {str(e)}[/red]")
        except Exception as e:
            console.print(f"[red][!] Unexpected Telegram photo error: {str(e)}[/red]")
