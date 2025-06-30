#!/usr/bin/env python3
"""Debug script to check cell loading."""

from jupyter_tui.notebook.models import Notebook

# Load the notebook
notebook = Notebook.load('demo_notebook.ipynb')
print(f"Loaded notebook with {len(notebook.cells)} cells:")

for i, cell in enumerate(notebook.cells):
    print(f"Cell {i}: {cell.cell_type} - {cell.source[:50]}...")
    
print("\nNotebook metadata:", notebook.metadata)
print("Notebook filepath:", notebook.filepath)