#!/bin/bash

# ZeroEye Installer
# Developer: Zero Haven

echo -e "\e[1;32m[*] Installing ZeroEye Dependencies...\e[0m"

# System updates
sudo apt-get update
sudo apt-get install -y python3 python3-pip wget unzip

# Python libraries
pip3 install -r requirements.txt

echo -e "\e[1;32m[*] Installation Complete.\e[0m"
echo -e "\e[1;33m[+] Run 'python3 main.py' to start ZeroEye.\e[0m"
chmod +x main.py
