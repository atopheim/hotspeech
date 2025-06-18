# Hotspeech - AUR Package

Simple voice recording and transcription tool using OpenAI Whisper API.

## Quick Setup (2 minutes)

After installing from AUR:

### 1. Install the package

```bash
yay -S hotspeech
# or
paru -S hotspeech
```

### 2. Run the setup script

```bash
hotspeech-setup
```

This will:

- Create your configuration directory
- Prompt for your OpenAI API key
- Show you exactly how to set up hotkeys

### 3. Set up hotkeys

**GNOME/Ubuntu:**

- Settings → Keyboard → View and Customize Shortcuts → Custom Shortcuts
- Add: Name='Start Recording', Command='hotspeech record', Shortcut=Ctrl+Shift+R
- Add: Name='Stop Recording', Command='hotspeech stop', Shortcut=Ctrl+Shift+Q

**KDE Plasma:**

- System Settings → Shortcuts → Custom Shortcuts → New → Global Shortcut
- Use the same commands as above

**i3/sway:**

```
bindsym $mod+Shift+r exec hotspeech record
bindsym $mod+Shift+q exec hotspeech stop
```

### 4. Start using

```bash
hotspeech daemon
```

## Usage

- **Start daemon:** `hotspeech daemon`
- **Record audio:** `hotspeech record`
- **Stop recording:** `hotspeech stop`
- **List recordings:** `hotspeech-cli list`
- **Web interface:** http://localhost:8080

## Configuration

- **Config file:** `~/.config/hotspeech/config.toml`
- **Audio storage:** `~/.local/share/hotspeech/audio/`
- **Database:** `~/.local/share/hotspeech/hotspeech.db`

## Requirements

- OpenAI API key (get from https://platform.openai.com/api-keys)
- Microphone access
- Internet connection for transcription

## Optional Dependencies

- `wl-clipboard` - for Wayland clipboard support
- `xclip` - for X11 clipboard support
- `zenity` - for GUI notifications

## Troubleshooting

**No config file found:**

```bash
hotspeech-setup
```

**Audio not recording:**

- Check microphone permissions
- Ensure ffmpeg is working: `ffmpeg -version`

**Transcription failing:**

- Verify API key: `grep api_key ~/.config/hotspeech/config.toml`
- Check internet connection

**Hotkeys not working:**

- Make sure you used the exact commands: `hotspeech record` and `hotspeech stop`
- Test commands manually in terminal first

## Files Installed

- `/usr/bin/hotspeech` - Main program
- `/usr/bin/hotspeech-cli` - CLI interface
- `/usr/bin/hotspeech-setup` - Setup script
- `/etc/hotspeech/config.toml` - System config template
- `/usr/share/doc/hotspeech/` - Documentation
- `/usr/share/applications/hotspeech.desktop` - Desktop file

## License

MIT License
