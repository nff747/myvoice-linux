#!/usr/bin/env bash
# ==============================================================================
#   🎙️ MyVoice (Linux Edition) — One-Click Universal Installer
#   Authored & Rebuilt for Linux by @nff747 (https://github.com/nff747)
# ==============================================================================
set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

clear 2>/dev/null || true
echo -e "${CYAN}${BOLD}"
echo "  __  __       __      __   _          "
echo " |  \/  |      \ \    / /  (_)         "
echo " | \  / |_   __ \ \  / /__  _  ___ ___ "
echo " | |\/| | | | |  \ \/ / _ \| |/ __/ _ \\"
echo " | |  | | |_| |   \  / (_) | | (_|  __/"
echo " |_|  |_|\__, |    \/ \___/|_|\___\___|"
echo "          __/ |    [ Linux Edition ]   "
echo "         |___/     Built by @nff747    "
echo -e "${NC}"
echo -e "${PURPLE}=======================================================${NC}"
echo -e "${BOLD}🚀 Fast, Zero-Shot AI Voice Generator, Cloner & Auto-Reply${NC}"
echo -e "${PURPLE}=======================================================${NC}\n"

# 1. Determine installation directory
if [ -d ".git" ] && [ -f "requirements.txt" ]; then
    INSTALL_DIR="$(pwd)"
else
    INSTALL_DIR="$HOME/myvoice-linux"
    if [ ! -d "$INSTALL_DIR" ]; then
        echo -e "${CYAN}📥 Cloning repository to ${BOLD}$INSTALL_DIR${NC}..."
        git clone https://github.com/nff747/myvoice-linux.git "$INSTALL_DIR"
    fi
    cd "$INSTALL_DIR"
fi

# 2. Check Python 3
echo -e "${CYAN}🔍 Checking system environment...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 is not installed on your system.${NC}"
    echo "Please install Python 3 using your package manager (e.g., sudo pacman -S python or sudo apt install python3 python3-venv)"
    exit 1
fi

# 3. Check or install uv for ultra-fast setup
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚡ uv not found. Installing uv for 10x faster installation...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1 || true
    export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
fi

# 4. Virtual environment setup
echo -e "${GREEN}🐍 Setting up Python virtual environment...${NC}"
if command -v uv &> /dev/null; then
    uv venv .venv
    echo -e "${CYAN}📦 Installing dependencies...${NC}"
    uv pip install -r requirements.txt
    echo -e "${PURPLE}🚀 Installing CUDA-accelerated PyTorch (PyTorch 2.6 + CUDA 12.4)...${NC}"
    uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
else
    python3 -m venv .venv
    echo -e "${CYAN}📦 Installing dependencies...${NC}"
    .venv/bin/pip install -r requirements.txt
    echo -e "${PURPLE}🚀 Installing CUDA-accelerated PyTorch...${NC}"
    .venv/bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
fi

# 5. Make run script executable
chmod +x run_myvoice.sh

# 6. Install global 'myvoice' CLI command
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/myvoice" << EOF
#!/usr/bin/env bash
exec "$INSTALL_DIR/run_myvoice.sh" "\$@"
EOF
chmod +x "$HOME/.local/bin/myvoice"

# 7. Install desktop application launcher
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/myvoice.desktop" << EOF
[Desktop Entry]
Name=MyVoice TTS
Comment=Real-Time AI Voice Generator, Cloner & Auto-Reply
Exec=$HOME/.local/bin/myvoice
Icon=$INSTALL_DIR/ApplicationPhotos/MyVoiceTransparant.png
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Utility;
Keywords=tts;voice;ai;speech;cloning;discord;
EOF

if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
fi

# 8. Success Output
echo -e "\n${GREEN}${BOLD}=======================================================${NC}"
echo -e "${GREEN}${BOLD}   🎉 Installation Finished Successfully!${NC}"
echo -e "${GREEN}${BOLD}=======================================================${NC}"
echo -e "💡 ${BOLD}How to launch MyVoice:${NC}"
echo -e "   1. Type ${CYAN}${BOLD}myvoice${NC} anywhere in your terminal"
echo -e "   2. Or search for ${CYAN}${BOLD}MyVoice TTS${NC} in your desktop applications\n"
echo -e "🎧 ${BOLD}Discord Setup:${NC}"
echo -e "   - In Discord Settings → Voice & Video → Microphone, choose: ${PURPLE}${BOLD}MyVoice_Virtual_Microphone${NC}\n"
echo -e "⭐ GitHub: ${CYAN}https://github.com/nff747/myvoice-linux${NC}\n"
