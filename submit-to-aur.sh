#!/bin/bash

echo "🚀 AUR Submission Script for hotspeech"
echo "======================================="
echo ""

# Check if we're in the right directory
if [[ ! -d "aur-package" ]]; then
    echo "❌ Error: aur-package directory not found"
    echo "   Please run this script from the project root directory"
    exit 1
fi

# Check if SSH key is set up
echo "🔑 Checking SSH key setup..."
ssh_output=$(ssh -T aur@aur.archlinux.org 2>&1)
if echo "$ssh_output" | grep -q "Welcome to AUR"; then
    echo "✅ SSH key is configured for AUR"
else
    echo "❌ SSH key not configured for AUR"
    echo ""
    echo "SSH output: $ssh_output"
    echo ""
    echo "Please set up your SSH key first:"
    echo "1. Generate key: ssh-keygen -t ed25519 -C 'your-email@example.com'"
    echo "2. Display key: cat ~/.ssh/id_ed25519.pub"
    echo "3. Upload to: https://aur.archlinux.org/account/"
    echo "4. Test with: ssh -T aur@aur.archlinux.org"
    exit 1
fi

echo ""
echo "📦 Cloning AUR repository..."
if [[ -d "hotspeech-aur" ]]; then
    echo "⚠️  hotspeech-aur directory already exists, removing..."
    rm -rf hotspeech-aur
fi

git clone ssh://aur@aur.archlinux.org/hotspeech.git hotspeech-aur

if [[ $? -ne 0 ]]; then
    echo "❌ Failed to clone AUR repository"
    echo "   Make sure you have AUR access and the package name is available"
    exit 1
fi

echo ""
echo "📁 Copying package files..."
cp aur-package/* hotspeech-aur/

echo ""
echo "📋 Package files copied:"
ls -la hotspeech-aur/

echo ""
echo "🔍 Final verification in AUR directory..."
cd hotspeech-aur

# Quick verification
if [[ -f "PKGBUILD" && -f ".SRCINFO" ]]; then
    echo "✅ Required files present"
else
    echo "❌ Missing required files"
    exit 1
fi

echo ""
echo "📝 Committing to AUR..."
git add .

git commit -m "Initial import of hotspeech v1.0.0

Voice recording and transcription tool with hotkey support and web interface.

Features:
- Global hotkey recording (F9)
- OpenAI Whisper integration  
- Web interface on localhost:8081
- Systemd user service support
- Desktop file with recording actions

Dependencies: python, python-fastapi, uvicorn, python-jinja, python-python-multipart, python-openai, python-toml, python-pydantic, ffmpeg, libpulse, libnotify"

echo ""
echo "🚀 Pushing to AUR..."
git push origin master

if [[ $? -eq 0 ]]; then
    echo ""
    echo "🎉 SUCCESS! Package submitted to AUR"
    echo ""
    echo "📋 Next steps:"
    echo "1. Check your package at: https://aur.archlinux.org/packages/hotspeech"
    echo "2. Monitor for comments and feedback"
    echo "3. Test installation: yay -S hotspeech"
    echo ""
    echo "🔄 To update in the future:"
    echo "1. Update pkgver and sha256sums in PKGBUILD"
    echo "2. Run: makepkg --printsrcinfo > .SRCINFO"
    echo "3. Commit and push changes"
else
    echo "❌ Failed to push to AUR"
    echo "   Check the error messages above"
    exit 1
fi 