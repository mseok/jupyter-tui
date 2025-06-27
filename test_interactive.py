#!/usr/bin/env python3
"""Test script for interactive features."""

import asyncio
from jupyter_tui.notebook.models import Notebook, Cell, CellType
from jupyter_tui.kernel.manager import KernelManager


async def test_execution():
    """Test notebook execution."""
    # Create a notebook with some cells
    notebook = Notebook()
    
    # Add cells
    notebook.add_cell(Cell(
        cell_type=CellType.MARKDOWN,
        source="# Test Notebook\n\nThis is a test."
    ))
    
    notebook.add_cell(Cell(
        cell_type=CellType.CODE,
        source="2 + 2"
    ))
    
    notebook.add_cell(Cell(
        cell_type=CellType.CODE,
        source="print('Hello from Jupyter TUI!')"
    ))
    
    notebook.add_cell(Cell(
        cell_type=CellType.CODE,
        source="import sys\nprint(f'Python {sys.version}')"
    ))
    
    # Save the notebook
    notebook.save('demo_notebook.ipynb')
    print("Created demo_notebook.ipynb")
    
    # Create kernel manager
    km = KernelManager()
    kernel_id = await km.create_kernel()
    kernel = km.get_kernel()
    
    print("\nExecuting cells...")
    
    # Execute code cells
    for i, cell in enumerate(notebook.cells):
        if cell.cell_type == CellType.CODE:
            print(f"\nCell {i}: {cell.source[:50]}...")
            
            # Set up output handler
            outputs = []
            
            async def capture_output(msg):
                content = msg.get('content', {})
                if msg['msg_type'] == 'stream':
                    outputs.append(f"OUTPUT: {content.get('text', '').strip()}")
                elif msg['msg_type'] == 'execute_result':
                    data = content.get('data', {})
                    if 'text/plain' in data:
                        outputs.append(f"RESULT: {data['text/plain']}")
                elif msg['msg_type'] == 'error':
                    outputs.append(f"ERROR: {content.get('ename')}: {content.get('evalue')}")
            
            # Add handlers
            kernel.add_handler('stream', capture_output)
            kernel.add_handler('execute_result', capture_output)
            kernel.add_handler('error', capture_output)
            
            # Execute
            msg_id = await kernel.execute(cell.source)
            
            # Wait for execution to complete
            await asyncio.sleep(1)
            
            # Print outputs
            for output in outputs:
                print(f"  {output}")
            
            # Remove handlers
            kernel.remove_handler('stream', capture_output)
            kernel.remove_handler('execute_result', capture_output)
            kernel.remove_handler('error', capture_output)
    
    # Shutdown
    await km.shutdown_all()
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(test_execution())