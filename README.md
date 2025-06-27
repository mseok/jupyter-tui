# Jupyter TUI

A terminal user interface for Jupyter notebooks, inspired by vim and modern TUI applications.

## Features

- **Vim-style keybindings** for efficient notebook navigation
- **Async kernel communication** using ZeroMQ protocol
- **Rich output rendering** with support for multiple MIME types
- **Real-time execution** with streaming outputs
- **nbformat compatibility** - read and write standard .ipynb files

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with uv
uv pip install -e .
```

## Usage

```bash
# Open an existing notebook
python main.py notebook.ipynb

# Create a new notebook
python main.py

# Open with a specific filename
python main.py new_notebook.ipynb
```

## Keybindings

### Normal Mode (Command Mode)

| Key | Action |
|-----|--------|
| `j`/`k` | Navigate cells down/up |
| `Enter` | Edit current cell |
| `Esc` | Exit edit mode |
| `a`/`b` | Insert cell above/below |
| `dd` | Delete current cell |
| `m`/`y` | Convert cell to markdown/code |
| `Ctrl+Enter` | Execute cell |
| `Shift+Enter` | Execute cell and move to next |
| `Ctrl+S` | Save notebook |
| `gg`/`G` | Go to first/last cell |

### Edit Mode

| Key | Action |
|-----|--------|
| `Esc` | Return to normal mode |
| `Ctrl+Enter` | Execute cell |
| `Shift+Enter` | Execute and move to next |
| `Tab` | Trigger autocomplete (when implemented) |

## Architecture

The application follows a layered architecture:

1. **Kernel Layer**: Manages Jupyter kernel processes and ZeroMQ communication
2. **Document Layer**: Handles notebook structure and cell management
3. **UI Layer**: Textual-based interface with vim-like interactions
4. **Renderer Layer**: Converts various output types to terminal display

## Development

```bash
# Install in development mode
uv pip install -e .

# Run the application
python main.py
```

## License

MIT