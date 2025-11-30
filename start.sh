#!/bin/bash

# ZeroEye v2.1.0 Starter Script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "\033[1;36m[*] Starting ZeroEye v2.1.0...\033[0m"

# Check if virtual environment exists
if [ ! -d "zeroeye_venv" ]; then
    echo -e "\033[1;31m[!] Virtual environment not found. Run ./install.sh first\033[0m"
    exit 1
fi

# Activate virtual environment
echo -e "\033[1;33m[*] Activating virtual environment...\033[0m"
source zeroeye_venv/bin/activate

# Verify activation by checking Python path
VENV_PYTHON=$(which python3)
if [[ ! "$VENV_PYTHON" == *"zeroeye_venv"* ]]; then
    echo -e "\033[1;31m[!] Virtual environment activation failed\033[0m"
    echo -e "\033[1;33m[*] Trying direct Python execution...\033[0m"
    zeroeye_venv/bin/python3 zeroeye.py
    exit $?
fi

echo -e "\033[1;32m[+] Virtual environment activated successfully\033[0m"

# Check if zeroeye.py exists, if not use main.py
if [ -f "zeroeye.py" ]; then
    echo -e "\033[1;32m[+] Starting ZeroEye...\033[0m"
    python3 zeroeye.py
elif [ -f "main.py" ]; then
    echo -e "\033[1;32m[+] Starting ZeroEye (main.py)...\033[0m"
    python3 main.py
else
    echo -e "\033[1;31m[!] No startup script found. Check your installation.\033[0m"
    exit 1
fi
