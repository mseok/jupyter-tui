"""Main notebook view widget."""

from typing import Optional, List, Dict, Any
import asyncio
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Header, Footer, Static, Label
from textual.reactive import reactive
from textual.binding import Binding
from textual import events

from ..notebook.models import Notebook, Cell, CellType, CellState, CellOutput
from ..kernel.manager import KernelManager
from .cell_widget import CellWidget, CellSelected


class NotebookView(Container):
    """Main notebook view container."""
    
    BINDINGS = [
        Binding("j", "next_cell", "Next Cell", key_display="j"),
        Binding("k", "previous_cell", "Previous Cell", key_display="k"),
        Binding("a", "insert_above", "Insert Above", key_display="a"),
        Binding("b", "insert_below", "Insert Below", key_display="b"),
        Binding("d,d", "delete_cell", "Delete Cell", key_display="dd"),
        Binding("m", "to_markdown", "To Markdown", key_display="m"),
        Binding("y", "to_code", "To Code", key_display="y"),
        Binding("ctrl+s", "save", "Save", key_display="^S"),
        Binding("ctrl+enter", "execute", "Execute", key_display="^Enter"),
        Binding("shift+enter", "execute_next", "Execute & Next", key_display="S-Enter"),
        Binding("ctrl+c", "interrupt", "Interrupt", key_display="^C"),
        Binding("0,0", "restart_kernel", "Restart Kernel", key_display="00"),
        Binding("g,g", "go_top", "Go to Top", key_display="gg"),
        Binding("shift+g", "go_bottom", "Go to Bottom", key_display="G"),
        Binding("enter", "edit_cell", "Edit Cell", key_display="Enter"),
        Binding("escape", "command_mode", "Command Mode", key_display="Esc"),
    ]
    
    def __init__(self, notebook: Notebook, kernel_manager: KernelManager):
        super().__init__()
        self.notebook = notebook
        self.kernel_manager = kernel_manager
        self.cell_widgets: List[CellWidget] = []
        self.selected_index = 0
        self.mode = "command"  # command or insert
        
    def compose(self) -> ComposeResult:
        """Compose the notebook view."""
        with ScrollableContainer(id="notebook-container"):
            with Vertical(id="cells-container"):
                for i, cell in enumerate(self.notebook.cells):
                    cell_widget = CellWidget(cell, i)
                    self.cell_widgets.append(cell_widget)
                    yield cell_widget
                    
        # Select first cell
        if self.cell_widgets:
            self.cell_widgets[0].selected = True
            
    def on_mount(self) -> None:
        """Set up kernel message handlers when mounted."""
        kernel = self.kernel_manager.get_kernel()
        if kernel:
            kernel.add_handler('stream', self._handle_stream)
            kernel.add_handler('execute_result', self._handle_execute_result)
            kernel.add_handler('display_data', self._handle_display_data)
            kernel.add_handler('error', self._handle_error)
            kernel.add_handler('status', self._handle_status)
            
    async def _handle_stream(self, msg: Dict[str, Any]) -> None:
        """Handle stream output messages."""
        content = msg.get('content', {})
        parent_id = msg.get('parent_header', {}).get('msg_id')
        
        # Find cell by message ID
        for cell_widget in self.cell_widgets:
            if cell_widget.cell.msg_id == parent_id:
                output = CellOutput(
                    output_type='stream',
                    name=content.get('name', 'stdout'),
                    text=content.get('text', '')
                )
                cell_widget.cell.add_output(output)
                cell_widget.update_output()
                break
                
    async def _handle_execute_result(self, msg: Dict[str, Any]) -> None:
        """Handle execute result messages."""
        content = msg.get('content', {})
        parent_id = msg.get('parent_header', {}).get('msg_id')
        
        for cell_widget in self.cell_widgets:
            if cell_widget.cell.msg_id == parent_id:
                output = CellOutput(
                    output_type='execute_result',
                    data=content.get('data', {}),
                    metadata=content.get('metadata', {}),
                    execution_count=content.get('execution_count')
                )
                cell_widget.cell.add_output(output)
                cell_widget.update_output()
                break
                
    async def _handle_display_data(self, msg: Dict[str, Any]) -> None:
        """Handle display data messages."""
        content = msg.get('content', {})
        parent_id = msg.get('parent_header', {}).get('msg_id')
        
        for cell_widget in self.cell_widgets:
            if cell_widget.cell.msg_id == parent_id:
                output = CellOutput(
                    output_type='display_data',
                    data=content.get('data', {}),
                    metadata=content.get('metadata', {})
                )
                cell_widget.cell.add_output(output)
                cell_widget.update_output()
                break
                
    async def _handle_error(self, msg: Dict[str, Any]) -> None:
        """Handle error messages."""
        content = msg.get('content', {})
        parent_id = msg.get('parent_header', {}).get('msg_id')
        
        for cell_widget in self.cell_widgets:
            if cell_widget.cell.msg_id == parent_id:
                output = CellOutput(
                    output_type='error',
                    ename=content.get('ename'),
                    evalue=content.get('evalue'),
                    traceback=content.get('traceback', [])
                )
                cell_widget.cell.add_output(output)
                cell_widget.cell.state = CellState.ERROR
                cell_widget.update_output()
                break
                
    async def _handle_status(self, msg: Dict[str, Any]) -> None:
        """Handle kernel status messages."""
        content = msg.get('content', {})
        execution_state = content.get('execution_state')
        
        if execution_state == 'idle':
            # Mark any running cells as finished
            for cell_widget in self.cell_widgets:
                if cell_widget.cell.state == CellState.RUNNING:
                    cell_widget.cell.state = CellState.FINISHED
                    cell_widget.refresh()
                    
    def on_cell_selected(self, event: CellSelected) -> None:
        """Handle cell selection events."""
        # Deselect all cells
        for widget in self.cell_widgets:
            widget.selected = False
            
        # Select the clicked cell
        event.cell_widget.selected = True
        self.selected_index = event.cell_widget.index
        
    def action_next_cell(self) -> None:
        """Move to next cell."""
        if self.selected_index < len(self.cell_widgets) - 1:
            self.cell_widgets[self.selected_index].selected = False
            self.selected_index += 1
            self.cell_widgets[self.selected_index].selected = True
            self.cell_widgets[self.selected_index].scroll_visible()
            
    def action_previous_cell(self) -> None:
        """Move to previous cell."""
        if self.selected_index > 0:
            self.cell_widgets[self.selected_index].selected = False
            self.selected_index -= 1
            self.cell_widgets[self.selected_index].selected = True
            self.cell_widgets[self.selected_index].scroll_visible()
            
    def action_go_top(self) -> None:
        """Go to first cell."""
        if self.cell_widgets:
            self.cell_widgets[self.selected_index].selected = False
            self.selected_index = 0
            self.cell_widgets[0].selected = True
            self.cell_widgets[0].scroll_visible()
            
    def action_go_bottom(self) -> None:
        """Go to last cell."""
        if self.cell_widgets:
            self.cell_widgets[self.selected_index].selected = False
            self.selected_index = len(self.cell_widgets) - 1
            self.cell_widgets[self.selected_index].selected = True
            self.cell_widgets[self.selected_index].scroll_visible()
            
    def action_edit_cell(self) -> None:
        """Enter edit mode for current cell."""
        if self.selected_index < len(self.cell_widgets):
            self.cell_widgets[self.selected_index].enter_edit_mode()
            self.mode = "insert"
            
    def action_command_mode(self) -> None:
        """Enter command mode."""
        if self.selected_index < len(self.cell_widgets):
            self.cell_widgets[self.selected_index].exit_edit_mode()
            self.mode = "command"
            
    def action_insert_above(self) -> None:
        """Insert a new cell above current cell."""
        new_cell = Cell(cell_type=CellType.CODE)
        self.notebook.add_cell(new_cell, self.selected_index)
        self._refresh_cells()
        
    def action_insert_below(self) -> None:
        """Insert a new cell below current cell."""
        new_cell = Cell(cell_type=CellType.CODE)
        self.notebook.add_cell(new_cell, self.selected_index + 1)
        self._refresh_cells()
        self.action_next_cell()
        
    def action_delete_cell(self) -> None:
        """Delete current cell."""
        if len(self.notebook.cells) > 1:  # Keep at least one cell
            self.notebook.remove_cell(self.selected_index)
            self._refresh_cells()
            if self.selected_index >= len(self.cell_widgets):
                self.selected_index = len(self.cell_widgets) - 1
            if self.cell_widgets:
                self.cell_widgets[self.selected_index].selected = True
                
    def action_to_markdown(self) -> None:
        """Convert current cell to markdown."""
        if self.selected_index < len(self.notebook.cells):
            cell = self.notebook.cells[self.selected_index]
            if cell.cell_type != CellType.MARKDOWN:
                cell.cell_type = CellType.MARKDOWN
                cell.clear_outputs()
                self._refresh_cells()
                
    def action_to_code(self) -> None:
        """Convert current cell to code."""
        if self.selected_index < len(self.notebook.cells):
            cell = self.notebook.cells[self.selected_index]
            if cell.cell_type != CellType.CODE:
                cell.cell_type = CellType.CODE
                self._refresh_cells()
                
    async def action_execute(self) -> None:
        """Execute current cell."""
        if self.selected_index < len(self.notebook.cells):
            cell = self.notebook.cells[self.selected_index]
            if cell.cell_type == CellType.CODE:
                await self._execute_cell(cell)
                
    async def action_execute_next(self) -> None:
        """Execute current cell and move to next."""
        await self.action_execute()
        self.action_next_cell()
        
    async def _execute_cell(self, cell: Cell) -> None:
        """Execute a code cell."""
        kernel = self.kernel_manager.get_kernel()
        if not kernel:
            return
            
        # Clear outputs and set state
        cell.clear_outputs()
        cell.state = CellState.RUNNING
        
        # Get widget and refresh
        widget = self.cell_widgets[self.notebook.cells.index(cell)]
        widget.refresh()
        
        # Execute code
        try:
            msg_id = await kernel.execute(cell.source)
            cell.msg_id = msg_id
            
            # Update execution count
            kernel_conn = kernel
            cell.execution_count = kernel_conn.execution_count
            
        except Exception as e:
            cell.state = CellState.ERROR
            output = CellOutput(
                output_type='error',
                ename=type(e).__name__,
                evalue=str(e),
                traceback=[]
            )
            cell.add_output(output)
            widget.update_output()
            
    async def action_interrupt(self) -> None:
        """Interrupt kernel execution."""
        kernel = self.kernel_manager.get_kernel()
        if kernel:
            await kernel.interrupt()
            
    async def action_restart_kernel(self) -> None:
        """Restart the kernel."""
        kernel = self.kernel_manager.get_kernel()
        if kernel:
            await kernel.restart()
            # Clear all cell states
            for cell in self.notebook.cells:
                if cell.cell_type == CellType.CODE:
                    cell.state = CellState.IDLE
                    cell.execution_count = None
            self._refresh_cells()
            
    def action_save(self) -> None:
        """Save the notebook."""
        if self.notebook.filepath:
            self.notebook.save()
            self.notify("Notebook saved", severity="information")
        else:
            self.notify("No filepath set", severity="warning")
            
    def _refresh_cells(self) -> None:
        """Refresh the cell display."""
        # This is a simple implementation - in production you'd want
        # more efficient updating
        container = self.query_one("#cells-container")
        container.remove_children()
        
        self.cell_widgets.clear()
        for i, cell in enumerate(self.notebook.cells):
            cell_widget = CellWidget(cell, i)
            self.cell_widgets.append(cell_widget)
            container.mount(cell_widget)
            
        if self.cell_widgets and self.selected_index < len(self.cell_widgets):
            self.cell_widgets[self.selected_index].selected = True