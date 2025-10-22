"""
Audio recording functionality for Hotspeech
"""

import os
import time
import subprocess
import tempfile
import wave
import threading
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Callable

# Global recording state
recording_process = None
recording_thread = None
output_file_path = None
notification_process = None


class AudioRecorder:
    def __init__(self, config):
        self.output_format = config["recording"]["output_format"]
        self.max_duration = config["recording"]["max_duration_seconds"]
        self.audio_dir = os.path.expanduser(config["recording"]["audio_dir"])

        # Create audio directory if it doesn't exist
        os.makedirs(self.audio_dir, exist_ok=True)

    def _get_recording_filename(self) -> str:
        """Generate a filename for a new recording"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(
            self.audio_dir, f"recording_{timestamp}.{self.output_format}"
        )

    def start_recording(self) -> Tuple[str, subprocess.Popen]:
        """
        Start recording audio using ffmpeg
        Returns the output filename and the process object
        """
        output_file = self._get_recording_filename()

        # More verbose debug info
        print(f"DEBUG: Starting recording to {output_file}")
        print(f"DEBUG: Using PipeWire/PulseAudio for recording")

        # Get available audio input devices
        try:
            device_list = subprocess.check_output(
                ["pactl", "list", "sources", "short"], universal_newlines=True
            ).strip()
            print(f"DEBUG: Available audio sources:\n{device_list}")
        except Exception as e:
            print(f"DEBUG: Failed to list audio sources: {e}")

        # Try to use a specific audio input source instead of "default"
        # This can help with PipeWire/PulseAudio compatibility
        # Use the default source reported by PulseAudio
        try:
            # Fixed the shell command - don't use subprocess with shell=True and pipes
            default_source_output = subprocess.check_output(
                ["pactl", "info"], universal_newlines=True
            )
            # Parse the output to find the default source
            for line in default_source_output.split("\n"):
                if "Default Source:" in line:
                    default_source = line.split(":", 1)[1].strip()
                    break
            else:
                # If not found, try to get the first available input source
                sources_output = subprocess.check_output(
                    ["pactl", "list", "sources", "short"], universal_newlines=True
                )
                for line in sources_output.split("\n"):
                    if (
                        line.strip()
                        and not line.startswith("No valid command")
                        and "input" in line.lower()
                    ):
                        parts = line.split()
                        if len(parts) >= 2:
                            default_source = parts[1]
                            break
                else:
                    default_source = "default"

            print(f"DEBUG: Default audio source: {default_source}")
        except Exception as e:
            print(f"DEBUG: Failed to get default source, will use 'default': {e}")
            default_source = "default"

        # Use ffmpeg to record audio from the default input device
        cmd = [
            "ffmpeg",
            "-f",
            "pulse",  # Audio backend for Linux
            "-i",
            default_source,  # Use the actual default source device
            "-acodec",
            "pcm_s16le" if self.output_format == "wav" else "flac",
            "-ar",
            "44100",  # Sample rate
            "-ac",
            "2",  # Number of channels
            "-y",  # Overwrite output file
            output_file,
        ]

        print(f"DEBUG: ffmpeg command: {' '.join(cmd)}")

        # Start the recording process
        process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        print(f"DEBUG: ffmpeg process started with PID {process.pid}")
        return output_file, process

    def stop_recording(self, process: subprocess.Popen) -> None:
        """Stop the recording process by sending 'q' to ffmpeg"""
        if process and process.poll() is None:
            try:
                process.communicate(input=b"q", timeout=2)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=2)

    def record_audio(self) -> Optional[str]:
        """
        Record audio for up to max_duration seconds or until stopped
        Returns the path to the recorded audio file or None if failed
        """
        try:
            output_file, process = self.start_recording()

            # Wait for max_duration or until manually stopped
            start_time = time.time()
            while (
                process.poll() is None and time.time() - start_time < self.max_duration
            ):
                time.sleep(0.1)

            # Stop recording if it's still going
            if process.poll() is None:
                self.stop_recording(process)

            # Check if the file was created successfully
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                return output_file
            else:
                return None

        except Exception as e:
            print(f"Error recording audio: {e}")
            return None

    def play_audio(self, audio_path: str) -> bool:
        """Play an audio file using ffplay"""
        try:
            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", audio_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except Exception as e:
            print(f"Error playing audio: {e}")
            return False


def show_recording_notification():
    """Show a notification with recording status and stop button"""
    global notification_process

    print("DEBUG: Attempting to show recording notification")

    # Try multiple notification methods to ensure at least one works
    notification_shown = False

    # Method 1: Try zenity
    try:
        print("DEBUG: Trying zenity notification")
        # Use a more attention-grabbing zenity dialog
        cmd = [
            "zenity",
            "--warning",
            "--title=RECORDING IN PROGRESS",
            "--text=Recording audio... Click OK to stop recording.",
            "--ok-label=Stop Recording",
            "--width=400",
            "--timeout=0",
            "--default-cancel",
        ]

        notification_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print(f"DEBUG: Zenity process started with PID {notification_process.pid}")
        notification_shown = True
    except Exception as e:
        print(f"DEBUG: Zenity notification failed: {e}")

    # Method 2: Try notify-send
    try:
        print("DEBUG: Trying notify-send notification")
        result = subprocess.run(
            [
                "notify-send",
                "-u",
                "critical",
                "-t",
                "0",
                "RECORDING IN PROGRESS",
                "Recording audio... Press Ctrl+Alt+W to stop.",
            ]
        )
        print(f"DEBUG: notify-send result: {result.returncode}")
        notification_shown = True
    except Exception as e:
        print(f"DEBUG: notify-send failed: {e}")

    # Method 3: Try xmessage as last resort
    if not notification_shown:
        try:
            print("DEBUG: Trying xmessage notification")
            subprocess.Popen(
                [
                    "xmessage",
                    "-center",
                    "RECORDING IN PROGRESS. Press Ctrl+Alt+W to stop.",
                ]
            )
        except Exception as e:
            print(f"DEBUG: xmessage also failed: {e}")

    return notification_process


def start_recording_with_ui(
    recorder, on_complete: Callable[[str], None] = None
) -> None:
    """
    Start recording with a UI notification, returns the recording path when stopped
    The on_complete callback is called with the recording path when finished
    """
    global recording_process, recording_thread, output_file_path, notification_process

    def recording_thread_func():
        global recording_process, output_file_path, notification_process

        try:
            # Start recording
            output_file, process = recorder.start_recording()
            recording_process = process
            output_file_path = output_file

            # Show notification that allows stopping
            print("DEBUG: About to show notification")
            notification_proc = show_recording_notification()
            print(f"DEBUG: Notification process: {notification_proc}")

            # Print confirmation to terminal
            print("\n\n*** RECORDING STARTED ***")
            print(f"Recording to: {output_file}")
            print("Press Ctrl+Alt+W to stop recording")
            print("**********************\n")

            # Monitor both the recording process and notification
            counter = 0
            while recording_process and recording_process.poll() is None:
                # Every 10 iterations, print recording status
                if counter % 10 == 0:
                    print(f"DEBUG: Recording in progress ({counter / 10}s)...")
                    if notification_proc:
                        print(f"DEBUG: Notification status: {notification_proc.poll()}")

                # If notification was closed, stop recording
                if notification_proc and notification_proc.poll() is not None:
                    print("DEBUG: Notification was closed, stopping recording")
                    recorder.stop_recording(recording_process)
                    break

                time.sleep(0.1)
                counter += 1

            # Check if recording completed successfully
            print(f"DEBUG: Recording stopped, checking file {output_file}")
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                file_size = os.path.getsize(output_file)
                print(f"DEBUG: Recorded file size: {file_size} bytes")

                # Print confirmation to terminal
                print("\n*** RECORDING STOPPED ***")
                print(f"Recording saved to: {output_file}")
                print("**********************\n")

                # Call the callback with the recording path
                if on_complete:
                    print("DEBUG: Calling on_complete callback")
                    on_complete(output_file)
            else:
                print(
                    f"DEBUG: Recording failed or was empty (file exists: {os.path.exists(output_file)})"
                )
                if on_complete:
                    on_complete(None)

        except Exception as e:
            print(f"DEBUG: Error in recording thread: {str(e)}")
            import traceback

            traceback.print_exc()
            if on_complete:
                on_complete(None)
        finally:
            print("DEBUG: Recording thread cleanup")
            # Ensure all processes are properly cleaned up
            if recording_process and recording_process.poll() is None:
                try:
                    recording_process.terminate()
                    recording_process.wait(timeout=2)
                except Exception as e:
                    print(f"DEBUG: Error cleaning up recording process: {e}")

            if notification_process and notification_process.poll() is None:
                try:
                    notification_process.terminate()
                    notification_process.wait(timeout=1)
                except Exception as e:
                    print(f"DEBUG: Error cleaning up notification process: {e}")

            recording_process = None
            recording_thread = None
            notification_process = None

    # Don't start if already recording
    if recording_thread and recording_thread.is_alive():
        print("Already recording")
        return

    # Start the recording thread - REMOVED daemon=True to fix shutdown crash
    recording_thread = threading.Thread(target=recording_thread_func)
    # recording_thread.daemon = True  # REMOVED: This causes the fatal error
    recording_thread.start()


def stop_recording_from_hotkey() -> bool:
    """Stop the current recording from a hotkey press"""
    global recording_process, notification_process

    print("DEBUG: stop_recording_from_hotkey called")
    print(
        f"DEBUG: recording_process={recording_process}, notification_process={notification_process}"
    )

    if recording_process and recording_process.poll() is None:
        try:
            print("DEBUG: Attempting to stop recording process")
            # Send the 'q' key to ffmpeg to stop recording
            recording_process.communicate(input=b"q", timeout=2)
            print("DEBUG: Successfully sent stop signal to recording process")

            # Close notification if it exists
            if notification_process and notification_process.poll() is None:
                print("DEBUG: Terminating notification_process")
                notification_process.terminate()
                print("DEBUG: Notification process terminated")

            # Show notification that recording stopped
            try:
                print("DEBUG: Sending 'recording stopped' notification")
                subprocess.run(
                    [
                        "notify-send",
                        "-u",
                        "normal",
                        "-t",
                        "5000",
                        "Recording Stopped",
                        "Audio recording has been stopped and saved.",
                    ]
                )
                print("DEBUG: 'Recording stopped' notification sent")
            except Exception as e:
                print(f"DEBUG: Failed to send 'recording stopped' notification: {e}")

            return True
        except Exception as e:
            print(f"DEBUG: Error stopping recording: {e}")
            return False

    print("DEBUG: No active recording found to stop")
    return False
