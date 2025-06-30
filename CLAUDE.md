# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `jupyter-tui`, a Python project intended to provide a Terminal User Interface for Jupyter. Currently in early development stage with minimal implementation.

## Development Commands

This project uses `uv` as the Python package manager. Virtual environment activation:

- **Activate virtual environment**: `source $PROJECT_ROOT/.venv/bin/activate`
- **Run the application**: `python main.py`
- **Install dependencies**: `uv pip install -e .`
- **Add new dependencies**: `uv add <package-name>`

No testing, linting, or formatting tools are currently configured.

## Architecture

### Project Structure
```
jupyter_tui/
├── app.py              # Main Textual application
├── kernel/
│   ├── manager.py      # Kernel lifecycle and ZeroMQ communication
├── notebook/
│   ├── models.py       # Notebook, Cell, and Output data models
├── ui/
│   ├── cell_widget.py  # Cell display and editing widgets
│   ├── notebook_view.py # Main notebook interface
├── renderers/
│   ├── base.py         # Renderer interface and registry
│   ├── text.py         # MIME type renderers (plain, HTML, markdown, etc.)
└── utils/
    ├── keybindings.py  # Vim-style keybinding definitions
```

### Key Components

1. **Kernel Management** (`kernel/manager.py`)
   - Async ZeroMQ-based communication with Jupyter kernels
   - Message routing for execute, complete, inspect operations
   - Multi-kernel support with session management

2. **Notebook Model** (`notebook/models.py`)
   - Cell types: Code, Markdown, Raw
   - Execution states: Idle, Pending, Running, Finished, Error
   - nbformat v4 compatibility for .ipynb files

3. **UI Layer** (Textual-based)
   - Vim-like modal editing (command/insert modes)
   - Cell-based navigation with j/k movements
   - Real-time output rendering with Rich formatting

4. **Output Rendering** (`renderers/`)
   - MIME type handlers for text/plain, text/html, application/json
   - DataFrame detection and table rendering
   - Error traceback formatting

### Development Notes

- The app uses asyncio for concurrent kernel communication and UI updates
- Cell execution follows Jupyter's message protocol with proper parent tracking
- Outputs are streamed and rendered incrementally
- The UI is fully keyboard-driven with vim-style bindings
- Each time successfully created features, add all changed files and commit it with suitable message
- Since the program is streaming service, if you do not get any errors in 1 minute, automatically shutdown the app only when you do some debugging
