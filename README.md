# GuakeGPT

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

A GTK-based dropdown chat application that mimics Guake's dropdown terminal behavior.

## Features

- Dropdown window that slides from the top of the screen
- Global hotkey support (default: F12)
- Modern GTK-based chat interface
- Smooth animations
- Focus-loss auto-hide
- Support for multiple LLM providers (OpenAI, Anthropic)
- Secure API key storage using system keyring

## Requirements

- Python 3.8 or higher
- GTK 3.x
- For MacOS: Homebrew package manager (https://brew.sh)

## Installation

1. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Linux/MacOS
# or
.\venv\Scripts\activate  # On Windows
```

2. Install system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-keybinder-3.0 \
    libcairo2-dev pkg-config python3-dev libgirepository1.0-dev

# Fedora
sudo dnf install python3-gobject python3-gobject-base gtk3 keybinder3 python3-keybinder \
    cairo-devel pkg-config python3-devel gobject-introspection-devel

# Arch Linux
sudo pacman -S python-gobject gtk3 keybinder3 python-keybinder \
    cairo pkgconf python-cairo gobject-introspection

# MacOS
brew install gtk+3 pygobject3 gtk-mac-integration
brew install python-keybinder
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

Note: The keybinder library is provided through the system package manager (apt/dnf/pacman/brew), not through PyPI. Make sure to install the system packages first.

## Usage

Run the application:

```bash
python -m guakegpt.cli
```

- Press F12 to show/hide the chat window
- Type your message and press Enter or click Send
- Window automatically hides when focus is lost
- Configure LLM settings and API keys in the settings dialog (gear icon)

## Configuration

The configuration file is stored at `~/.config/guakegpt/config.json` and contains the following settings:

```json
{
    "window": {
        "width": 800,
        "height": 600,
        "animation_duration": 200,
        "hotkey": "F12"
    },
    "llm": {
        "provider": "anthropic",
        "model": "claude-3-opus-20240229"
    }
}
```

### Customizing Hotkeys
The default hotkey (F12) can be changed in the settings dialog or by editing the config file. Valid hotkeys include function keys (F1-F12) and key combinations (e.g., "<Ctrl>space").

## Security

- API keys are stored securely in the system keyring
- No sensitive data is stored in the configuration file
- Configuration is stored in `~/.config/guakegpt/config.json`
- Each LLM provider's API key is stored separately
- No API keys or sensitive data are included in logs or error messages

## Known Issues

- MacOS: Some keyboard shortcuts may conflict with system shortcuts
- Linux: On some window managers, the window may not slide smoothly
- The window may not hide properly when using multiple monitors

## Development

The application is structured as follows:
- `guakegpt/`: Main package directory
  - `app.py`: Core application and window management
  - `cli.py`: Command-line interface
  - `ui/`: User interface components
  - `llm/`: LLM client implementations
  - `config/`: Configuration management
- `requirements.txt`: Python dependencies

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 