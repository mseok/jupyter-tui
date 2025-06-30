"""Status bar component for Jupyter TUI."""

from typing import Optional
from rich.text import Text
from textual.widgets import Static
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.containers import Horizontal

from ..notebook.models import Notebook


class StatusBar(Static):
    """Status bar showing current mode, cell position, and other info."""
    
    mode = reactive("command")
    current_cell = reactive(0)
    total_cells = reactive(0)
    kernel_status = reactive("idle")
    modified = reactive(False)
    filename = reactive("Untitled")
    cursor_line = reactive(0)
    cursor_column = reactive(0)
    
    def __init__(self, notebook: Optional[Notebook] = None):
        super().__init__()
        self.notebook = notebook
        if notebook:
            self.total_cells = len(notebook.cells)
            self.modified = notebook.modified
            self.filename = notebook.filepath or "Untitled"
    
    def render(self):
        """Render the status bar."""
        # Mode indicator
        mode_color = "green" if self.mode == "command" else "yellow"
        mode_text = "COMMAND" if self.mode == "command" else "INSERT"
        
        # Cell position with cursor info
        cell_info = f"Cell {self.current_cell + 1}/{self.total_cells}"
        if self.mode == "insert" and (self.cursor_line > 0 or self.cursor_column > 0):
            cell_info += f" | {self.cursor_line}:{self.cursor_column}"
        
        # Kernel status
        kernel_color = {
            "idle": "green",
            "busy": "yellow", 
            "dead": "red"
        }.get(self.kernel_status, "white")
        
        # File status
        file_indicator = "*" if self.modified else ""
        
        # Build status text
        status_parts = [
            Text(f" {mode_text} ", style=f"bold white on {mode_color}"),
            Text(f" {cell_info} ", style="white"),
            Text(f" Kernel: {self.kernel_status} ", style=f"{kernel_color}"),
            Text(f" {self.filename}{file_indicator} ", style="white"),
        ]
        
        return Text.assemble(*status_parts)
        
    def update_cell_position(self, current: int, total: int):
        """Update current cell position."""
        self.current_cell = current
        self.total_cells = total
        
    def update_mode(self, mode: str):
        """Update current mode."""
        self.mode = mode
        
    def update_kernel_status(self, status: str):
        """Update kernel status."""
        self.kernel_status = status
        
    def update_file_info(self, filename: str, modified: bool):
        """Update file information."""
        self.filename = filename
        self.modified = modified
        
    def update_cursor_position(self, line: int, column: int):
        """Update cursor position."""
        self.cursor_line = line
        self.cursor_column = column