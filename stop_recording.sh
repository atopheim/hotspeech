#!/bin/bash
# Simple script to stop recording
# Use this path in your hotkey configuration

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Run the stop command
cd "$SCRIPT_DIR/hotspeech"
python3 main.py stop