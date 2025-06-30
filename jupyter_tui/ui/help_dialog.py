"""Help dialog for displaying keymaps and usage information."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Button
from textual.screen import ModalScreen
from rich.text import Text
from rich.table import Table
from rich.panel import Panel


class HelpDialog(ModalScreen):
    """Modal help dialog showing keybindings and usage."""
    
    CSS = """
    HelpDialog {
        align: center middle;
    }
    
    #help-container {
        width: 80%;
        height: 80%;
        background: $surface;
        border: thick $primary;
    }
    
    #help-content {
        height: 1fr;
        overflow-y: auto;
        padding: 1;
    }
    
    #help-header {
        height: 3;
        background: $primary;
        color: $text;
        padding: 1;
    }
    
    #help-footer {
        height: 3;
        background: $surface-lighten-1;
        padding: 1;
    }
    """
    
    def __init__(self, mode: str = "command"):
        super().__init__()
        self.mode = mode
        
    def compose(self) -> ComposeResult:
        """Compose the help dialog."""
        with Container(id="help-container"):
            with Container(id="help-header"):
                yield Static(
                    Text(f"Jupyter TUI Help - {self.mode.upper()} Mode", 
                         style="bold white"),
                    classes="help-title"
                )
                
            with ScrollableContainer(id="help-content"):
                yield self._create_help_content()
                
            with Horizontal(id="help-footer"):
                yield Button("Close (Esc)", variant="primary", id="close-help")
                
    def _create_help_content(self) -> Static:
        """Create the help content based on current mode."""
        if self.mode == "command":
            return Static(self._command_mode_help())
        else:
            return Static(self._edit_mode_help())
            
    def _command_mode_help(self) -> Panel:
        """Create command mode help content."""
        
        # Navigation table
        nav_table = Table(title="Navigation", show_header=True, header_style="bold blue")
        nav_table.add_column("Key", style="cyan", width=12)
        nav_table.add_column("Action", style="white")
        
        nav_bindings = [
            ("j", "Move to next cell"),
            ("k", "Move to previous cell"),
            ("gg", "Go to first cell"),
            ("G", "Go to last cell"),
            ("Ctrl+d", "Page down"),
            ("Ctrl+u", "Page up"),
        ]
        
        for key, action in nav_bindings:
            nav_table.add_row(key, action)
            
        # Cell management table
        cell_table = Table(title="Cell Management", show_header=True, header_style="bold green")
        cell_table.add_column("Key", style="cyan", width=12)
        cell_table.add_column("Action", style="white")
        
        cell_bindings = [
            ("a", "Insert cell above"),
            ("b", "Insert cell below"),
            ("dd", "Delete current cell"),
            ("m", "Convert to markdown cell"),
            ("y", "Convert to code cell"),
            ("yy", "Copy cell"),
            ("p", "Paste cell below"),
            ("P", "Paste cell above"),
        ]
        
        for key, action in cell_bindings:
            cell_table.add_row(key, action)
            
        # Execution table
        exec_table = Table(title="Execution", show_header=True, header_style="bold yellow")
        exec_table.add_column("Key", style="cyan", width=12)
        exec_table.add_column("Action", style="white")
        
        exec_bindings = [
            ("Ctrl+Enter", "Execute current cell"),
            ("Shift+Enter", "Execute and move to next"),
            ("Alt+Enter", "Execute and insert below"),
            ("Ctrl+C", "Interrupt kernel"),
            ("00", "Restart kernel"),
        ]
        
        for key, action in exec_bindings:
            exec_table.add_row(key, action)
            
        # Editing table
        edit_table = Table(title="Editing", show_header=True, header_style="bold magenta")
        edit_table.add_column("Key", style="cyan", width=12)
        edit_table.add_column("Action", style="white")
        
        edit_bindings = [
            ("Enter", "Enter edit mode"),
            ("i", "Enter edit mode"),
            ("o", "Insert cell below and edit"),
            ("O", "Insert cell above and edit"),
        ]
        
        for key, action in edit_bindings:
            edit_table.add_row(key, action)
            
        # File operations table
        file_table = Table(title="File Operations", show_header=True, header_style="bold red")
        file_table.add_column("Key", style="cyan", width=12)
        file_table.add_column("Action", style="white")
        
        file_bindings = [
            ("Ctrl+S", "Save notebook"),
            ("Ctrl+O", "Open notebook"),
            ("Ctrl+N", "New notebook"),
            ("Ctrl+Q", "Quit application"),
        ]
        
        for key, action in file_bindings:
            file_table.add_row(key, action)
            
        # Combine all tables
        content = Vertical(
            nav_table,
            Static(""),
            cell_table,
            Static(""),
            exec_table,
            Static(""),
            edit_table,
            Static(""),
            file_table,
            Static(""),
            Static(Text("Press '?' to toggle this help dialog", style="italic dim")),
        )
        
        return Panel(content, title="Command Mode Keybindings", border_style="blue")
        
    def _edit_mode_help(self) -> Panel:
        """Create edit mode help content."""
        
        edit_table = Table(title="Edit Mode", show_header=True, header_style="bold green")
        edit_table.add_column("Key", style="cyan", width=15)
        edit_table.add_column("Action", style="white")
        
        edit_bindings = [
            ("Esc", "Exit to command mode"),
            ("Ctrl+Enter", "Execute cell"),
            ("Shift+Enter", "Execute and move to next"),
            ("Alt+Enter", "Execute and insert below"),
            ("Tab", "Indent or autocomplete"),
            ("Shift+Tab", "Dedent"),
            ("Ctrl+Space", "Force autocomplete"),
            ("Ctrl+/", "Toggle comment"),
            ("Ctrl+A", "Select all"),
            ("Ctrl+Z", "Undo"),
            ("Ctrl+Y", "Redo"),
        ]
        
        for key, action in edit_bindings:
            edit_table.add_row(key, action)
            
        content = Vertical(
            edit_table,
            Static(""),
            Static(Text("Use standard text editing keys for navigation and editing", style="italic")),
            Static(Text("Press Esc to return to command mode", style="bold yellow")),
        )
        
        return Panel(content, title="Edit Mode Keybindings", border_style="green")
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "close-help":
            self.dismiss()
            
    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape" or event.key == "q":
            self.dismiss()
            event.stop()