"""
Clipboard functionality for Hotspeech
"""

import subprocess
from typing import Optional


class Clipboard:
    """Clipboard handler for copying transcriptions"""

    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """
        Copy text to clipboard using wl-copy for Wayland or xclip for X11
        Returns: True if successful, False otherwise
        """
        if not text:
            return False

        try:
            # Try wl-copy first (Wayland)
            subprocess.run(["wl-copy"], input=text.encode(), check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            try:
                # Fall back to xclip (X11)
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text.encode(),
                    check=True,
                )
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                return False

    @staticmethod
    def get_clipboard_content() -> Optional[str]:
        """
        Get text from clipboard using wl-paste or xclip
        Returns: Clipboard content or None if failed
        """
        try:
            # Try wl-paste first (Wayland)
            result = subprocess.run(
                ["wl-paste"], capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                return result.stdout
        except FileNotFoundError:
            pass

        try:
            # Fall back to xclip (X11)
            result = subprocess.run(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return result.stdout
        except FileNotFoundError:
            pass

        return None
