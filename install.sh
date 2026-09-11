#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "======================================================="
echo "   🎙️ Installing MyVoice (Linux Edition) by @nff747"
echo "======================================================="

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed."
    exit 1
fi

# 2. Check or install uv
if ! command -v uv &> /dev/null; then
    echo "📦 uv not found, installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# 3. Create virtual environment
echo "🐍 Creating virtual environment..."
if command -v uv &> /dev/null; then
    uv venv .venv
    echo "⚡ Installing dependencies with uv..."
    uv pip install -r requirements.txt
    echo "🚀 Installing CUDA-accelerated PyTorch..."
    uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
else
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
    .venv/bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
fi

# 4. Make run script executable
chmod +x run_myvoice.sh

# 5. Install 'myvoice' command to ~/.local/bin
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/myvoice" << EOF
#!/bin/bash
exec "$SCRIPT_DIR/run_myvoice.sh" "\$@"
EOF
chmod +x "$HOME/.local/bin/myvoice"

# 6. Install desktop shortcut
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/myvoice.desktop" << EOF
[Desktop Entry]
Name=MyVoice TTS
Comment=Real-Time AI Voice Generator & Cloner
Exec=$HOME/.local/bin/myvoice
Icon=$SCRIPT_DIR/ApplicationPhotos/MyVoiceTransparant.png
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Utility;
Keywords=tts;voice;ai;speech;cloning;
EOF

if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
fi

echo ""
echo "======================================================="
echo "   ✅ Installation Complete!"
echo "   🚀 You can now launch MyVoice simply by typing:"
echo "      myvoice"
echo "   Or click the desktop icon in your app launcher."
echo "======================================================="
