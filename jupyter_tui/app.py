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
from .ui.status_bar import StatusBar


class JupyterTUI(App):
    """Main Jupyter TUI application."""
    
    CSS = """
    /* App-level transparent background */
    JupyterTUI {
        background: transparent;
    }
    
    #notebook-container {
        height: 100%;
        overflow-y: auto;
        background: transparent;
    }
    
    #cells-container {
        background: transparent;
    }
    
    .cell-container {
        margin: 1 2;
        padding: 1 1;
        height: auto;
        background: transparent;
        border: none;
    }
    
    /* Current cell selection - more prominent */
    .cell-container.selected {
        border: thick cyan;
        background: rgba(0, 255, 255, 0.1);
        outline: solid cyan;
    }
    
    /* Edit mode indication */
    .cell-container.editing {
        border: thick yellow;
        background: rgba(255, 255, 0, 0.1);
        outline: solid yellow;
    }
    
    /* Special styling for current cell indicator */
    .cell-container.selected > CellIndicator {
        background: rgba(0, 255, 255, 0.2);
    }
    
    .cell-container.editing > CellIndicator {
        background: rgba(255, 255, 0, 0.2);
    }
    
    /* Cell type indicators */
    .cell-container.code-cell {
        border-left: solid cyan;
    }
    
    .cell-container.markdown-cell {
        border-left: solid yellow;
    }
    
    .cell-container.raw-cell {
        border-left: solid white;
    }
    
    .cell-source {
        margin: 0 1;
        background: transparent;
    }
    
    .cell-editor {
        height: auto;
        min-height: 3;
        max-height: 20;
        background: transparent;
    }
    
    /* Cell execution indicator */
    CellIndicator {
        width: 8;
        content-align: right middle;
        color: $text-muted;
        background: transparent;
    }
    
    /* Output section styling */
    .cell-output {
        margin: 0 1;
        padding: 1 0;
        border-top: solid white;
        background: transparent;
    }
    
    /* Status indicators */
    .execution-running {
        color: orange;
    }
    
    .execution-finished {
        color: green;
    }
    
    .execution-error {
        color: red;
    }
    
    /* Status bar */
    #status-bar {
        dock: bottom;
        height: 1;
        background: $surface-lighten-1;
        color: $text;
    }
    
    /* Output display */
    .cell-output-container {
        margin: 1 0;
        background: transparent;
    }
    
    .output-header {
        color: cyan;
        background: transparent;
    }
    
    .output-content {
        background: transparent;
        margin: 0 1;
    }
    
    .output-item {
        margin: 1 0;
        background: transparent;
    }
    
    /* Enhanced footer */
    .enhanced-footer {
        height: 1;
        dock: bottom;
        background: $accent;
        color: $text;
        content-align: center middle;
        padding: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+o", "open", "Open", priority=True),
        Binding("ctrl+n", "new", "New", priority=True),
    ]
    
    def __init__(self, notebook_path: Optional[str] = None):
        super().__init__(ansi_color=True)
        self.notebook_path = notebook_path
        self.notebook: Optional[Notebook] = None
        self.kernel_manager = KernelManager()
        self.notebook_view: Optional[NotebookView] = None
        self.status_bar: Optional[StatusBar] = None
        
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
        
        # Create status bar
        self.status_bar = StatusBar(self.notebook)
        
        # Create and mount notebook view
        self.notebook_view = NotebookView(self.notebook, self.kernel_manager)
        self.notebook_view.set_status_bar(self.status_bar)
        
        # Mount components
        container = self.query_one("#main-container")
        await container.mount(self.notebook_view)
        
        # Mount status bar above footer
        self.status_bar.add_class("status-bar")
        await self.mount(self.status_bar)
        
    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header(show_clock=True)
        yield Container(id="main-container")
        # Note: StatusBar will be mounted dynamically
        yield self._create_enhanced_footer()
        
    def _create_enhanced_footer(self):
        """Create an enhanced footer with better keymap visualization."""
        from textual.widgets import Footer
        
        class EnhancedFooter(Footer):
            """Enhanced footer with better keymap display."""
            
            def compose(self) -> ComposeResult:
                from textual.containers import Horizontal
                from textual.widgets import Static
                from rich.text import Text
                
                # Create mode-aware shortcuts
                mode = getattr(self.app.notebook_view, 'mode', 'command') if hasattr(self.app, 'notebook_view') and self.app.notebook_view else 'command'
                
                if mode == "command":
                    shortcuts = [
                        ("j/k", "Navigate"),
                        ("Enter", "Edit"),
                        ("a/b", "Insert"),
                        ("dd", "Delete"),
                        ("?", "Help"),
                        ("^Q", "Quit")
                    ]
                else:
                    shortcuts = [
                        ("Esc", "Command"),
                        ("^Enter", "Execute"),
                        ("S-Enter", "Execute&Next"),
                        ("?", "Help"),
                        ("^Q", "Quit")
                    ]
                
                # Create formatted shortcut text
                shortcut_text = Text()
                for i, (key, desc) in enumerate(shortcuts):
                    if i > 0:
                        shortcut_text.append(" │ ", style="dim")
                    shortcut_text.append(f"{key}", style="bold cyan")
                    shortcut_text.append(f" {desc}", style="white")
                
                yield Static(shortcut_text, classes="enhanced-footer")
        
        return EnhancedFooter()
        
    async def action_quit(self) -> None:
        """Quit the application."""
        if self.notebook and self.notebook.has_unsaved_changes():
            # Discard temporary changes on quit without save
            self.notebook.discard_changes()
            self.notify("Discarded unsaved changes", severity="information")
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