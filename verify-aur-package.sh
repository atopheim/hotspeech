#!/bin/bash

echo "🔍 Verifying AUR package for hotspeech..."
echo "==========================================="

cd aur-package || { echo "❌ aur-package directory not found"; exit 1; }

# Check required files exist
required_files=("PKGBUILD" ".SRCINFO" "hotspeech.install" "hotspeech.service" "hotspeech.desktop")
for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

echo ""
echo "📋 Checking PKGBUILD metadata..."

# Extract key values from PKGBUILD
pkgname=$(grep "^pkgname=" PKGBUILD | cut -d'=' -f2 | tr -d '"')
pkgver=$(grep "^pkgver=" PKGBUILD | cut -d'=' -f2 | tr -d '"')
pkgdesc=$(grep "^pkgdesc=" PKGBUILD | cut -d'=' -f2 | tr -d '"')
maintainer=$(grep "^# Maintainer:" PKGBUILD | cut -d':' -f2 | xargs)

echo "📦 Package: $pkgname"
echo "🏷️  Version: $pkgver"  
echo "📝 Description: $pkgdesc"
echo "👤 Maintainer: $maintainer"

echo ""
echo "🔗 Verifying source URL and checksum..."

# Build the actual source URL by expanding variables
source_url="https://github.com/atopheim/$pkgname/archive/v$pkgver.tar.gz"

if curl -s --head "$source_url" | head -n 1 | grep -q -E "(200 OK|302)"; then
    echo "✅ Source URL accessible: $source_url"
else
    echo "❌ Source URL not accessible: $source_url"
    exit 1
fi

# Verify checksum
expected_sum=$(grep "^sha256sums=" PKGBUILD | sed "s/.*'\(.*\)'.*/\1/")
actual_sum=$(curl -sL "$source_url" | sha256sum | cut -d' ' -f1)

if [[ "$expected_sum" == "$actual_sum" ]]; then
    echo "✅ SHA256 checksum matches: $expected_sum"
else
    echo "❌ SHA256 checksum mismatch!"
    echo "   Expected: $expected_sum"
    echo "   Actual:   $actual_sum"
    exit 1
fi

echo ""
echo "📋 Checking .SRCINFO consistency..."

# Verify .SRCINFO is up to date
temp_srcinfo=$(mktemp)
makepkg --printsrcinfo > "$temp_srcinfo" 2>/dev/null

if diff -q .SRCINFO "$temp_srcinfo" >/dev/null; then
    echo "✅ .SRCINFO is up to date"
else
    echo "❌ .SRCINFO is outdated. Run: makepkg --printsrcinfo > .SRCINFO"
    rm "$temp_srcinfo"
    exit 1
fi
rm "$temp_srcinfo"

echo ""
echo "🏗️  Testing package build (dry run)..."

# Test if package would build (without actually building)
if makepkg --nobuild --syncdeps --noconfirm 2>/dev/null; then
    echo "✅ Package build test passed"
    # Clean up any downloaded sources
    [[ -d src ]] && rm -rf src
else
    echo "❌ Package build test failed"
    exit 1
fi

echo ""
echo "🎉 All checks passed! Package is ready for AUR submission."
echo ""
echo "Next steps:"
echo "1. Register/login to AUR: https://aur.archlinux.org/"
echo "2. Upload SSH key to your AUR account"
echo "3. Clone AUR repo: git clone ssh://aur@aur.archlinux.org/hotspeech.git"
echo "4. Copy files and submit following AUR_SUBMISSION_GUIDE.md" 