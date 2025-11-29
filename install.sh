#!/bin/bash

# ZeroEye v2.0 Installer for Kali Linux
set -e

echo -e "\033[1;34m"
echo "╔══════════════════════════════════════╗"
echo "║         ZeroEye v2.0 Installer       ║"
echo "╚══════════════════════════════════════╝"
echo -e "\033[0m"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "\033[1;31m[!] Please do not run as root. Use regular user.\033[0m"
    exit 1
fi

# Check Python version
echo -e "\033[1;33m[*] Checking Python version...\033[0m"
if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31m[!] Python3 not found. Installing...\033[0m"
    sudo apt update && sudo apt install -y python3 python3-pip python3-venv
fi

# Check for python3-venv
echo -e "\033[1;33m[*] Checking for python3-venv...\033[0m"
if ! dpkg -l | grep -q python3-venv; then
    echo -e "\033[1;33m[*] Installing python3-venv...\033[0m"
    sudo apt update && sudo apt install -y python3-venv
fi

# Create virtual environment
echo -e "\033[1;33m[*] Creating virtual environment...\033[0m"
python3 -m venv zeroeye_venv

# Activate virtual environment
echo -e "\033[1;33m[*] Activating virtual environment...\033[0m"
source zeroeye_venv/bin/activate

# Upgrade pip
echo -e "\033[1;33m[*] Upgrading pip...\033[0m"
pip install --upgrade pip

# Remove conflicting multipart package if exists
echo -e "\033[1;33m[*] Checking for conflicting packages...\033[0m"
if pip list | grep -q "^multipart "; then
    echo -e "\033[1;33m[*] Removing conflicting 'multipart' package...\033[0m"
    pip uninstall -y multipart
fi

# Install dependencies
echo -e "\033[1;33m[*] Installing dependencies...\033[0m"
pip install -r requirements.txt

# Check for cloudflared
echo -e "\033[1;33m[*] Checking for cloudflared...\033[0m"
if ! command -v cloudflared &> /dev/null; then
    echo -e "\033[1;33m[*] Downloading cloudflared...\033[0m"
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
    chmod +x cloudflared
    echo -e "\033[1;33m[*] Note: Move cloudflared to /usr/local/bin for system-wide access\033[0m"
fi

# Create necessary directories
echo -e "\033[1;33m[*] Setting up directories...\033[0m"
mkdir -p static captured templates core

# Make scripts executable
chmod +x start.sh 2>/dev/null || true

echo -e "\033[1;32m"
echo "╔══════════════════════════════════════╗"
echo "║        Installation Complete!        ║"
echo "╚══════════════════════════════════════╝"
echo -e "\033[0m"
echo -e "\033[1;36m[*] To start ZeroEye:\033[0m"
echo -e "    Method 1: ./start.sh"
echo -e "    Method 2: python3 zeroeye.py"
echo -e "\033[1;36m[*] Virtual environment will be activated automatically\033[0m"
