# GuakeGPT

A GTK-based dropdown chat application that mimics Guake's dropdown terminal behavior.

## Features

- Dropdown window that slides from the top of the screen
- Global hotkey support (default: F12)
- Modern GTK-based chat interface
- Smooth animations
- Focus-loss auto-hide

## Installation

1. Install system dependencies:

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
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

Note: The keybinder library is provided through the system package manager, not through PyPI. Make sure to install the system packages first.

## Usage

Run the application:

```bash
python main.py
```

- Press F12 to show/hide the chat window
- Type your message and press Enter or click Send
- Window automatically hides when focus is lost

## Development

The application is structured as follows:
- `main.py`: Core application and window management
- `requirements.txt`: Python dependencies 