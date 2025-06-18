#!/usr/bin/env python3
"""
Hotspeech - Voice recording, transcription and clipboard integration
"""

import os
import sys
import signal
import threading
import time
import argparse
import toml
import subprocess
from threading import Thread
from pathlib import Path

# Handle imports for both local and installed versions
try:
    # Try system installation imports first
    from hotspeech.app.db import Database
    from hotspeech.app.audio import (
        AudioRecorder,
        start_recording_with_ui,
        stop_recording_from_hotkey,
    )
    from hotspeech.app.transcriber import Transcriber
    from hotspeech.app.clipboard import Clipboard
    from hotspeech.app.webui.routes import initialize as init_webui, run_server
except ImportError as e:
    # If system imports fail, check if it's a missing dependency issue
    if "No module named 'openai'" in str(e):
        print("❌ Error: Missing required dependency 'openai'")
        print("This usually means the package wasn't installed with all dependencies.")
        print()
        print("💡 If you installed via AUR:")
        print("   The python-openai dependency should be installed automatically.")
        print("   Try reinstalling: yay -S hotspeech")
        print()
        print("💡 If you're running locally:")
        print(
            "   Install dependencies: pip install openai toml flask requests sounddevice numpy scipy"
        )
        sys.exit(1)
    elif "No module named 'flask'" in str(e):
        print("❌ Error: Missing required dependency 'flask'")
        print("Install with: pip install flask")
        sys.exit(1)
    else:
        # Try fall back to local imports for development
        try:
            from app.db import Database
            from app.audio import (
                AudioRecorder,
                start_recording_with_ui,
                stop_recording_from_hotkey,
            )
            from app.transcriber import Transcriber
            from app.clipboard import Clipboard
            from app.webui.routes import initialize as init_webui, run_server
        except ImportError as local_e:
            print("❌ Error: Could not import hotspeech modules")
            print(f"System import error: {e}")
            print(f"Local import error: {local_e}")
            print()
            print("💡 Make sure hotspeech is properly installed:")
            print("   - Via AUR: yay -S hotspeech")
            print("   - Or run from project directory with dependencies installed")
            sys.exit(1)

# Config file locations (in order of preference)
CONFIG_PATHS = [
    os.path.expanduser("~/.config/hotspeech/config.toml"),  # User config
    "/etc/hotspeech/config.toml",  # System config
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "config.toml"
    ),  # Local config
]

# Global flag to prevent reentrant signal handling
_shutting_down = False


def find_config_file():
    """Find the first available config file"""
    for path in CONFIG_PATHS:
        if os.path.exists(path):
            return path
    return None


def load_config(config_path=None):
    """Load configuration from TOML file"""
    if config_path is None:
        config_path = find_config_file()

    if not config_path or not os.path.exists(config_path):
        print("❌ Error: No config file found!")
        print("Expected locations:")
        for path in CONFIG_PATHS:
            print(f"   {path}")
        print()
        print("💡 If you installed via AUR, run: hotspeech-setup")
        print("💡 Otherwise, copy config.toml to one of the above locations")
        sys.exit(1)

    try:
        with open(config_path, "r") as f:
            config = toml.load(f)
        return config
    except Exception as e:
        print(f"Error loading config from {config_path}: {str(e)}")
        sys.exit(1)


def display_program_info():
    """Display program location and command paths for manual hotkey setup"""
    script_path = os.path.abspath(__file__)

    # Check if we're running from system installation
    if script_path.startswith("/usr/bin/"):
        # System installation
        print("=" * 70)
        print("🎤 HOTSPEECH - Voice Recording & Transcription")
        print("=" * 70)
        print()
        print("📁 SYSTEM INSTALLATION DETECTED")
        print("   Installed via package manager (AUR)")
        print()
        print("🔥 HOTKEY COMMANDS:")
        print("   Start Recording: hotspeech record")
        print("   Stop Recording:  hotspeech stop")
        print("   Quick Note:      hotspeech record --quiet")
        print()
        print("⚙️  SETUP HOTKEYS:")
        print("   Use your desktop environment's hotkey settings")
        print("   Commands are simple: 'hotspeech record' and 'hotspeech stop'")
        print("   Suggested hotkeys: Ctrl+Shift+R (start), Ctrl+Shift+Q (stop)")
        print()
        print("🌐 WEB INTERFACE:")
        print("   http://localhost:8080")
        print()
        print("⚙️  CONFIGURATION:")
        config_file = find_config_file()
        if config_file:
            print(f"   Config file: {config_file}")
        print("   Run 'hotspeech-setup' to configure API key")
        print()
        print("📖 Documentation: /usr/share/doc/hotspeech/README.md")
    else:
        # Local installation
        script_dir = os.path.dirname(script_path)
        root_dir = os.path.dirname(script_dir)

        print("=" * 70)
        print("🎤 HOTSPEECH - Voice Recording & Transcription")
        print("=" * 70)
        print()
        print("📁 LOCAL INSTALLATION DETECTED")
        print(f"   Directory: {script_dir}")
        print(f"   Main Script: {script_path}")
        print()
        print("🔥 HOTKEY COMMANDS (choose one method):")
        print()
        print("   METHOD 1 - Direct Python commands:")
        print(f"   Start Recording: python3 {script_path} record")
        print(f"   Stop Recording:  python3 {script_path} stop")
        print(f"   Quick Note:      python3 {script_path} record --quiet")
        print()
        print("   METHOD 2 - Convenient wrapper scripts:")
        print(f"   Start Recording: {root_dir}/start_recording.sh")
        print(f"   Stop Recording:  {root_dir}/stop_recording.sh")
        print()
        print("⚙️  SETUP HOTKEYS:")
        print("   1. Use your desktop environment's hotkey settings")
        print("   2. Use the exact command paths shown above")
        print("   3. Suggested hotkeys: Ctrl+Shift+R (start), Ctrl+Shift+Q (stop)")
        print()
        print("🌐 WEB INTERFACE:")
        print("   http://localhost:8080")
        print()
        print("📖 For detailed setup instructions, see README.md")

    print("=" * 70)
    print()


def record_and_transcribe(config, quiet=False):
    """Record audio, transcribe it, and copy to clipboard"""
    db = Database(os.path.expanduser(config["storage"]["sqlite_path"]))
    recorder = AudioRecorder(config)
    transcriber = Transcriber(config)

    def on_recording_complete(audio_path):
        if not audio_path:
            if not quiet:
                print("Error: Failed to record audio")
            return

        if not quiet:
            print(f"Recorded audio saved to {audio_path}")
            print("Transcribing...")

        # Transcribe the audio
        result = transcriber.transcribe(audio_path)

        # Save to database
        db.add_recording(
            audio_path=audio_path,
            transcription=result["transcription"],
            model_used=result["model_used"],
            status=result["status"],
            error_message=result["error_message"],
        )

        # Clean up old recordings if needed
        deleted_paths = db.cleanup_old_recordings(
            keep_last_n=int(config["storage"]["keep_last_n"])
        )
        for path in deleted_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass

        # Copy to clipboard if transcription successful
        if result["transcription"] and config["clipboard"]["enabled"]:
            Clipboard.copy_to_clipboard(result["transcription"])
            if not quiet:
                print("Transcription copied to clipboard.")

        if not quiet:
            if result["transcription"]:
                print("Transcription:")
                print(result["transcription"])
            else:
                print(f"Transcription failed: {result['error_message']}")

    # Start recording with UI
    if not quiet:
        print(
            "Recording... Press Ctrl+Shift+Q (or your configured stop hotkey) to stop."
        )

    start_recording_with_ui(recorder, on_recording_complete)

    # Return immediately as recording runs in the background
    return True


def stop_recording():
    """Stop an active recording"""
    if stop_recording_from_hotkey():
        print("Recording stopped")
        return True
    else:
        print("No active recording to stop")
        return False


def handle_signal(sig, frame):
    """Handle shutdown signals gracefully"""
    global _shutting_down

    # Prevent reentrant calls
    if _shutting_down:
        return
    _shutting_down = True

    print("\nShutting down Hotspeech...")
    sys.exit(0)


def run_web_server(config):
    """Run the web server in a separate thread"""
    init_webui(config)
    run_server()


def main():
    """Main entry point"""
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    parser = argparse.ArgumentParser(
        description="Hotspeech - Voice recording and transcription"
    )
    parser.add_argument("--config", help="Path to config file")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Record command
    record_parser = subparsers.add_parser("record", help="Record and transcribe audio")
    record_parser.add_argument(
        "--quiet", action="store_true", help="Run without notifications"
    )

    # Stop command
    subparsers.add_parser("stop", help="Stop active recording")

    # Server command
    subparsers.add_parser("server", help="Run the web server")

    # Daemon command
    subparsers.add_parser(
        "daemon",
        help="Run as background daemon (web server only - set up hotkeys manually)",
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    if args.command == "record":
        # Record and transcribe audio
        record_and_transcribe(config, quiet=args.quiet)
    elif args.command == "stop":
        # Stop active recording
        success = stop_recording()
        if success:
            print("Recording stopped")
        else:
            print("No active recording found")
    elif args.command == "server":
        # Run web server
        run_web_server(config)
    elif args.command == "daemon":
        # Display program information for manual hotkey setup
        display_program_info()

        # Start web server - REMOVED daemon=True to fix shutdown crash
        print(
            f"Starting web server on http://{config['webui']['host']}:{config['webui']['port']}..."
        )
        server_thread = Thread(target=run_web_server, args=(config,))
        # server_thread.daemon = True  # REMOVED: This causes shutdown issues
        server_thread.start()

        print("✅ Hotspeech daemon is running!")
        print("   Set up hotkeys manually using the commands shown above.")
        print("   Press Ctrl+C to stop the daemon.")
        print()

        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down Hotspeech...")
            # Give threads time to cleanup gracefully
            server_thread.join(timeout=5)
    else:
        # Default behavior without command: show help and program info
        display_program_info()
        print("USAGE:")
        parser.print_help()


if __name__ == "__main__":
    main()
