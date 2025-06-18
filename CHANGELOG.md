# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-18

### Added

- Voice recording with configurable hotkeys
- OpenAI Whisper API integration for transcription
- Modern web interface for managing recordings
- Clipboard integration for automatic copying
- Full-text search through transcription history
- SQLite database for local storage
- Systemd user service support
- Desktop integration with .desktop file
- Cross-platform clipboard support (X11/Wayland)
- Comprehensive configuration system
- RESTful API for programmatic access
- Audio file management and cleanup
- PulseAudio/PipeWire compatibility
- Graceful shutdown handling
- Thread safety improvements

### Fixed

- Daemon thread shutdown crashes
- Signal handler reentrancy issues
- Audio input detection on modern Linux systems
- Database connection handling
- Web server stability improvements

### Security

- Secure API key handling
- Input validation for all endpoints
- Safe file path handling

## [Unreleased]

### Planned

- Local Whisper model support
- Additional audio formats
- Hotkey management UI
- Plugin system
- Multi-language support improvements
