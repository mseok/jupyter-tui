# Jupyter TUI Demo

## Running the Application

1. **Start the TUI with a notebook:**
   ```bash
   python main.py demo_notebook.ipynb
   ```

2. **Navigation (Vim-style):**
   - `j` - Move to next cell
   - `k` - Move to previous cell
   - `gg` - Go to first cell
   - `G` - Go to last cell

3. **Cell Editing:**
   - `Enter` - Enter edit mode for current cell
   - `Esc` - Exit edit mode back to command mode
   - `a` - Insert new cell above
   - `b` - Insert new cell below
   - `dd` - Delete current cell

4. **Cell Execution:**
   - `Ctrl+Enter` - Execute current cell
   - `Shift+Enter` - Execute current cell and move to next

5. **Cell Type Conversion:**
   - `m` - Convert cell to Markdown
   - `y` - Convert cell to Code

6. **File Operations:**
   - `Ctrl+S` - Save notebook
   - `Ctrl+Q` - Quit application

## Features Demonstrated

1. **Syntax Highlighting** - Code cells show Python syntax highlighting
2. **Execution Indicators** - Cell states shown as `[ ]`, `[*]`, `[1]`, etc.
3. **Output Rendering** - Results displayed below cells
4. **Modal Editing** - Vim-like command and insert modes
5. **Real-time Updates** - Outputs stream as kernel executes

## Architecture Highlights

- **Async Kernel Communication** - Non-blocking execution
- **ZeroMQ Messaging** - Full Jupyter protocol support
- **Rich Terminal UI** - Built with Textual framework
- **nbformat Compatibility** - Read/write standard .ipynb files