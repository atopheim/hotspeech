"""
FastAPI routes for Hotspeech web UI
"""

import os
import time
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import toml

from ..db import Database
from ..audio import AudioRecorder
from ..transcriber import Transcriber
from ..clipboard import Clipboard


# Models for API requests/responses
class TranscriptionRequest(BaseModel):
    recording_id: int
    model: Optional[str] = None


class DeleteRequest(BaseModel):
    recording_id: int


class DefaultModelRequest(BaseModel):
    model: str


# Global app state
app = FastAPI(title="Hotspeech API")
config = None
db = None
recorder = None
transcriber = None
config_path = None


def initialize(app_config):
    """Initialize the FastAPI app with configuration"""
    global config, db, recorder, transcriber, config_path
    config = app_config
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.toml")
    db = Database(os.path.expanduser(config["storage"]["sqlite_path"]))
    recorder = AudioRecorder(config)
    transcriber = Transcriber(config)

    # Setup templates and static files
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    static_dir = os.path.join(os.path.dirname(__file__), "static")

    # Ensure directories exist
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)

    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    templates = Jinja2Templates(directory=templates_dir)

    # Set templates in app state
    app.state.templates = templates


# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page"""
    recordings = db.get_recent_recordings(limit=int(config["storage"]["keep_last_n"]))
    
    # Get the current model name for display
    current_model = config["transcription"]["model"]
    
    # Check if GPU is available for faster-whisper
    gpu_available = False
    try:
        import torch
        gpu_available = torch.cuda.is_available()
    except ImportError:
        pass
    
    return app.state.templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "recordings": recordings,
            "title": "Hotspeech - Voice Transcription",
            "current_model": current_model,
            "gpu_available": gpu_available
        },
    )


@app.get("/api/recordings", response_model=List[Dict[str, Any]])
async def get_recordings():
    """API endpoint to get recent recordings"""
    recordings = db.get_recent_recordings(limit=int(config["storage"]["keep_last_n"]))
    return recordings


@app.get("/api/recording/{recording_id}")
async def get_recording(recording_id: int):
    """API endpoint to get a specific recording"""
    recording = db.get_recording(recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    return recording


@app.post("/api/transcribe")
async def transcribe_recording(request: TranscriptionRequest):
    """API endpoint to re-transcribe a recording with a different model"""
    recording = db.get_recording(request.recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Transcribe the audio
    result = transcriber.transcribe(recording["audio_path"], model=request.model)

    # Update the recording in the database
    db.update_recording(
        request.recording_id,
        transcription=result["transcription"],
        model_used=result["model_used"],
        status=result["status"],
        error_message=result["error_message"],
    )

    # Return the updated recording
    return db.get_recording(request.recording_id)


@app.post("/api/set-default-model")
async def set_default_model(request: DefaultModelRequest):
    """API endpoint to change the default transcription model"""
    global config
    
    # Validate model option
    valid_models = ["whisper-1", "faster-whisper"]
    if request.model not in valid_models:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid model. Choose from: {', '.join(valid_models)}"
        )
    
    try:
        # Update in-memory config
        config["transcription"]["model"] = request.model
        
        # Set backend accordingly
        if request.model == "whisper-1":
            config["transcription"]["backend"] = "api"
        elif request.model == "faster-whisper":
            config["transcription"]["backend"] = "local"
        
        # Reinitialize the transcriber with new config
        transcriber.model = request.model
        transcriber.backend = config["transcription"]["backend"]
        
        # Update the config file
        if config_path:
            # Read existing config
            with open(config_path, "r") as f:
                config_data = toml.load(f)
            
            # Update values
            config_data["transcription"]["model"] = request.model
            config_data["transcription"]["backend"] = config["transcription"]["backend"]
            
            # Write back
            with open(config_path, "w") as f:
                toml.dump(config_data, f)
        
        return {"success": True, "model": request.model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update model: {str(e)}")


@app.post("/api/copy/{recording_id}")
async def copy_to_clipboard(recording_id: int):
    """API endpoint to copy a transcription to clipboard"""
    recording = db.get_recording(recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    if not recording["transcription"]:
        raise HTTPException(status_code=400, detail="No transcription available")

    success = Clipboard.copy_to_clipboard(recording["transcription"])
    return {"success": success}


@app.delete("/api/recording/{recording_id}")
async def delete_recording(recording_id: int):
    """API endpoint to delete a recording"""
    recording = db.get_recording(recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Delete the audio file if it exists
    audio_path = recording["audio_path"]
    if os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except OSError:
            pass

    # Delete from database
    success = db.delete_recording(recording_id)
    return {"success": success}


@app.get("/api/audio/{recording_id}")
async def get_audio(recording_id: int):
    """API endpoint to get the audio file for a recording"""
    recording = db.get_recording(recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    audio_path = recording["audio_path"]
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(audio_path, media_type="audio/wav")


@app.post("/api/search")
async def search_recordings(query: str = Form(...)):
    """API endpoint to search recordings"""
    if not query or len(query.strip()) < 3:
        raise HTTPException(
            status_code=400, detail="Search query must be at least 3 characters"
        )

    results = db.search_transcriptions(
        query, limit=int(config["storage"]["keep_last_n"])
    )
    return results


def run_server():
    """Run the FastAPI server"""
    host = config["webui"]["host"]
    port = config["webui"]["port"]
    uvicorn.run(app, host=host, port=port)


# Helper function to get app instance after initialization
def get_app():
    return app
