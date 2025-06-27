"""Main Jupyter TUI application."""

import asyncio
import sys
from pathlib import Path
from typing import Optional
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, LoadingIndicator
from textual.binding import Binding
from rich.text import Text

from .notebook.models import Notebook, Cell, CellType
from .kernel.manager import KernelManager
from .ui.notebook_view import NotebookView


class JupyterTUI(App):
    """Main Jupyter TUI application."""
    
    CSS = """
    #notebook-container {
        height: 100%;
        overflow-y: auto;
    }
    
    .cell-container {
        margin: 1 2;
        padding: 1 1;
        height: auto;
    }
    
    .cell-container.selected {
        border: solid blue;
    }
    
    .cell-container.editing {
        border: solid green;
    }
    
    .cell-source {
        margin: 0 1;
    }
    
    .cell-editor {
        height: auto;
        min-height: 3;
        max-height: 20;
    }
    
    CellIndicator {
        width: 7;
        content-align: right middle;
        color: $text-muted;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+o", "open", "Open", priority=True),
        Binding("ctrl+n", "new", "New", priority=True),
    ]
    
    def __init__(self, notebook_path: Optional[str] = None):
        super().__init__()
        self.notebook_path = notebook_path
        self.notebook: Optional[Notebook] = None
        self.kernel_manager = KernelManager()
        self.notebook_view: Optional[NotebookView] = None
        
    async def on_mount(self) -> None:
        """Initialize the application."""
        # Load or create notebook
        if self.notebook_path and Path(self.notebook_path).exists():
            self.notebook = Notebook.load(self.notebook_path)
            self.sub_title = f"Editing: {Path(self.notebook_path).name}"
        else:
            self.notebook = Notebook()
            # Add an initial cell
            self.notebook.add_cell(Cell(cell_type=CellType.CODE))
            if self.notebook_path:
                self.notebook.filepath = self.notebook_path
                self.sub_title = f"New: {Path(self.notebook_path).name}"
            else:
                self.sub_title = "Untitled"
                
        # Start kernel
        await self.kernel_manager.create_kernel()
        
        # Create and mount notebook view
        self.notebook_view = NotebookView(self.notebook, self.kernel_manager)
        await self.mount(self.notebook_view)
        
    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header(show_clock=True)
        yield Container(id="main-container")
        yield Footer()
        
    async def action_quit(self) -> None:
        """Quit the application."""
        if self.notebook and self.notebook.modified:
            # In a real app, you'd want to prompt for save
            pass
        await self.kernel_manager.shutdown_all()
        self.exit()
        
    async def action_new(self) -> None:
        """Create a new notebook."""
        # This is simplified - in reality you'd want to prompt for save
        self.notebook = Notebook()
        self.notebook.add_cell(Cell(cell_type=CellType.CODE))
        self.sub_title = "Untitled"
        
        # Refresh view
        if self.notebook_view:
            await self.notebook_view.remove()
        self.notebook_view = NotebookView(self.notebook, self.kernel_manager)
        container = self.query_one("#main-container")
        await container.mount(self.notebook_view)
        
    async def action_open(self) -> None:
        """Open a notebook file."""
        # This is simplified - in reality you'd want a file picker
        self.notify("File picker not implemented yet", severity="warning")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Jupyter TUI - Terminal UI for Jupyter notebooks")
    parser.add_argument("notebook", nargs="?", help="Path to notebook file")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    app = JupyterTUI(notebook_path=args.notebook)
    app.run()


if __name__ == "__main__":
    main()