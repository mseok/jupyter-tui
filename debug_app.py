#!/usr/bin/env python3
"""Debug version of the app with auto-shutdown and cell debugging."""

import asyncio
from jupyter_tui.app import JupyterTUI
from jupyter_tui.notebook.models import Notebook


class DebugJupyterTUI(JupyterTUI):
    """Debug version with auto-shutdown."""
    
    def __init__(self, notebook_path=None, auto_shutdown_seconds=60):
        super().__init__(notebook_path)
        self.auto_shutdown_seconds = auto_shutdown_seconds
        self.debug_mode = True
        
    async def on_mount(self) -> None:
        """Initialize with debugging."""
        print(f"[DEBUG] Starting app initialization...")
        
        # Start auto-shutdown timer
        if self.auto_shutdown_seconds > 0:
            asyncio.create_task(self._auto_shutdown())
            
        await super().on_mount()
        
        # Debug notebook loading
        if self.notebook:
            print(f"[DEBUG] Loaded notebook with {len(self.notebook.cells)} cells")
            for i, cell in enumerate(self.notebook.cells):
                print(f"[DEBUG] Cell {i}: {cell.cell_type} - {len(cell.source)} chars")
                
        # Debug UI components
        if self.notebook_view:
            print(f"[DEBUG] NotebookView created with {len(self.notebook_view.cell_widgets)} widgets")
            
        if self.status_bar:
            print(f"[DEBUG] StatusBar created, total_cells: {self.status_bar.total_cells}")
            
    async def _auto_shutdown(self):
        """Auto-shutdown after specified time."""
        print(f"[DEBUG] Auto-shutdown timer started: {self.auto_shutdown_seconds}s")
        await asyncio.sleep(self.auto_shutdown_seconds)
        print(f"[DEBUG] Auto-shutdown triggered after {self.auto_shutdown_seconds}s")
        self.exit()


async def main():
    """Run debug app."""
    app = DebugJupyterTUI('demo_notebook.ipynb', auto_shutdown_seconds=60)
    try:
        await app.run_async()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[DEBUG] App finished")


if __name__ == "__main__":
    asyncio.run(main())