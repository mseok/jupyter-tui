#!/usr/bin/env python3
"""Quick test with 5-second auto-shutdown."""

import asyncio
from jupyter_tui.app import JupyterTUI


class QuickTestApp(JupyterTUI):
    """Quick test version with 5-second auto-shutdown."""
    
    async def on_mount(self) -> None:
        """Initialize with quick shutdown."""
        await super().on_mount()
        # Auto-shutdown after 5 seconds
        asyncio.create_task(self._quick_shutdown())
        
    async def _quick_shutdown(self):
        """Auto-shutdown after 5 seconds."""
        await asyncio.sleep(5)
        print("[DEBUG] Quick test completed - auto-shutting down")
        self.exit()


if __name__ == "__main__":
    app = QuickTestApp('demo_notebook.ipynb')
    app.run()