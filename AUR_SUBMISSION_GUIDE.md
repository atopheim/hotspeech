# AUR Submission Guide for Hotspeech

This guide explains how to submit the hotspeech package to the Arch User Repository (AUR).

## Prerequisites

1. **AUR Account**: Register at https://aur.archlinux.org/register/
2. **SSH Key**: Upload your SSH public key to your AUR account
3. **Git**: Ensure git is installed and configured
4. **makepkg**: Arch Linux package building tools

## Package Files Ready for Submission

The `aur-package/` directory contains all necessary files:

- `PKGBUILD` - Main package build script
- `.SRCINFO` - Package metadata (auto-generated from PKGBUILD)
- `hotspeech.install` - Post-installation messages and setup
- `hotspeech.service` - Systemd user service file
- `hotspeech.desktop` - Desktop application file

## Submission Steps

### 1. Clone the AUR Repository

```bash
git clone ssh://aur@aur.archlinux.org/hotspeech.git hotspeech-aur
cd hotspeech-aur
```

### 2. Copy Package Files

```bash
# Copy all files from the aur-package directory
cp ../aur-package/* .
```

### 3. Verify Package Build

```bash
# Test the package builds correctly
makepkg --syncdeps --noconfirm --rmdeps

# Clean up build artifacts
rm -rf src/ pkg/ *.pkg.tar.zst
```

### 4. Commit and Push

```bash
# Add all files
git add .

# Commit with descriptive message
git commit -m "Initial import of hotspeech v1.0.0

Voice recording and transcription tool with hotkey support and web interface.

Features:
- Global hotkey recording (F9)
- OpenAI Whisper integration
- Web interface on localhost:8081
- Systemd user service support
- Desktop file with recording actions"

# Push to AUR
git push origin master
```

## Package Details

### Dependencies

- **Runtime**: python, python-fastapi, uvicorn, python-jinja, python-python-multipart, python-openai, python-toml, python-pydantic, ffmpeg, libpulse, libnotify
- **Optional**: xclip (X11 clipboard), wl-clipboard (Wayland clipboard)
- **Build**: python-build, python-installer, python-wheel, python-setuptools

### Installation Files

- **Desktop file**: `/usr/share/applications/hotspeech.desktop`
- **Systemd service**: `/usr/lib/systemd/user/hotspeech.service`
- **Config example**: `/usr/share/hotspeech/config.toml.example`
- **Documentation**: `/usr/share/doc/hotspeech/`
- **License**: `/usr/share/licenses/hotspeech/LICENSE`

## Post-Submission

1. **Monitor Comments**: Check the AUR page for user feedback
2. **Update Package**: When new versions are released, update `pkgver` and `sha256sums`
3. **Flag Out-of-Date**: Users may flag the package when updates are available

## Package Maintenance

### Updating to New Version

1. Edit `PKGBUILD`:

   - Update `pkgver`
   - Update `sha256sums` (get new hash from GitHub release)
   - Reset `pkgrel=1`

2. Regenerate `.SRCINFO`:

   ```bash
   makepkg --printsrcinfo > .SRCINFO
   ```

3. Test build:

   ```bash
   makepkg --syncdeps --noconfirm --rmdeps
   ```

4. Commit and push:
   ```bash
   git add .
   git commit -m "Update to v<new_version>"
   git push
   ```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Verify all package names exist in repositories
2. **Build Failures**: Test locally with `makepkg` before pushing
3. **SHA256 Mismatch**: Regenerate hash with:
   ```bash
   curl -sL https://github.com/atopheim/hotspeech/archive/v<version>.tar.gz | sha256sum
   ```

### Support

- **AUR Guidelines**: https://wiki.archlinux.org/title/AUR_submission_guidelines
- **PKGBUILD**: https://wiki.archlinux.org/title/PKGBUILD
- **makepkg**: https://wiki.archlinux.org/title/Makepkg

## Files Status

✅ PKGBUILD - Complete with correct dependencies  
✅ .SRCINFO - Auto-generated and up-to-date  
✅ hotspeech.install - Post-install instructions  
✅ hotspeech.service - Systemd service configuration  
✅ hotspeech.desktop - Desktop file with actions

**Ready for AUR submission!**
