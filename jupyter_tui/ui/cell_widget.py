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
        if self.cell.cell_type != CellType.CODE:
            return " " * 7
            
        if self.cell.state == CellState.IDLE:
            count = self.cell.execution_count
            if count is None:
                return "[ ]:   "
            else:
                return f"[{count}]:  "
        elif self.cell.state == CellState.PENDING:
            return "[...]: "
        elif self.cell.state == CellState.RUNNING:
            return "[*]:   "
        elif self.cell.state == CellState.ERROR:
            return "[!]:   "
        else:
            count = self.cell.execution_count or " "
            return f"[{count}]:  "


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
        
    def on_blur(self) -> None:
        """Save content when editor loses focus."""
        self.cell.source = self.text


class OutputDisplay(Static):
    """Widget for displaying cell outputs."""
    
    def __init__(self, outputs: List[CellOutput]):
        super().__init__()
        self.outputs = outputs
        self.renderer_registry = create_default_registry()
        
    def render(self) -> RenderableType:
        if not self.outputs:
            return ""
            
        rendered_outputs = []
        
        for output in self.outputs:
            if output.output_type == 'stream':
                rendered_outputs.append(Text(output.text or '', style="dim"))
            elif output.output_type == 'error':
                renderer = self.renderer_registry.get_renderer('error')
                rendered_outputs.append(renderer.render({
                    'ename': output.ename,
                    'evalue': output.evalue,
                    'traceback': output.traceback
                }))
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
                            rendered_outputs.append(
                                renderer.render(output.data[mime_type], output.metadata)
                            )
                            break
                            
        return Vertical(*rendered_outputs)


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
        
    def compose(self) -> ComposeResult:
        """Compose the cell widget."""
        with Horizontal(classes="cell-container"):
            yield CellIndicator(self.cell)
            
            with Vertical(classes="cell-content"):
                if self.editing:
                    self.editor = CellEditor(self.cell, classes="cell-editor")
                    yield self.editor
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
                    else:
                        yield Static(
                            Text(self.cell.source or " ", style="italic"),
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
        else:
            self.remove_class("selected")
            if self.editing:
                self.editing = False
                
    def watch_editing(self, editing: bool) -> None:
        """React to editing mode changes."""
        if editing:
            self.add_class("editing")
        else:
            self.remove_class("editing")
        self.refresh()
        
    def enter_edit_mode(self) -> None:
        """Enter edit mode."""
        if not self.editing:
            self.editing = True
            if self.editor:
                self.editor.focus()
                
    def exit_edit_mode(self) -> None:
        """Exit edit mode."""
        if self.editing:
            self.editing = False
            
    def update_output(self) -> None:
        """Update the output display."""
        if self.output_display:
            self.output_display.outputs = self.cell.outputs
            self.output_display.refresh()
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