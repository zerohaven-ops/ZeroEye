import requests

class TelegramSender:
    def __init__(self, token, chat_id):
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.chat_id = chat_id

    def send_message(self, text):
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "Markdown"}
            requests.post(url, json=payload, timeout=5)
        except:
            pass

    def send_photo(self, file_path, caption=""):
        try:
            url = f"{self.base_url}/sendPhoto"
            with open(file_path, "rb") as f:
                requests.post(
                    url, 
                    data={"chat_id": self.chat_id, "caption": caption, "parse_mode": "Markdown"}, 
                    files={"photo": f},
                    timeout=10
                )
        except:
            pass

    def send_audio(self, file_path, caption=""):
        try:
            url = f"{self.base_url}/sendAudio"
            with open(file_path, "rb") as f:
                requests.post(
                    url, 
                    data={"chat_id": self.chat_id, "caption": caption}, 
                    files={"audio": f},
                    timeout=20
                )
        except:
            pass
