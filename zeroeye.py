#!/usr/bin/env python3
"""
ZeroEye v2.0 - Main Entry Point
Single command startup: python3 zeroeye.py
"""

import os
import sys

def check_venv():
    """Check if we're running in the virtual environment"""
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("\033[1;33m[*] Activating virtual environment...\033[0m")
        venv_path = os.path.join(os.path.dirname(__file__), 'zeroeye_venv')
        if os.path.exists(venv_path):
            activate_script = os.path.join(venv_path, 'bin', 'activate_this.py')
            if os.path.exists(activate_script):
                with open(activate_script) as f:
                    exec(f.read(), {'__file__': activate_script})
            else:
                print("\033[1;31m[!] Virtual environment not properly activated. Run ./start.sh instead\033[0m")
                sys.exit(1)
        else:
            print("\033[1;31m[!] Virtual environment not found. Please run ./install.sh first\033[0m")
            sys.exit(1)

def main():
    """Main entry point"""
    check_venv()
    
    # Import and run the actual application
    from main import start_wizard
    start_wizard()

if __name__ == "__main__":
    main()
