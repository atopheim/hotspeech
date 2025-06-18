#!/usr/bin/env python3
"""
Hotspeech CLI - Command line interface for managing recordings
"""

import os
import sys
import argparse
import toml
from datetime import datetime

# Handle imports for both local and installed versions
try:
    # Try system installation imports first
    from hotspeech.app.db import Database
except ImportError:
    # Fall back to local imports
    from app.db import Database

# Config file locations (in order of preference)
CONFIG_PATHS = [
    os.path.expanduser("~/.config/hotspeech/config.toml"),  # User config
    "/etc/hotspeech/config.toml",  # System config
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "config.toml"
    ),  # Local config
]


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


def list_recordings(db, limit=None):
    """List recent recordings"""
    recordings = db.get_recent_recordings(limit or 10)

    if not recordings:
        print("No recordings found.")
        return

    print(f"Recent recordings (showing {len(recordings)}):")
    print("-" * 80)

    for recording in recordings:
        timestamp = datetime.fromisoformat(recording["timestamp"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        status = "✅" if recording["status"] == "success" else "❌"

        print(f"{status} {timestamp}")
        print(f"   File: {recording['audio_path']}")
        if recording["transcription"]:
            # Truncate long transcriptions
            text = recording["transcription"]
            if len(text) > 100:
                text = text[:97] + "..."
            print(f"   Text: {text}")
        else:
            print(f"   Error: {recording['error_message'] or 'Unknown error'}")
        print()


def show_recording(db, recording_id):
    """Show details of a specific recording"""
    recording = db.get_recording(recording_id)

    if not recording:
        print(f"Recording with ID {recording_id} not found.")
        return

    timestamp = datetime.fromisoformat(recording["timestamp"]).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    status = "✅ Success" if recording["status"] == "success" else "❌ Failed"

    print(f"Recording ID: {recording['id']}")
    print(f"Timestamp: {timestamp}")
    print(f"Status: {status}")
    print(f"Audio file: {recording['audio_path']}")
    print(f"Model used: {recording['model_used']}")
    print()

    if recording["transcription"]:
        print("Transcription:")
        print("-" * 40)
        print(recording["transcription"])
    else:
        print(f"Error: {recording['error_message'] or 'Unknown error'}")


def delete_recording(db, recording_id):
    """Delete a recording"""
    recording = db.get_recording(recording_id)

    if not recording:
        print(f"Recording with ID {recording_id} not found.")
        return

    # Delete audio file if it exists
    if os.path.exists(recording["audio_path"]):
        try:
            os.remove(recording["audio_path"])
            print(f"Deleted audio file: {recording['audio_path']}")
        except OSError as e:
            print(f"Warning: Could not delete audio file: {e}")

    # Delete from database
    db.delete_recording(recording_id)
    print(f"Deleted recording ID {recording_id}")


def cleanup_old_recordings(db, keep_last_n):
    """Clean up old recordings"""
    deleted_paths = db.cleanup_old_recordings(keep_last_n)

    if not deleted_paths:
        print("No old recordings to clean up.")
        return

    print(f"Cleaned up {len(deleted_paths)} old recordings:")

    # Delete audio files
    for path in deleted_paths:
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"  Deleted: {path}")
            except OSError as e:
                print(f"  Warning: Could not delete {path}: {e}")
        else:
            print(f"  Already gone: {path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Hotspeech CLI - Manage voice recordings"
    )
    parser.add_argument("--config", help="Path to config file")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List command
    list_parser = subparsers.add_parser("list", help="List recent recordings")
    list_parser.add_argument(
        "--limit", "-n", type=int, help="Number of recordings to show"
    )

    # Show command
    show_parser = subparsers.add_parser("show", help="Show details of a recording")
    show_parser.add_argument("id", type=int, help="Recording ID")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a recording")
    delete_parser.add_argument("id", type=int, help="Recording ID")

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old recordings")
    cleanup_parser.add_argument(
        "--keep",
        "-k",
        type=int,
        default=50,
        help="Number of recent recordings to keep (default: 50)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Load configuration
    config = load_config(args.config)

    # Initialize database
    db = Database(os.path.expanduser(config["storage"]["sqlite_path"]))

    # Handle commands
    if args.command == "list":
        list_recordings(db, args.limit)
    elif args.command == "show":
        show_recording(db, args.id)
    elif args.command == "delete":
        delete_recording(db, args.id)
    elif args.command == "cleanup":
        cleanup_old_recordings(db, args.keep)


if __name__ == "__main__":
    main()
