# Hotspeech

Hotspeech is a voice recording and transcription tool for Linux that allows you to quickly record audio, transcribe it using the OpenAI Whisper API, and copy the result to your clipboard. It includes a database to store your recordings and transcriptions, and a web interface to manage them.

## Features

- **Hotkey Triggered Recording**: Set global hotkeys to start recording from any application
- **Transcription**: Uses OpenAI's Whisper API for accurate speech-to-text conversion
- **Model Switching**: Easily switch between different transcription models
- **Clipboard Integration**: Automatically copies transcriptions to clipboard for easy pasting
- **Local Storage**: Saves recordings and transcriptions in a SQLite database
- **Web Interface**: View, manage, and re-transcribe your recordings from a web browser
- **Command Line Interface**: Control Hotspeech from the terminal

## Requirements

- Linux system with Python 3.7+
- ffmpeg (for audio recording and playback)
- sxhkd (for hotkey support)
- wl-clipboard (for Wayland) or xclip (for X11) for clipboard support
- zenity (optional, for the recording UI dialog)

## Installation

### Prerequisites

- Python 3.9+
- FFmpeg
- SWHKD (for hotkey support on Wayland)
  - Install from: https://github.com/waycrate/swhkd
- OpenAI API key (for transcription)

### Automatic Installation (Recommended)

Use the provided installation script, which will set up everything automatically using Astral's uv:

```
git clone [repository-url]
cd hotspeech
./hotspeech/install.sh
```

The script will:

1. Install system dependencies (ffmpeg, sxhkd, wl-clipboard)
2. Install Astral's uv if not already present
3. Create a virtual environment
4. Install Python dependencies
5. Set up configuration directories
6. Prompt for your OpenAI API key

### Manual Installation

1. Clone this repository:

```
git clone [repository-url]
cd hotspeech
```

2. Install Astral's uv (if you don't have it yet):

```
curl -fsSL https://astral.sh/uv/install.sh | bash
```

3. Set up a virtual environment and install dependencies:

```
# Create and activate a virtual environment with uv
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

Alternatively, you can use pip:

```
# Create and activate a virtual environment with venv
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

4. Install system dependencies:

```
# On Arch Linux
sudo pacman -S ffmpeg sxhkd wl-clipboard zenity

# On Ubuntu/Debian
sudo apt install ffmpeg sxhkd wl-clipboard xclip zenity
```

5. Configure your OpenAI API key in `config.toml` or set it as an environment variable:

```
export OPENAI_API_KEY=your_api_key_here
```

## Usage

### Starting the daemon (web server + hotkeys)

Make sure your virtual environment is activated, then run one of these commands:

```
# Option 1: Run directly with Python
python main.py daemon

# Option 2: Run as a module
python -m main daemon

# Option 3: Run with uv
uv python main.py daemon
```

This will start a web server and configure the hotkeys.

### Recording with hotkeys

- Press `Ctrl+Alt+S` to start recording
  - A notification window will appear to confirm recording is in progress
  - You can click the "Stop Recording" button in this window to stop
- Press `Ctrl+Alt+W` to stop recording
- Press `Ctrl+Shift+N` for a quick note (quiet mode recording)
- The transcription will be automatically copied to your clipboard

> Note: You can customize hotkeys in the `config.toml` file.

### Using the Web Interface

Open your browser and navigate to http://localhost:8080 to access the web interface.

### Using the CLI

List your recordings:

```
python cli.py list
```

Play a recording:

```
python cli.py play 1
```

Re-transcribe with a different model:

```
python cli.py transcribe 1 --model whisper-1
```

Copy to clipboard:

```
python cli.py copy 1
```

Delete a recording:

```
python cli.py delete 1
```

Start recording (from command line):

```
python main.py record
```

Stop recording (from command line):

```
python main.py stop
```

## Configuration

The configuration file is located at `config.toml`. You can customize:

- Hotkeys
- Recording settings
- Transcription models
- Database location
- Web server settings

## License

MIT License
