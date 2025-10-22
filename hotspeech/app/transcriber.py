"""
Transcription functionality for Hotspeech using OpenAI Whisper API
"""

import os
import json
import openai
import subprocess
import traceback
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
                
        # Validate and adjust models based on backend
        self._adjust_models_for_backends()
                
    def _adjust_models_for_backends(self):
        """Validate and adjust model settings for different backends"""
        # For API backend, ensure model is a valid OpenAI Whisper model
        if self.backend == "api":
            # If model is set to faster-whisper, adjust to whisper-1
            if self.model.startswith("faster-whisper"):
                print(f"WARNING: Model '{self.model}' is not valid for API backend. Using 'whisper-1' instead.")
                self.model = "whisper-1"
                
        # For local backend, ensure model is a valid faster-whisper format
        elif self.backend == "local":
            # If model doesn't start with faster-whisper, adjust it
            if not self.model.startswith("faster-whisper"):
                if ":" not in self.model:
                    # Default to small.en if no specific model is specified
                    self.model = "faster-whisper:small.en"
                    print(f"WARNING: Using 'faster-whisper:small.en' for local backend.")
                else:
                    # Add the faster-whisper prefix if not present
                    self.model = f"faster-whisper:{self.model}"
                    print(f"WARNING: Adjusted model name to '{self.model}' for local backend.")

    def _get_model_for_backend(self, backend, specified_model=None):
        """Get appropriate model name for the given backend"""
        model_to_use = specified_model or self.model
        
        if backend == "api":
            # For API, ensure it's an OpenAI model
            if model_to_use.startswith("faster-whisper"):
                return "whisper-1"  # Default OpenAI model
            return model_to_use
        else:  # local backend
            # For local, ensure it's a faster-whisper model
            if not model_to_use.startswith("faster-whisper"):
                return "faster-whisper:small.en"  # Default local model
            return model_to_use

    def _transcribe_api(self, audio_path: str) -> Tuple[str, str]:
        """
        Transcribe audio using OpenAI's Whisper API
        Returns: (transcription text, model used)
        """
        if not openai.api_key:
            raise TranscriptionError("OpenAI API key not set")

        try:
            # Make sure we're using a valid OpenAI model
            api_model = self._get_model_for_backend("api", self.model)
            print(f"DEBUG: Using API model: {api_model}")
            
            client = openai.OpenAI(api_key=openai.api_key)
            with open(audio_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model=api_model,
                    file=audio_file,
                    language=self.language,
                    response_format="text",
                )

            return response, api_model
        except Exception as e:
            raise TranscriptionError(f"API transcription failed: {str(e)}")

    def _transcribe_local_faster_whisper(self, audio_path: str) -> Tuple[str, str]:
        """
        Transcribe audio using the faster-whisper Python library
        Returns: (transcription text, model used)
        """
        try:
            # Import the library here to avoid issues if it's not installed
            # and API is being used as primary method
            from faster_whisper import WhisperModel
            
            # Check if CUDA (GPU) is available
            try:
                import torch
                has_cuda = torch.cuda.is_available()
                print(f"DEBUG: CUDA available: {has_cuda}")
                if has_cuda:
                    device = "cuda"
                    compute_type = "float16"  # Better precision for GPU
                    device_info = f"GPU: {torch.cuda.get_device_name(0)}"
                    print(f"DEBUG: Using {device_info} with compute_type={compute_type}")
                else:
                    device = "cpu"
                    compute_type = "int8"
                    device_info = "CPU (CUDA not available)"
                    print(f"DEBUG: Using {device_info} with compute_type={compute_type}")
            except ImportError as e:
                # Torch not available, use CPU
                device = "cpu"
                compute_type = "int8"
                device_info = "CPU (PyTorch not installed)"
                print(f"DEBUG: PyTorch import error: {str(e)}")
                print(f"DEBUG: Using {device_info} with compute_type={compute_type}")

            # Extract model size from the model name
            # Format: "faster-whisper:size" or just "faster-whisper" (use small.en as default)
            local_model = self._get_model_for_backend("local", self.model)
            if ":" in local_model:
                model_size = local_model.split(":", 1)[1]
            else:
                model_size = "small.en"  # Default if not specified
            
            print(f"DEBUG: Using model size: {model_size}")

            # Initialize the model
            print(f"DEBUG: Initializing WhisperModel with size={model_size}, device={device}, compute_type={compute_type}")
            model = WhisperModel(model_size, device=device, compute_type=compute_type)
            print(f"DEBUG: Model initialized successfully")
            
            # Transcribe the audio
            print(f"DEBUG: Transcribing audio file: {audio_path}")
            segments, info = model.transcribe(
                audio_path, language=self.language or "en", beam_size=5
            )
            
            # Join all segments to get the complete transcription
            print(f"DEBUG: Processing transcription segments")
            segments_list = list(segments)  # Convert generator to list
            print(f"DEBUG: Found {len(segments_list)} segments")
            
            transcription = " ".join([segment.text for segment in segments_list])
            print(f"DEBUG: Final transcription length: {len(transcription)}")
            
            return transcription, f"faster-whisper:{model_size} ({device_info})"
            
        except ImportError as e:
            error_msg = f"faster-whisper is not installed. Run './install_faster_whisper.sh'. Error: {str(e)}"
            print(f"DEBUG ERROR: {error_msg}")
            raise TranscriptionError(error_msg)
        except Exception as e:
            error_msg = f"Local transcription failed: {str(e)}"
            print(f"DEBUG ERROR: {error_msg}")
            print("DEBUG TRACEBACK:")
            traceback.print_exc()
            raise TranscriptionError(error_msg)

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
            # Override backend and model if specific model requested
            backend_to_use = self.backend
            if model:
                result["model_used"] = model
                
                # Determine backend based on model name
                if model.startswith("whisper-") or model == "whisper-1":
                    backend_to_use = "api"
                elif model.startswith("faster-whisper"):
                    backend_to_use = "local"
            
            # Try primary backend
            print(f"DEBUG: Using backend: {backend_to_use} with model: {result['model_used']}")
            if backend_to_use == "api":
                result["transcription"], result["model_used"] = self._transcribe_api(
                    audio_path
                )
                result["status"] = "done"
            else:
                result["transcription"], result["model_used"] = (
                    self._transcribe_local_faster_whisper(audio_path)
                )
                result["status"] = "done"

        except TranscriptionError as e:
            result["error_message"] = str(e)
            print(f"DEBUG: Primary transcription failed: {str(e)}")

            # Try fallback if primary fails
            try:
                print(f"DEBUG: Trying fallback method with model: {self.fallback_model}")
                fallback_backend = "api" if self.backend == "local" else "local"
                
                if fallback_backend == "api" and openai.api_key:
                    # Fall back to API
                    result["transcription"], result["model_used"] = self._transcribe_api(
                        audio_path
                    )
                    result["status"] = "done"
                elif fallback_backend == "local":
                    # Fall back to local
                    result["transcription"], result["model_used"] = (
                        self._transcribe_local_faster_whisper(audio_path)
                    )
                    result["status"] = "done"
                else:
                    print("DEBUG: Cannot use fallback (API key missing or other issue)")
            except TranscriptionError as fallback_error:
                # Both primary and fallback failed
                result["error_message"] = (
                    f"{str(e)}; Fallback also failed: {str(fallback_error)}"
                )
                print(f"DEBUG: Fallback also failed: {str(fallback_error)}")

        return result
