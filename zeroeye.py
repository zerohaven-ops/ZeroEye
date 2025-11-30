#!/usr/bin/env python3
"""
ZeroEye v2.0 - Main Entry Point
Automatically activates virtual environment and starts the tool
"""

import os
import sys
import subprocess

def ensure_venv():
    """Ensure we're running in the virtual environment"""
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zeroeye_venv")
    
    # Check if we're already in the correct venv
    if hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    ):
        # We're in some virtual environment, check if it's ours
        if sys.prefix.startswith(venv_path):
            return True  # Already in our venv
        else:
            print("🔧 Already in a virtual environment, but not ZeroEye's")
            print("💡 Deactivate current venv and run again")
            sys.exit(1)
    
    # Check if our venv exists
    if os.path.exists(venv_path):
        venv_python = os.path.join(venv_path, "bin", "python")
        
        # On Windows it would be different, but we're targeting Kali Linux
        if not os.path.exists(venv_python):
            venv_python = os.path.join(venv_path, "bin", "python3")
        
        if os.path.exists(venv_python):
            print("🔧 Switching to ZeroEye virtual environment...")
            
            # Get the current script path
            script_path = os.path.abspath(__file__)
            
            # Build new command line
            new_argv = [venv_python, script_path] + sys.argv[1:]
            
            # Replace current process
            os.execv(venv_python, new_argv)
        else:
            print("❌ Virtual environment Python not found")
            print("💡 Please run: ./install.sh")
            sys.exit(1)
    else:
        print("❌ Virtual environment not found")
        print("💡 Please run: ./install.sh")
        sys.exit(1)
        
    return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        'fastapi', 'uvicorn', 'rich', 'requests', 
        'python_multipart', 'json', 'time', 'shutil', 'atexit'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            if module == 'python_multipart':
                __import__('python_multipart')
            else:
                __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing dependencies: {', '.join(missing_modules)}")
        print("💡 Please run: ./install.sh")
        return False
    return True

def main():
    """Main entry point"""
    # Ensure virtual environment is active
    ensure_venv()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Now we should be in the venv, import and run
    try:
        from main import start_wizard
        print("✅ All dependencies loaded successfully")
        start_wizard()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the ZeroEye directory and dependencies are installed")
        print("💡 Try running: ./install.sh")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down ZeroEye...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
