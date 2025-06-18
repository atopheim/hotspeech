#!/bin/bash
# Script to test AUR package build locally

set -e

echo "🧪 TESTING AUR PACKAGE BUILD LOCALLY"
echo "===================================="
echo

# Check if we're in the right directory
if [ ! -f "PKGBUILD" ]; then
    echo "❌ Error: PKGBUILD not found. Run this script from the project root."
    exit 1
fi

# Create a temporary build directory
BUILD_DIR="/tmp/hotspeech-aur-test"
echo "📁 Creating build directory: $BUILD_DIR"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy all necessary files to build directory
echo "📋 Copying files to build directory..."
cp PKGBUILD "$BUILD_DIR/"
cp hotspeech.install "$BUILD_DIR/"

# Create the source directory structure that matches GitHub release
SOURCE_DIR="$BUILD_DIR/hotspeech-1.0.0"
mkdir -p "$SOURCE_DIR"

# Copy all source files to the source directory
cp -r hotspeech "$SOURCE_DIR/"
cp hotspeech-setup "$SOURCE_DIR/"
cp start_recording.sh "$SOURCE_DIR/"
cp stop_recording.sh "$SOURCE_DIR/"
cp hotspeech.desktop "$SOURCE_DIR/"
cp README.md "$SOURCE_DIR/"
cp LICENSE "$SOURCE_DIR/"

# Copy pyproject.toml to the source directory
cp hotspeech/pyproject.toml "$SOURCE_DIR/"

# Create a proper source tarball
echo "📦 Creating source tarball for testing..."
cd "$BUILD_DIR"
tar -czf hotspeech-1.0.0.tar.gz hotspeech-1.0.0/

# Update PKGBUILD to use local tarball
echo "⚙️  Updating PKGBUILD for local testing..."
sed -i 's|source=.*|source=("hotspeech-1.0.0.tar.gz")|' PKGBUILD

echo
echo "🔨 BUILDING PACKAGE..."
echo "====================="

# Build the package
if makepkg -f --noconfirm; then
    echo
    echo "✅ PACKAGE BUILT SUCCESSFULLY!"
    echo
    
    # List the built package
    PACKAGE_FILE=$(ls hotspeech-*.pkg.tar.* 2>/dev/null | head -1)
    if [ -n "$PACKAGE_FILE" ]; then
        echo "📦 Built package: $PACKAGE_FILE"
        echo "   Size: $(du -h "$PACKAGE_FILE" | cut -f1)"
        echo
        
        # Show package contents
        echo "📋 Package contents:"
        tar -tf "$PACKAGE_FILE" | head -20
        if [ $(tar -tf "$PACKAGE_FILE" | wc -l) -gt 20 ]; then
            echo "   ... and $(( $(tar -tf "$PACKAGE_FILE" | wc -l) - 20 )) more files"
        fi
        echo
        
        # Ask if user wants to install for testing
        echo "🤔 Would you like to install this package for testing?"
        echo "   This will install hotspeech system-wide on your machine."
        echo "   You can uninstall it later with: sudo pacman -R hotspeech"
        echo
        read -p "Install package for testing? [y/N] " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "📥 Installing package..."
            sudo pacman -U "$PACKAGE_FILE" --noconfirm
            echo
            echo "✅ PACKAGE INSTALLED!"
            echo
            echo "🧪 Now you can test it:"
            echo "   1. Run: hotspeech-setup"
            echo "   2. Test: hotspeech --help"
            echo "   3. Test: hotspeech daemon"
            echo
            echo "🗑️  To uninstall later:"
            echo "   sudo pacman -R hotspeech"
        else
            echo "📦 Package built but not installed."
            echo "   You can install it manually later with:"
            echo "   sudo pacman -U $BUILD_DIR/$PACKAGE_FILE"
        fi
    fi
else
    echo
    echo "❌ PACKAGE BUILD FAILED!"
    echo "Check the error messages above."
    exit 1
fi

echo
echo "🧹 Cleaning up..."
echo "Build directory: $BUILD_DIR"
echo "You can remove it with: rm -rf $BUILD_DIR" 