#!/bin/bash

echo "🔍 AUR Package Verification for hotspeech"
echo "=========================================="
echo ""

cd aur-package || exit 1

echo "📋 1. File Structure Check:"
required_files=("PKGBUILD" ".SRCINFO" "hotspeech.install" "hotspeech.service" "hotspeech.desktop")
for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file missing"
        exit 1
    fi
done

echo ""
echo "📦 2. PKGBUILD Syntax Check:"
if bash -n PKGBUILD; then
    echo "   ✅ Valid bash syntax"
else
    echo "   ❌ Syntax error"
    exit 1
fi

echo ""
echo "🔗 3. Source URL Test:"
source_url="https://github.com/atopheim/hotspeech/archive/v1.0.0.tar.gz"
response=$(curl -s --head "$source_url" | head -1)
if echo "$response" | grep -q -E "(200 OK|302)"; then
    echo "   ✅ Source accessible: $source_url"
else
    echo "   ❌ Source not accessible: $source_url"
    exit 1
fi

echo ""
echo "🔢 4. SHA256 Checksum Verification:"
expected=$(grep "sha256sums=" PKGBUILD | sed "s/.*'\(.*\)'.*/\1/")
actual=$(curl -sL "$source_url" | sha256sum | cut -d' ' -f1)
if [[ "$expected" == "$actual" ]]; then
    echo "   ✅ Checksum matches: $expected"
else
    echo "   ❌ Checksum mismatch!"
    echo "      Expected: $expected"
    echo "      Actual:   $actual"
    exit 1
fi

echo ""
echo "📄 5. .SRCINFO Consistency:"
temp_srcinfo=$(mktemp)
makepkg --printsrcinfo > "$temp_srcinfo" 2>/dev/null
if diff -q .SRCINFO "$temp_srcinfo" >/dev/null; then
    echo "   ✅ .SRCINFO is up to date"
else
    echo "   ❌ .SRCINFO is outdated"
    rm "$temp_srcinfo"
    exit 1
fi
rm "$temp_srcinfo"

echo ""
echo "📋 6. Package Metadata Check:"
pkgname=$(grep "^pkgname=" PKGBUILD | cut -d'=' -f2 | tr -d '"')
pkgver=$(grep "^pkgver=" PKGBUILD | cut -d'=' -f2 | tr -d '"')
maintainer=$(grep "^# Maintainer:" PKGBUILD | cut -d':' -f2 | xargs)
echo "   📦 Package: $pkgname"
echo "   🏷️  Version: $pkgver"
echo "   👤 Maintainer: $maintainer"

echo ""
echo "🎉 All verification checks passed!"
echo ""
echo "✅ Package is ready for AUR submission"
echo ""
echo "Next steps:"
echo "1. Register at AUR: https://aur.archlinux.org/register/"
echo "2. Upload SSH key to your AUR account"
echo "3. Clone AUR repo: git clone ssh://aur@aur.archlinux.org/hotspeech.git"
echo "4. Copy files and submit" 