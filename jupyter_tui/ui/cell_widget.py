"""Cell widget for displaying and editing notebook cells."""

from typing import Optional, List
from rich.text import Text
from rich.syntax import Syntax
from rich.panel import Panel
from rich.console import RenderableType
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Label, TextArea
from textual.reactive import reactive
from textual import events

from ..notebook.models import Cell, CellType, CellState, CellOutput
from ..renderers import create_default_registry


class CellIndicator(Static):
    """Cell execution state indicator."""
    
    def __init__(self, cell: Cell):
        super().__init__()
        self.cell = cell
        
    def render(self) -> RenderableType:
        # Show cell type indicator for all cells
        if self.cell.cell_type == CellType.MARKDOWN:
            return Text("   M:   ", style="yellow")
        elif self.cell.cell_type == CellType.RAW:
            return Text("   R:   ", style="white")
        
        # Code cell execution indicators
        if self.cell.state == CellState.IDLE:
            count = self.cell.execution_count
            if count is None:
                return Text("[ ]:    ", style="cyan")
            else:
                return Text(f"[{count}]:   ", style="cyan")
        elif self.cell.state == CellState.PENDING:
            return Text("[...]:  ", style="orange")
        elif self.cell.state == CellState.RUNNING:
            return Text("[*]:    ", style="orange bold")
        elif self.cell.state == CellState.ERROR:
            return Text("[!]:    ", style="red bold")
        else:
            count = self.cell.execution_count or " "
            return Text(f"[{count}]:   ", style="green")


class CellEditor(TextArea):
    """Editor widget for cell content."""
    
    def __init__(self, cell: Cell, **kwargs):
        super().__init__(
            cell.source,
            language="python" if cell.cell_type == CellType.CODE else "markdown",
            theme="monokai",
            show_line_numbers=True,
            **kwargs
        )
        self.cell = cell
        
    def on_mount(self) -> None:
        """Set up cursor tracking when mounted."""
        super().on_mount()
        # Set cursor style for insert mode
        self.cursor_type = "bar"
        self.cursor_blink = True
        # Force focus to ensure cursor is visible
        self.focus()
        
    def on_blur(self) -> None:
        """Save content when editor loses focus."""
        if self.cell.source != self.text:
            self.cell.source = self.text
            # Mark notebook as having temporary changes
            if hasattr(self.cell, '_notebook') and self.cell._notebook:
                self.cell._notebook._backup_original_state()
                self.cell._notebook._temp_changes = True
                self.cell._notebook.modified = True
        
    def watch_cursor_position(self, cursor_position) -> None:
        """Track cursor position changes."""
        # Update status bar with cursor position
        if hasattr(self.app, 'notebook_view') and self.app.notebook_view and self.app.notebook_view.status_bar:
            line = cursor_position[0] + 1  # 1-based indexing
            column = cursor_position[1] + 1
            self.app.notebook_view.status_bar.update_cursor_position(line, column)
            
    def on_key(self, event) -> None:
        """Handle key events and update content in real-time."""
        super().on_key(event)
        # Update cell content immediately and track changes
        if self.cell.source != self.text:
            self.cell.source = self.text
            # Mark notebook as having temporary changes
            if hasattr(self.cell, '_notebook') and self.cell._notebook:
                self.cell._notebook._backup_original_state()
                self.cell._notebook._temp_changes = True
                self.cell._notebook.modified = True
        # Force refresh to show changes
        self.refresh()


class OutputDisplay(Container):
    """Widget for displaying cell outputs."""
    
    def __init__(self, outputs: List[CellOutput]):
        super().__init__(classes="cell-output-container")
        self.outputs = outputs
        self.renderer_registry = create_default_registry()
        self.collapsed = False
        
    def compose(self) -> ComposeResult:
        """Compose the output display."""
        if not self.outputs:
            return
            
        # Output header with collapse toggle
        output_count = len(self.outputs)
        header_text = f"Output ({output_count} items)" if output_count > 1 else "Output"
        yield Static(Text(f"▼ {header_text}", style="bold cyan"), classes="output-header")
        
        # Render outputs
        if not self.collapsed:
            with Vertical(classes="output-content"):
                for i, output in enumerate(self.outputs):
                    if output.output_type == 'stream':
                        stream_name = output.name or 'stdout'
                        style = "green" if stream_name == 'stdout' else "red"
                        yield Static(
                            Panel(
                                Text(output.text or '', style=style),
                                title=f"[{stream_name}]",
                                border_style=style
                            ),
                            classes="output-item"
                        )
                    elif output.output_type == 'error':
                        renderer = self.renderer_registry.get_renderer('error')
                        yield Static(
                            renderer.render({
                                'ename': output.ename,
                                'evalue': output.evalue,
                                'traceback': output.traceback
                            }),
                            classes="output-item"
                        )
                    elif output.output_type in ['display_data', 'execute_result']:
                        # Try different MIME types in order of preference
                        mime_priority = [
                            'text/html', 'text/markdown', 'text/latex',
                            'application/json', 'text/plain'
                        ]
                        
                        for mime_type in mime_priority:
                            if mime_type in output.data:
                                renderer = self.renderer_registry.get_renderer(mime_type)
                                if renderer:
                                    result_style = "blue" if output.output_type == 'execute_result' else "cyan"
                                    yield Static(
                                        Panel(
                                            renderer.render(output.data[mime_type], output.metadata),
                                            title=f"[{output.output_type}]",
                                            border_style=result_style
                                        ),
                                        classes="output-item"
                                    )
                                    break
    
    def toggle_collapsed(self):
        """Toggle output collapse state."""
        self.collapsed = not self.collapsed
        self.refresh()
        
    def update_outputs(self, outputs: List[CellOutput]):
        """Update the outputs and refresh display."""
        self.outputs = outputs
        self.refresh()


class CellWidget(Container):
    """Widget representing a notebook cell."""
    
    BINDINGS = [
        ("ctrl+enter", "execute", "Execute"),
        ("shift+enter", "execute_next", "Execute and Next"),
        ("escape", "command_mode", "Command Mode"),
    ]
    
    selected = reactive(False)
    editing = reactive(False)
    
    def __init__(self, cell: Cell, index: int):
        super().__init__()
        self.cell = cell
        self.index = index
        self.editor: Optional[CellEditor] = None
        self.output_display: Optional[OutputDisplay] = None
        
        # Set cell type CSS class
        if cell.cell_type == CellType.CODE:
            self.add_class("code-cell")
        elif cell.cell_type == CellType.MARKDOWN:
            self.add_class("markdown-cell")
        elif cell.cell_type == CellType.RAW:
            self.add_class("raw-cell")
        
    def compose(self) -> ComposeResult:
        """Compose the cell widget."""
        with Horizontal(classes="cell-container"):
            yield CellIndicator(self.cell)
            
            with Vertical(classes="cell-content"):
                if self.editing:
                    self.editor = CellEditor(self.cell, classes="cell-editor")
                    yield self.editor
                    # Schedule focus after compose
                    self.set_timer(0.1, self._focus_editor)
                else:
                    # Display cell source as syntax-highlighted static content
                    if self.cell.cell_type == CellType.CODE:
                        yield Static(
                            Syntax(
                                self.cell.source or " ",
                                "python",
                                theme="monokai",
                                line_numbers=True
                            ),
                            classes="cell-source"
                        )
                    elif self.cell.cell_type == CellType.MARKDOWN:
                        from rich.markdown import Markdown
                        yield Static(
                            Markdown(self.cell.source or " "),
                            classes="cell-source"
                        )
                    else:  # RAW cell
                        yield Static(
                            Text(self.cell.source or " ", style="dim white"),
                            classes="cell-source"
                        )
                        
                # Display outputs for code cells
                if self.cell.cell_type == CellType.CODE and self.cell.outputs:
                    self.output_display = OutputDisplay(self.cell.outputs)
                    yield self.output_display
                    
    def watch_selected(self, selected: bool) -> None:
        """React to selection changes."""
        if selected:
            self.add_class("selected")
            # Clear cursor position when cell is not being edited
            if not self.editing and hasattr(self.app, 'notebook_view') and self.app.notebook_view and self.app.notebook_view.status_bar:
                self.app.notebook_view.status_bar.update_cursor_position(0, 0)
        else:
            self.remove_class("selected")
            if self.editing:
                self.editing = False
                
    def watch_editing(self, editing: bool) -> None:
        """React to editing mode changes."""
        if editing:
            self.add_class("editing")
            # Force recompose to show editor
            self.refresh(layout=True)
        else:
            self.remove_class("editing")
            # Clear cursor position when exiting edit mode
            if hasattr(self.app, 'notebook_view') and self.app.notebook_view and self.app.notebook_view.status_bar:
                self.app.notebook_view.status_bar.update_cursor_position(0, 0)
            # Force recompose to show static content
            self.refresh(layout=True)
        
    def enter_edit_mode(self) -> None:
        """Enter edit mode."""
        if not self.editing:
            self.editing = True
                
    def _focus_editor(self) -> None:
        """Focus the editor after recompose."""
        if self.editor:
            self.editor.focus()
            # Set cursor style for insert mode
            self.editor.cursor_type = "bar"
            self.editor.cursor_blink = True
            # Force refresh to apply cursor changes
            self.editor.refresh()
                
    def exit_edit_mode(self) -> None:
        """Exit edit mode."""
        if self.editing:
            self.editing = False
            # Set cursor style for command mode
            if self.editor:
                self.editor.cursor_type = "block"
                self.editor.cursor_blink = False
            
    def update_output(self) -> None:
        """Update the output display."""
        if self.output_display:
            self.output_display.update_outputs(self.cell.outputs)
        else:
            self.refresh()
            
    def on_click(self) -> None:
        """Handle click events."""
        self.post_message(CellSelected(self))
        
    def on_key(self, event: events.Key) -> None:
        """Handle key events."""
        if event.key == "enter" and not self.editing:
            self.enter_edit_mode()
            event.stop()
        elif event.key == "escape" and self.editing:
            self.exit_edit_mode()
            event.stop()


class CellSelected(events.Event):
    """Event emitted when a cell is selected."""
    
    def __init__(self, cell_widget: CellWidget):
        super().__init__()
        self.cell_widget = cell_widget