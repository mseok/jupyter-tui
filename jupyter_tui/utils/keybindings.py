"""Vim-like keybindings for Jupyter TUI."""

from typing import Dict, List, Tuple, Callable
from textual.binding import Binding


class VimKeybindings:
    """Vim-style keybindings for notebook navigation."""
    
    # Normal mode bindings
    NORMAL_MODE_BINDINGS = [
        # Navigation
        ("j", "next_cell", "Next cell"),
        ("k", "previous_cell", "Previous cell"),
        ("g,g", "go_top", "Go to first cell"),
        ("shift+g", "go_bottom", "Go to last cell"),
        ("ctrl+d", "page_down", "Page down"),
        ("ctrl+u", "page_up", "Page up"),
        
        # Cell manipulation
        ("a", "insert_above", "Insert cell above"),
        ("b", "insert_below", "Insert cell below"),
        ("d,d", "delete_cell", "Delete cell"),
        ("y,y", "copy_cell", "Copy cell"),
        ("p", "paste_below", "Paste cell below"),
        ("shift+p", "paste_above", "Paste cell above"),
        
        # Cell type changes
        ("m", "to_markdown", "Change to markdown"),
        ("y", "to_code", "Change to code"),
        ("r", "to_raw", "Change to raw"),
        
        # Execution
        ("ctrl+enter", "execute", "Execute cell"),
        ("shift+enter", "execute_next", "Execute and select next"),
        ("alt+enter", "execute_insert", "Execute and insert below"),
        
        # Editing
        ("i", "edit_cell", "Edit cell"),
        ("enter", "edit_cell", "Edit cell"),
        ("o", "insert_below_edit", "Insert below and edit"),
        ("shift+o", "insert_above_edit", "Insert above and edit"),
        
        # Cell movement
        ("ctrl+k", "move_cell_up", "Move cell up"),
        ("ctrl+j", "move_cell_down", "Move cell down"),
        
        # Other
        ("l", "toggle_line_numbers", "Toggle line numbers"),
        ("shift+l", "toggle_all_line_numbers", "Toggle all line numbers"),
        ("z,z", "center_cell", "Center current cell"),
        ("ctrl+s", "save", "Save notebook"),
        ("/", "search", "Search"),
        ("n", "search_next", "Next match"),
        ("shift+n", "search_previous", "Previous match"),
    ]
    
    # Insert mode bindings (when editing a cell)
    INSERT_MODE_BINDINGS = [
        ("escape", "exit_edit_mode", "Exit edit mode"),
        ("ctrl+enter", "execute", "Execute cell"),
        ("shift+enter", "execute_next", "Execute and next"),
        ("alt+enter", "execute_insert", "Execute and insert"),
        ("tab", "indent", "Indent"),
        ("shift+tab", "dedent", "Dedent"),
        ("ctrl+space", "autocomplete", "Autocomplete"),
    ]
    
    @classmethod
    def get_normal_bindings(cls) -> List[Binding]:
        """Get bindings for normal mode."""
        return [Binding(key, action, desc) for key, action, desc in cls.NORMAL_MODE_BINDINGS]
        
    @classmethod
    def get_insert_bindings(cls) -> List[Binding]:
        """Get bindings for insert mode."""
        return [Binding(key, action, desc) for key, action, desc in cls.INSERT_MODE_BINDINGS]


class CommandParser:
    """Parse vim-style commands (e.g., :w, :q, :wq)."""
    
    COMMANDS = {
        "w": "save",
        "write": "save",
        "q": "quit",
        "quit": "quit",
        "wq": "save_quit",
        "x": "save_quit",
        "e": "open",
        "edit": "open",
        "new": "new",
        "kernel": "kernel_info",
        "restart": "restart_kernel",
    }
    
    @classmethod
    def parse(cls, command: str) -> Tuple[str, List[str]]:
        """Parse a command string into action and arguments."""
        if not command.startswith(":"):
            return "", []
            
        parts = command[1:].split()
        if not parts:
            return "", []
            
        cmd = parts[0]
        args = parts[1:]
        
        action = cls.COMMANDS.get(cmd, "")
        return action, args