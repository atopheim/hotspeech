#!/bin/bash
# Test script to verify Hotspeech installation

echo "🧪 TESTING HOTSPEECH INSTALLATION"
echo "================================="
echo

# Test 1: Check if hotspeech command exists
echo "1. Testing hotspeech command..."
if command -v hotspeech &> /dev/null; then
    echo "   ✅ hotspeech command found"
else
    echo "   ❌ hotspeech command not found"
    exit 1
fi

# Test 2: Check if hotspeech-cli command exists
echo "2. Testing hotspeech-cli command..."
if command -v hotspeech-cli &> /dev/null; then
    echo "   ✅ hotspeech-cli command found"
else
    echo "   ❌ hotspeech-cli command not found"
    exit 1
fi

# Test 3: Check if hotspeech-setup command exists
echo "3. Testing hotspeech-setup command..."
if command -v hotspeech-setup &> /dev/null; then
    echo "   ✅ hotspeech-setup command found"
else
    echo "   ❌ hotspeech-setup command not found"
    exit 1
fi

# Test 4: Check if config template exists
echo "4. Testing system config template..."
if [ -f "/etc/hotspeech/config.toml" ]; then
    echo "   ✅ System config template found"
else
    echo "   ❌ System config template not found"
    exit 1
fi

# Test 5: Check if documentation exists
echo "5. Testing documentation..."
if [ -f "/usr/share/doc/hotspeech/README.md" ]; then
    echo "   ✅ Documentation found"
else
    echo "   ❌ Documentation not found"
    exit 1
fi

# Test 6: Check dependencies
echo "6. Testing dependencies..."
if command -v python3 &> /dev/null; then
    echo "   ✅ Python 3 found"
else
    echo "   ❌ Python 3 not found"
    exit 1
fi

if command -v ffmpeg &> /dev/null; then
    echo "   ✅ ffmpeg found"
else
    echo "   ⚠️  ffmpeg not found (required for recording)"
fi

# Test 7: Test help output
echo "7. Testing help output..."
if hotspeech --help &> /dev/null; then
    echo "   ✅ Help command works"
else
    echo "   ❌ Help command failed"
    exit 1
fi

echo
echo "🎉 ALL TESTS PASSED!"
echo
echo "Next steps:"
echo "1. Run: hotspeech-setup"
echo "2. Configure your hotkeys"
echo "3. Start using: hotspeech daemon" 