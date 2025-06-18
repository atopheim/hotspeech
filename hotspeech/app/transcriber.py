"""
Transcription functionality for Hotspeech using OpenAI Whisper API
"""

import os
import json
import openai
import subprocess
from typing import Dict, Optional, Any, Tuple


class TranscriptionError(Exception):
    """Exception raised for errors in the transcription process."""

    pass


class Transcriber:
    def __init__(self, config):
        self.config = config
        self.backend = config["transcription"]["backend"]
        self.model = config["transcription"]["model"]
        self.fallback_model = config["transcription"]["fallback_model"]
        self.language = config["transcription"]["language"]

        # Configure OpenAI API if using API backend
        if self.backend == "api":
            # Check for API key in config, then in environment variables
            api_key = config["transcription"].get("api_key") or os.environ.get(
                "OPENAI_API_KEY"
            )
            if api_key:
                openai.api_key = api_key

    def _transcribe_api(self, audio_path: str) -> Tuple[str, str]:
        """
        Transcribe audio using OpenAI's Whisper API
        Returns: (transcription text, model used)
        """
        if not openai.api_key:
            raise TranscriptionError("OpenAI API key not set")

        try:
            client = openai.OpenAI(api_key=openai.api_key)
            with open(audio_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language=self.language,
                    response_format="text",
                )

            return response, self.model
        except Exception as e:
            raise TranscriptionError(f"API transcription failed: {str(e)}")

    def _transcribe_local_whisper_cpp(self, audio_path: str) -> Tuple[str, str]:
        """
        Transcribe audio using locally installed whisper.cpp
        Returns: (transcription text, model used)
        """
        try:
            result = subprocess.run(
                [
                    "whisper",
                    "--model",
                    self.fallback_model,
                    "--output-json",
                    "-f",
                    audio_path,
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse JSON output
            output_file = audio_path.rsplit(".", 1)[0] + ".json"
            if os.path.exists(output_file):
                with open(output_file, "r") as f:
                    data = json.load(f)
                    transcription = data.get("text", "")
                return transcription, f"local:{self.fallback_model}"
            else:
                # Fall back to stdout if json not found
                return result.stdout, f"local:{self.fallback_model}"

        except subprocess.CalledProcessError as e:
            raise TranscriptionError(f"Local transcription failed: {e.stderr}")
        except Exception as e:
            raise TranscriptionError(f"Local transcription failed: {str(e)}")

    def transcribe(
        self, audio_path: str, model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using the configured backend
        Returns a dict with transcription, model used, and status
        """
        result = {
            "transcription": None,
            "model_used": model or self.model,
            "status": "error",
            "error_message": None,
        }

        try:
            # Override backend if specific model requested
            if model:
                self.model = model

            # Try primary backend
            if self.backend == "api":
                result["transcription"], result["model_used"] = self._transcribe_api(
                    audio_path
                )
                result["status"] = "done"
            else:
                result["transcription"], result["model_used"] = (
                    self._transcribe_local_whisper_cpp(audio_path)
                )
                result["status"] = "done"

        except TranscriptionError as e:
            result["error_message"] = str(e)

            # Try fallback if primary fails
            try:
                if self.backend == "api":
                    # Fall back to local
                    result["transcription"], result["model_used"] = (
                        self._transcribe_local_whisper_cpp(audio_path)
                    )
                    result["status"] = "done"
                else:
                    # Fall back to API if local fails and API key exists
                    if openai.api_key:
                        result["transcription"], result["model_used"] = (
                            self._transcribe_api(audio_path)
                        )
                        result["status"] = "done"
            except TranscriptionError as fallback_error:
                # Both primary and fallback failed
                result["error_message"] = (
                    f"{str(e)}; Fallback also failed: {str(fallback_error)}"
                )

        return result
