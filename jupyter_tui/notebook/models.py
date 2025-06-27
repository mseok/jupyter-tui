"""Notebook and cell models for Jupyter TUI."""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Union

import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell, new_raw_cell


class CellType(Enum):
    """Cell type enumeration."""
    CODE = "code"
    MARKDOWN = "markdown"
    RAW = "raw"


class CellState(Enum):
    """Cell execution state."""
    IDLE = "idle"
    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"


@dataclass
class CellOutput:
    """Represents a cell output."""
    output_type: str  # stream, display_data, execute_result, error
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    text: Optional[str] = None
    name: Optional[str] = None  # For stream outputs (stdout/stderr)
    execution_count: Optional[int] = None
    ename: Optional[str] = None  # For error outputs
    evalue: Optional[str] = None
    traceback: Optional[List[str]] = None
    
    def to_nbformat(self) -> Dict[str, Any]:
        """Convert to nbformat output dict."""
        output = {
            'output_type': self.output_type,
        }
        
        if self.output_type == 'stream':
            output['name'] = self.name or 'stdout'
            output['text'] = self.text or ''
        elif self.output_type == 'display_data' or self.output_type == 'execute_result':
            output['data'] = self.data
            output['metadata'] = self.metadata
            if self.output_type == 'execute_result' and self.execution_count:
                output['execution_count'] = self.execution_count
        elif self.output_type == 'error':
            output['ename'] = self.ename or ''
            output['evalue'] = self.evalue or ''
            output['traceback'] = self.traceback or []
            
        return output


@dataclass
class Cell:
    """Represents a notebook cell."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cell_type: CellType = CellType.CODE
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_count: Optional[int] = None
    outputs: List[CellOutput] = field(default_factory=list)
    state: CellState = CellState.IDLE
    msg_id: Optional[str] = None  # Active execution message ID
    
    def clear_outputs(self):
        """Clear cell outputs."""
        self.outputs.clear()
        self.state = CellState.IDLE
        
    def add_output(self, output: CellOutput):
        """Add output to cell."""
        self.outputs.append(output)
        
    def to_nbformat(self) -> Dict[str, Any]:
        """Convert to nbformat cell dict."""
        cell_dict = {
            'id': self.id,
            'cell_type': self.cell_type.value,
            'metadata': self.metadata,
            'source': self.source,
        }
        
        if self.cell_type == CellType.CODE:
            cell_dict['execution_count'] = self.execution_count
            cell_dict['outputs'] = [output.to_nbformat() for output in self.outputs]
            
        return cell_dict
        
    @classmethod
    def from_nbformat(cls, cell_dict: Dict[str, Any]) -> 'Cell':
        """Create cell from nbformat dict."""
        cell_type = CellType(cell_dict['cell_type'])
        cell = cls(
            id=cell_dict.get('id', str(uuid.uuid4())),
            cell_type=cell_type,
            source=cell_dict.get('source', ''),
            metadata=cell_dict.get('metadata', {}),
        )
        
        if cell_type == CellType.CODE:
            cell.execution_count = cell_dict.get('execution_count')
            for output_dict in cell_dict.get('outputs', []):
                output = CellOutput(
                    output_type=output_dict['output_type'],
                    data=output_dict.get('data', {}),
                    metadata=output_dict.get('metadata', {}),
                    text=output_dict.get('text'),
                    name=output_dict.get('name'),
                    execution_count=output_dict.get('execution_count'),
                    ename=output_dict.get('ename'),
                    evalue=output_dict.get('evalue'),
                    traceback=output_dict.get('traceback'),
                )
                cell.outputs.append(output)
                
        return cell


@dataclass
class Notebook:
    """Represents a Jupyter notebook."""
    cells: List[Cell] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    nbformat: int = 4
    nbformat_minor: int = 5
    current_cell_index: int = 0
    filepath: Optional[str] = None
    modified: bool = False
    
    def add_cell(self, cell: Cell, index: Optional[int] = None):
        """Add a cell to the notebook."""
        if index is None:
            self.cells.append(cell)
        else:
            self.cells.insert(index, cell)
        self.modified = True
        
    def remove_cell(self, index: int):
        """Remove a cell from the notebook."""
        if 0 <= index < len(self.cells):
            self.cells.pop(index)
            if self.current_cell_index >= len(self.cells) and self.current_cell_index > 0:
                self.current_cell_index = len(self.cells) - 1
            self.modified = True
            
    def move_cell(self, from_index: int, to_index: int):
        """Move a cell to a new position."""
        if 0 <= from_index < len(self.cells) and 0 <= to_index < len(self.cells):
            cell = self.cells.pop(from_index)
            self.cells.insert(to_index, cell)
            self.modified = True
            
    def get_current_cell(self) -> Optional[Cell]:
        """Get the current cell."""
        if 0 <= self.current_cell_index < len(self.cells):
            return self.cells[self.current_cell_index]
        return None
        
    def next_cell(self):
        """Move to next cell."""
        if self.current_cell_index < len(self.cells) - 1:
            self.current_cell_index += 1
            
    def previous_cell(self):
        """Move to previous cell."""
        if self.current_cell_index > 0:
            self.current_cell_index -= 1
            
    def to_nbformat(self) -> nbformat.NotebookNode:
        """Convert to nbformat notebook."""
        nb = new_notebook()
        nb.metadata = self.metadata
        nb.cells = [nbformat.from_dict(cell.to_nbformat()) for cell in self.cells]
        return nb
        
    @classmethod
    def from_nbformat(cls, nb: nbformat.NotebookNode) -> 'Notebook':
        """Create notebook from nbformat."""
        notebook = cls(
            metadata=dict(nb.metadata),
            nbformat=nb.nbformat,
            nbformat_minor=nb.nbformat_minor,
        )
        
        for cell_dict in nb.cells:
            cell = Cell.from_nbformat(dict(cell_dict))
            notebook.cells.append(cell)
            
        return notebook
        
    def save(self, filepath: Optional[str] = None):
        """Save notebook to file."""
        if filepath:
            self.filepath = filepath
        if not self.filepath:
            raise ValueError("No filepath specified")
            
        nb = self.to_nbformat()
        with open(self.filepath, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        self.modified = False
        
    @classmethod
    def load(cls, filepath: str) -> 'Notebook':
        """Load notebook from file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        notebook = cls.from_nbformat(nb)
        notebook.filepath = filepath
        return notebook