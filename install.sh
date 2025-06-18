#!/bin/bash
# Simple Hotspeech installation script for all Linux distributions

set -e

echo "=== Hotspeech Simple Installation ==="
echo

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
HOTSPEECH_DIR="$SCRIPT_DIR/hotspeech"

# Check if we're in the right location
if [ ! -d "$HOTSPEECH_DIR" ]; then
    echo "Error: hotspeech directory not found. Make sure you're running this from the correct location."
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is required but not installed."
    echo "Please install Python 3 using your distribution's package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Arch/Manjaro:  sudo pacman -S python python-pip"
    echo "  Fedora:        sudo dnf install python3 python3-pip"
    echo "  OpenSUSE:      sudo zypper install python3 python3-pip"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ ERROR: pip3 is required but not installed."
    echo "Please install pip3 using your distribution's package manager."
    exit 1
fi

echo "✅ pip3 found"

# Check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  WARNING: ffmpeg not found (required for audio recording)"
    echo "Please install ffmpeg:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  Arch/Manjaro:  sudo pacman -S ffmpeg"
    echo "  Fedora:        sudo dnf install ffmpeg"
    echo "  OpenSUSE:      sudo zypper install ffmpeg"
    echo
    read -p "Continue without ffmpeg? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ ffmpeg found"
fi

# Check for clipboard tools
CLIPBOARD_FOUND=false
if command -v wl-copy &> /dev/null; then
    echo "✅ wl-clipboard found (Wayland)"
    CLIPBOARD_FOUND=true
elif command -v xclip &> /dev/null; then
    echo "✅ xclip found (X11)"
    CLIPBOARD_FOUND=true
fi

if [ "$CLIPBOARD_FOUND" = false ]; then
    echo "⚠️  WARNING: No clipboard tool found"
    echo "Please install a clipboard tool:"
    echo "  For Wayland: wl-clipboard"
    echo "  For X11: xclip"
    echo
    echo "  Ubuntu/Debian: sudo apt install wl-clipboard xclip"
    echo "  Arch/Manjaro:  sudo pacman -S wl-clipboard xclip"
    echo "  Fedora:        sudo dnf install wl-clipboard xclip"
    echo "  OpenSUSE:      sudo zypper install wl-clipboard xclip"
fi

# Change to hotspeech directory
cd "$HOTSPEECH_DIR"

# Install Python dependencies
echo
echo "📦 Installing Python dependencies..."
pip3 install --user -r requirements.txt

echo "✅ Dependencies installed!"

# Create config directories
echo
echo "📁 Setting up directories..."
mkdir -p ~/.hotspeech/audio

# Check if config.toml exists, if not create default
if [ ! -f "config.toml" ]; then
    echo "📝 Creating default config.toml..."
    cat > config.toml << 'EOL'
[hotkeys]
# These are just examples - you'll set up hotkeys manually
record_transcribe = "ctrl+shift+r"
record_quicknote = "ctrl+shift+n"

[recording]
output_format = "wav"
max_duration_seconds = 3600
audio_dir = "~/.hotspeech/audio"

[transcription]
backend = "api"
model = "whisper-1"
language = "en"
api_key = ""  # Set your OpenAI API key here

[storage]
sqlite_path = "~/.hotspeech/hotspeech.db"
keep_last_n = 10

[clipboard]
enabled = true

[webui]
port = 8080
host = "127.0.0.1"
EOL
fi

# Get OpenAI API key
echo
echo "🔑 OpenAI API Key Setup"
echo "You need an OpenAI API key for transcription."
echo "Get one from: https://platform.openai.com/api-keys"
echo
read -p "Enter your OpenAI API key (or press Enter to skip): " api_key

if [[ ! -z "$api_key" ]]; then
    # Update config.toml with the API key
    sed -i "s/api_key = \"\"/api_key = \"$api_key\"/" config.toml
    echo "✅ API key saved to config.toml"
else
    echo "⚠️  No API key provided. You can:"
    echo "   1. Edit config.toml and add your key later"
    echo "   2. Set environment variable: export OPENAI_API_KEY='your-key'"
fi

echo
echo "🎉 INSTALLATION COMPLETE!"
echo
echo "=" * 60
echo "📍 PROGRAM LOCATION:"
echo "   $HOTSPEECH_DIR"
echo
echo "🚀 TO START HOTSPEECH:"
echo "   cd $HOTSPEECH_DIR"
echo "   python3 main.py daemon"
echo
echo "⌨️  MANUAL HOTKEY SETUP:"
echo "When you run the daemon, it will show you the exact commands"
echo "to use for setting up hotkeys in your desktop environment."
echo
echo "The commands will be something like:"
echo "   Start: python3 $HOTSPEECH_DIR/main.py record"
echo "   Stop:  python3 $HOTSPEECH_DIR/main.py stop"
echo
echo "📖 See README.md for detailed hotkey setup instructions"
echo "   for GNOME, KDE, i3, sway, xbindkeys, and more!"
echo "=" * 60 