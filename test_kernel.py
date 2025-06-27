#!/usr/bin/env python3
"""Test kernel creation."""

import asyncio
from jupyter_tui.kernel.manager import KernelManager


async def test_kernel():
    """Test kernel functionality."""
    print("Creating kernel manager...")
    km = KernelManager()
    
    print("Available kernels:", km.list_kernel_specs())
    
    print("Creating Python kernel...")
    try:
        kernel_id = await km.create_kernel()
        print(f"Kernel created with ID: {kernel_id}")
        
        kernel = km.get_kernel()
        print("Executing code...")
        msg_id = await kernel.execute("2 + 2")
        print(f"Execution message ID: {msg_id}")
        
        await asyncio.sleep(2)
        
        print("Shutting down kernel...")
        await km.shutdown_all()
        print("Done!")
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_kernel())