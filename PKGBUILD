# Maintainer: Your Name <your.email@example.com>
pkgname=hotspeech
pkgver=1.0.0
pkgrel=1
pkgdesc="Simple voice recording and transcription tool using OpenAI Whisper"
arch=('any')
url="https://github.com/yourusername/hotspeech"
license=('MIT')
depends=(
    'python' 
    'python-pip' 
    'ffmpeg'
)
optdepends=(
    'wl-clipboard: clipboard support for Wayland'
    'xclip: clipboard support for X11'
    'zenity: GUI notifications'
)
makedepends=('python-build' 'python-installer' 'python-wheel')
install=hotspeech.install
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
    cd "$pkgname-$pkgver"
    cd hotspeech
    python -m build --wheel --no-isolation
}

package() {
    cd "$pkgname-$pkgver"
    
    # Create virtual environment in /opt/hotspeech
    python -m venv "$pkgdir/opt/hotspeech"
    
    # Install Python dependencies in the virtual environment
    "$pkgdir/opt/hotspeech/bin/pip" install openai fastapi uvicorn jinja2 python-multipart pydantic toml
    
    # Install the hotspeech package files directly
    install -dm755 "$pkgdir/opt/hotspeech/lib/python$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/site-packages/hotspeech"
    
    # Copy Python modules
    install -Dm644 hotspeech/main.py "$pkgdir/opt/hotspeech/lib/python$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/site-packages/hotspeech/main.py"
    install -Dm644 hotspeech/cli.py "$pkgdir/opt/hotspeech/lib/python$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/site-packages/hotspeech/cli.py"
    
    # Create __init__.py for the package
    cat > "$pkgdir/opt/hotspeech/lib/python$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/site-packages/hotspeech/__init__.py" << 'EOF'
"""Hotspeech - Voice recording and transcription tool"""
__version__ = "1.0.0"
EOF
    
    # Copy app directory if it exists
    if [ -d "hotspeech/app" ]; then
        cp -r hotspeech/app "$pkgdir/opt/hotspeech/lib/python$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/site-packages/hotspeech/"
    fi
    
    # Create wrapper scripts that use the virtual environment
    install -dm755 "$pkgdir/usr/bin"
    
    # Main hotspeech command
    cat > "$pkgdir/usr/bin/hotspeech" << 'EOF'
#!/bin/bash
exec /opt/hotspeech/bin/python -m hotspeech.main "$@"
EOF
    chmod +x "$pkgdir/usr/bin/hotspeech"
    
    # CLI command
    cat > "$pkgdir/usr/bin/hotspeech-cli" << 'EOF'
#!/bin/bash
exec /opt/hotspeech/bin/python -m hotspeech.cli "$@"
EOF
    chmod +x "$pkgdir/usr/bin/hotspeech-cli"
    
    # Install setup script
    install -Dm755 hotspeech-setup "$pkgdir/usr/bin/hotspeech-setup"
    
    # Install desktop files for easy hotkey setup
    install -Dm644 hotspeech.desktop "$pkgdir/usr/share/applications/hotspeech.desktop"
    
    # Install documentation
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    
    # Create system-wide config template
    install -Dm644 hotspeech/config.toml "$pkgdir/etc/hotspeech/config.toml"
    
    # Install convenience scripts
    install -Dm755 start_recording.sh "$pkgdir/usr/share/hotspeech/start_recording.sh"
    install -Dm755 stop_recording.sh "$pkgdir/usr/share/hotspeech/stop_recording.sh"
    
    # Install post-install message
    install -Dm644 /dev/stdin "$pkgdir/usr/share/hotspeech/post-install.txt" << 'EOF'
🎤 HOTSPEECH INSTALLED!

Quick setup (2 minutes):
1. Run: hotspeech-setup
2. Follow the prompts to set your API key
3. Set up hotkeys in your desktop environment
4. Start using: hotspeech daemon

For detailed instructions: /usr/share/doc/hotspeech/README.md
EOF
} 