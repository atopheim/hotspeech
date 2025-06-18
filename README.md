# Hotspeech

Voice recording and transcription tool with hotkey support and web interface.

## Features

- 🎙️ **Voice Recording**: High-quality audio recording with configurable hotkeys
- 🤖 **AI Transcription**: Powered by OpenAI Whisper API with local fallback support
- 🌐 **Web Interface**: Modern web UI for managing recordings and transcriptions
- 📋 **Clipboard Integration**: Automatic copying of transcriptions to clipboard
- 🔍 **Full-Text Search**: Search through your transcription history
- 🎯 **Hotkey Support**: Global hotkeys for quick recording (manual setup required)
- 💾 **Local Storage**: SQLite database with audio file management
- 🔧 **Configurable**: Extensive configuration options via TOML files

## Installation

### Arch Linux (AUR)

```bash
yay -S hotspeech
# or
paru -S hotspeech
```

### Manual Installation

```bash
git clone https://github.com/atopheim/hotspeech.git
cd hotspeech
pip install -r requirements.txt
python setup.py install
```

## Configuration

### Initial Setup

1. Create configuration directory:

```bash
mkdir -p ~/.config/hotspeech
```

2. Copy example configuration:

```bash
cp /usr/share/hotspeech/config.toml.example ~/.config/hotspeech/config.toml
```

3. Edit configuration with your OpenAI API key:

```bash
nano ~/.config/hotspeech/config.toml
```

### Configuration Options

```toml
[recording]
output_format = "wav"
max_duration_seconds = 3600
audio_dir = "~/.local/share/hotspeech/audio"

[transcription]
backend = "api"                    # "api" or "local"
model = "whisper-1"               # OpenAI model
language = "en"                   # Language code
api_key = "your-openai-api-key"   # Required for API backend

[storage]
sqlite_path = "~/.local/share/hotspeech/hotspeech.db"
keep_last_n = 10                  # Number of recordings to keep

[clipboard]
enabled = true                    # Auto-copy transcriptions

[webui]
port = 8081
host = "127.0.0.1"
```

## Usage

### Start the Daemon

```bash
# Start the web interface and daemon
hotspeech daemon

# Or start as systemd user service
systemctl --user enable hotspeech.service
systemctl --user start hotspeech.service
```

### Manual Recording

```bash
# Record with transcription
hotspeech record

# Record quietly (no notifications)
hotspeech record --quiet

# Stop active recording
hotspeech stop
```

### Web Interface

Access the web interface at: http://localhost:8081

Features:

- View all recordings and transcriptions
- Play back audio files
- Copy transcriptions to clipboard
- Re-transcribe with different models
- Search through transcription history
- Delete recordings

### Hotkeys (Manual Setup Required)

Set up global hotkeys in your desktop environment to trigger:

```bash
# Start recording
hotspeech record

# Stop recording
hotspeech stop
```

**Example for i3/sway:**

```
bindsym $mod+Shift+r exec hotspeech record
bindsym $mod+Shift+q exec hotspeech stop
```

## Dependencies

- Python 3.8+
- FFmpeg (for audio processing)
- PulseAudio/PipeWire (for audio capture)
- libnotify (for desktop notifications)

### Optional Dependencies

- `xclip` (clipboard support on X11)
- `wl-clipboard` (clipboard support on Wayland)

## API Endpoints

The web interface provides a REST API:

- `GET /api/recordings` - List recent recordings
- `GET /api/recording/{id}` - Get specific recording
- `POST /api/transcribe` - Re-transcribe a recording
- `POST /api/copy/{id}` - Copy transcription to clipboard
- `DELETE /api/recording/{id}` - Delete recording
- `POST /api/search` - Search transcriptions

## Troubleshooting

### Audio Issues

1. Check audio devices:

```bash
pactl list sources short
```

2. Test recording:

```bash
ffmpeg -f pulse -i default -t 5 test.wav
```

### Permission Issues

Ensure your user is in the `audio` group:

```bash
sudo usermod -a -G audio $USER
```

### API Key Issues

1. Verify your OpenAI API key has credits
2. Check the key format in the configuration file
3. Test API access manually

## Development

### Running from Source

```bash
git clone https://github.com/atopheim/hotspeech.git
cd hotspeech
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python hotspeech/main.py daemon
```

### Building

```bash
python -m build
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- GitHub Issues: https://github.com/atopheim/hotspeech/issues
- Documentation: https://github.com/atopheim/hotspeech/wiki
