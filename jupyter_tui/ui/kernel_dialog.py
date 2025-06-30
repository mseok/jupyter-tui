"""Kernel selection dialog for Jupyter TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button, ListItem, ListView
from textual.screen import ModalScreen
from rich.text import Text
from rich.table import Table
from typing import Dict, Any, Optional


class KernelSelectionDialog(ModalScreen[Optional[str]]):
    """Modal dialog for selecting a kernel."""
    
    CSS = """
    KernelSelectionDialog {
        align: center middle;
    }
    
    #kernel-container {
        width: 60%;
        height: 70%;
        background: $surface;
        border: thick $primary;
    }
    
    #kernel-header {
        height: 3;
        background: $primary;
        color: $text;
        padding: 1;
    }
    
    #kernel-list {
        height: 1fr;
        overflow-y: auto;
        padding: 1;
    }
    
    #kernel-footer {
        height: 3;
        background: $surface-lighten-1;
        padding: 1;
    }
    
    .kernel-item {
        padding: 1;
        margin: 0 0 1 0;
        border: solid $primary;
    }
    
    .kernel-item:hover {
        background: $primary;
        color: $text-on-primary;
    }
    
    .kernel-item.selected {
        background: $accent;
        color: $text-on-accent;
    }
    """
    
    def __init__(self, available_kernels: Dict[str, Any], current_kernel: Optional[str] = None):
        super().__init__()
        self.available_kernels = available_kernels
        self.current_kernel = current_kernel
        self.selected_kernel = current_kernel
        
    def compose(self) -> ComposeResult:
        """Compose the kernel selection dialog."""
        with Container(id="kernel-container"):
            with Container(id="kernel-header"):
                yield Static(
                    Text("Select Kernel", style="bold white"),
                    classes="kernel-title"
                )
                
            with Vertical(id="kernel-list"):
                if not self.available_kernels:
                    yield Static(
                        Text("No kernels available", style="dim italic"),
                        classes="no-kernels"
                    )
                else:
                    kernel_list = ListView(id="kernels")
                    for kernel_name, kernel_info in self.available_kernels.items():
                        spec = kernel_info.get('spec', {})
                        display_name = spec.get('display_name', kernel_name)
                        language = spec.get('language', 'unknown')
                        
                        # Create kernel info display
                        kernel_text = Text()
                        kernel_text.append(f"{display_name}", style="bold cyan")
                        kernel_text.append(f" ({language})", style="dim")
                        if kernel_name == self.current_kernel:
                            kernel_text.append(" [CURRENT]", style="green")
                            
                        kernel_list.append(ListItem(
                            Static(kernel_text),
                            id=f"kernel-{kernel_name}"
                        ))
                        
                    yield kernel_list
                    
            with Horizontal(id="kernel-footer"):
                yield Button("Select", variant="primary", id="select-kernel")
                yield Button("Cancel", variant="default", id="cancel-kernel")
                
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle kernel selection."""
        if event.item and event.item.id:
            kernel_name = event.item.id.replace("kernel-", "")
            self.selected_kernel = kernel_name
            
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "select-kernel":
            self.dismiss(self.selected_kernel)
        elif event.button.id == "cancel-kernel":
            self.dismiss(None)
            
    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape":
            self.dismiss(None)
            event.stop()
        elif event.key == "enter":
            self.dismiss(self.selected_kernel)
            event.stop()