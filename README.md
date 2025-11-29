## ZeroEye v2.0 - Information Gathering Framework

Developed by: Zero Haven

ZeroEye is a next-generation reconnaissance tool designed for Red Team engagements and educational security testing. It leverages advanced client-side JavaScript techniques to gather device telemetry and audio/visual data, transmitting it securely to a self-hosted Python server.

⚠️ Disclaimer

This tool is for EDUCATIONAL PURPOSES and AUTHORIZED SECURITY TESTING only.
The developer (Zero Haven) is not responsible for any misuse of this tool. Using this tool against computers or networks without explicit permission is illegal and punishable by law.

🚀 Features

Zero Config: Self-hosted on your machine.

Nuclear Payload:

📸 CamShot: Silent camera capture.

🎙️ AudioBug: 15-second audio recording.

📍 GeoTag: High-accuracy GPS.

🌐 NetScan: Internal IP Leak (WebRTC).

Dual Exfiltration:

Send data to your private Telegram Bot.

Save data locally to captured/ folder.

Smart Templates: Eid, Ramadan, Free Data (Jazz/Zong/STC).

💿 Installation (Kali Linux)

Clone the repository:

git clone https://github.com/zerohaven-ops/ZeroEye 

cd ZeroEye


Run the installer:

chmod +x install.sh
./install.sh


Start the tool:

python3 main.py


⚙️ How to Use

Get a Telegram Bot:

Search for @BotFather on Telegram.

Create a new bot and get the Token.

Search for @userinfobot to get your Chat ID.

Run ZeroEye:

Paste your Token and Chat ID when asked.

Select a template (e.g., Free Data).

Select Cloudflared Tunnel.

Send Link:

Copy the generated trycloudflare.com link.

Send it to the target device.

🛡️ License

MIT License - See LICENSE file for details.
