# Testing Hotspeech AUR Package Locally

This guide shows you how to test the AUR package build locally before uploading to AUR.

## Prerequisites

Make sure you have the required tools installed:

```bash
# Install base-devel group (includes makepkg)
sudo pacman -S base-devel

# Install Python build tools
sudo pacman -S python-build python-installer python-wheel
```

## Quick Test (Automated)

Run the automated test script:

```bash
./test-aur-build.sh
```

This script will:

1. Create a temporary build directory
2. Copy all necessary files
3. Create a fake source tarball
4. Build the package using `makepkg`
5. Optionally install it for testing
6. Show you the package contents

## Manual Testing Steps

### 1. Prepare Build Environment

```bash
# Create a clean build directory
mkdir -p /tmp/hotspeech-test
cd /tmp/hotspeech-test

# Copy necessary files from your project
cp /path/to/your/project/PKGBUILD .
cp /path/to/your/project/hotspeech.install .
cp -r /path/to/your/project/hotspeech .
cp /path/to/your/project/hotspeech-setup .
cp /path/to/your/project/*.sh .
cp /path/to/your/project/hotspeech.desktop .
cp /path/to/your/project/README.md .
cp /path/to/your/project/LICENSE .
```

### 2. Create Source Tarball

Since we don't have a real GitHub release yet, create a fake tarball:

```bash
tar -czf hotspeech-1.0.0.tar.gz hotspeech/ hotspeech-setup *.sh hotspeech.desktop README.md LICENSE

# Update PKGBUILD to use local tarball
sed -i 's|source=.*|source=("hotspeech-1.0.0.tar.gz")|' PKGBUILD
```

### 3. Build the Package

```bash
# Build the package
makepkg -f

# Check if build succeeded
ls -la hotspeech-*.pkg.tar.*
```

### 4. Inspect Package Contents

```bash
# List package contents
PACKAGE=$(ls hotspeech-*.pkg.tar.* | head -1)
tar -tf "$PACKAGE"

# Check package info
pacman -Qip "$PACKAGE"
```

### 5. Install and Test

```bash
# Install the package
sudo pacman -U hotspeech-*.pkg.tar.*

# Test the installation
hotspeech --help
hotspeech-setup --help
hotspeech-cli --help

# Run the installation test
/usr/share/hotspeech/test-installation.sh  # if included
```

## Testing Checklist

After installation, verify these work:

### ✅ Basic Commands

- [ ] `hotspeech --help` shows help
- [ ] `hotspeech-cli --help` shows help
- [ ] `hotspeech-setup` runs without errors

### ✅ File Installation

- [ ] `/usr/bin/hotspeech` exists and is executable
- [ ] `/usr/bin/hotspeech-cli` exists and is executable
- [ ] `/usr/bin/hotspeech-setup` exists and is executable
- [ ] `/etc/hotspeech/config.toml` exists
- [ ] `/usr/share/doc/hotspeech/README.md` exists
- [ ] `/usr/share/applications/hotspeech.desktop` exists

### ✅ Configuration Setup

- [ ] `hotspeech-setup` creates `~/.config/hotspeech/config.toml`
- [ ] Config file has correct paths
- [ ] API key can be set and saved

### ✅ Functionality

- [ ] `hotspeech daemon` starts without errors
- [ ] Web interface accessible at http://localhost:8080
- [ ] `hotspeech record` starts recording (if you have a mic)
- [ ] `hotspeech stop` stops recording

### ✅ Dependencies

- [ ] All Python dependencies are installed
- [ ] ffmpeg is available
- [ ] Clipboard tools work (wl-clipboard/xclip)

## Common Issues and Fixes

### Build Fails with "No such file or directory"

- Make sure all files are copied to the build directory
- Check that file permissions are correct (`chmod +x` for scripts)

### Python Import Errors

- Verify all dependencies are listed in `pyproject.toml`
- Check that the package structure is correct

### Config File Not Found

- Ensure `/etc/hotspeech/config.toml` is installed
- Check that `hotspeech-setup` can find and copy it

### Commands Not Found

- Verify scripts are installed to `/usr/bin/`
- Check that they have execute permissions

## Cleanup After Testing

```bash
# Uninstall the package
sudo pacman -R hotspeech

# Remove build directory
rm -rf /tmp/hotspeech-test

# Remove user config (optional)
rm -rf ~/.config/hotspeech
rm -rf ~/.local/share/hotspeech
```

## Before Uploading to AUR

1. ✅ All tests pass
2. ✅ Package builds cleanly
3. ✅ All files are installed correctly
4. ✅ Post-install script works
5. ✅ Setup script works
6. ✅ Basic functionality works
7. ✅ Documentation is complete

## Upload to AUR

Once testing is complete:

1. Create a GitHub release with the source code
2. Update PKGBUILD with real GitHub URL and sha256sum
3. Create AUR repository: `git clone ssh://aur@aur.archlinux.org/hotspeech.git`
4. Copy PKGBUILD and .install file to AUR repo
5. Commit and push: `git add .; git commit -m "Initial commit"; git push`

## Updating the Package

For updates:

1. Update version in PKGBUILD and pyproject.toml
2. Create new GitHub release
3. Update sha256sum in PKGBUILD
4. Test locally again
5. Push to AUR
