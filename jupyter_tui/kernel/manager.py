"""Kernel management system for Jupyter TUI."""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Optional, Any, Callable, List
from pathlib import Path

import zmq
import zmq.asyncio
from jupyter_client import AsyncKernelManager, AsyncKernelClient
from jupyter_client.kernelspec import KernelSpecManager


class KernelConnection:
    """Manages ZeroMQ connections to a Jupyter kernel."""
    
    def __init__(self, kernel_manager: AsyncKernelManager):
        self.kernel_manager = kernel_manager
        self.client: Optional[AsyncKernelClient] = None
        self.session_id = str(uuid.uuid4())
        self.execution_count = 0
        self.msg_handlers: Dict[str, List[Callable]] = {
            'execute_reply': [],
            'execute_input': [],
            'execute_result': [],
            'stream': [],
            'error': [],
            'status': [],
            'clear_output': [],
            'display_data': [],
            'update_display_data': [],
        }
        
    async def start(self):
        """Start the kernel and establish connections."""
        await self.kernel_manager.start_kernel()
        self.client = self.kernel_manager.client()
        self.client.start_channels()
        await self.client.wait_for_ready()
        
        # Start message listeners
        asyncio.create_task(self._listen_iopub())
        asyncio.create_task(self._listen_shell())
        
    async def stop(self):
        """Stop the kernel and close connections."""
        if self.client:
            self.client.stop_channels()
        await self.kernel_manager.shutdown_kernel()
        
    def add_handler(self, msg_type: str, handler: Callable):
        """Add a message handler for a specific message type."""
        if msg_type in self.msg_handlers:
            self.msg_handlers[msg_type].append(handler)
            
    def remove_handler(self, msg_type: str, handler: Callable):
        """Remove a message handler."""
        if msg_type in self.msg_handlers and handler in self.msg_handlers[msg_type]:
            self.msg_handlers[msg_type].remove(handler)
            
    async def execute(self, code: str, silent: bool = False) -> str:
        """Execute code in the kernel."""
        if not self.client:
            raise RuntimeError("Kernel client not initialized")
            
        self.execution_count += 1
        msg_id = self.client.execute(
            code,
            silent=silent,
            user_expressions={},
            allow_stdin=False
        )
        return msg_id
        
    async def complete(self, code: str, cursor_pos: int) -> Dict[str, Any]:
        """Get code completions at cursor position."""
        if not self.client:
            raise RuntimeError("Kernel client not initialized")
            
        msg_id = self.client.complete(code, cursor_pos)
        reply = await self._wait_for_reply(msg_id, 'complete_reply')
        return reply.get('content', {})
        
    async def inspect(self, code: str, cursor_pos: int) -> Dict[str, Any]:
        """Get object inspection at cursor position."""
        if not self.client:
            raise RuntimeError("Kernel client not initialized")
            
        msg_id = self.client.inspect(code, cursor_pos)
        reply = await self._wait_for_reply(msg_id, 'inspect_reply')
        return reply.get('content', {})
        
    async def interrupt(self):
        """Interrupt kernel execution."""
        await self.kernel_manager.interrupt_kernel()
        
    async def restart(self):
        """Restart the kernel."""
        await self.kernel_manager.restart_kernel()
        await self.client.wait_for_ready()
        self.execution_count = 0
        
    async def _listen_iopub(self):
        """Listen for IOPub messages."""
        while True:
            try:
                msg = await self.client.get_iopub_msg()
                msg_type = msg['msg_type']
                if msg_type in self.msg_handlers:
                    for handler in self.msg_handlers[msg_type]:
                        await handler(msg)
            except Exception as e:
                # Log error but continue listening
                pass
                
    async def _listen_shell(self):
        """Listen for shell messages."""
        while True:
            try:
                msg = await self.client.get_shell_msg()
                msg_type = msg['msg_type']
                if msg_type in self.msg_handlers:
                    for handler in self.msg_handlers[msg_type]:
                        await handler(msg)
            except Exception as e:
                # Log error but continue listening
                pass
                
    async def _wait_for_reply(self, msg_id: str, reply_type: str, timeout: float = 10.0) -> Dict[str, Any]:
        """Wait for a specific reply message."""
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            try:
                reply = await asyncio.wait_for(
                    self.client.get_shell_msg(),
                    timeout=deadline - asyncio.get_event_loop().time()
                )
                if reply.get('parent_header', {}).get('msg_id') == msg_id and reply['msg_type'] == reply_type:
                    return reply
            except asyncio.TimeoutError:
                break
        raise TimeoutError(f"Timeout waiting for {reply_type}")


class KernelManager:
    """Manages multiple kernel connections."""
    
    def __init__(self):
        self.kernels: Dict[str, KernelConnection] = {}
        self.kernel_spec_manager = KernelSpecManager()
        self.active_kernel_id: Optional[str] = None
        
    def list_kernel_specs(self) -> Dict[str, Any]:
        """List available kernel specifications."""
        return self.kernel_spec_manager.get_all_specs()
        
    async def create_kernel(self, kernel_name: str = 'jupyter-tui-kernel') -> str:
        """Create a new kernel connection."""
        kernel_id = str(uuid.uuid4())
        manager = AsyncKernelManager(kernel_name=kernel_name)
        connection = KernelConnection(manager)
        await connection.start()
        
        self.kernels[kernel_id] = connection
        if not self.active_kernel_id:
            self.active_kernel_id = kernel_id
            
        return kernel_id
        
    async def shutdown_kernel(self, kernel_id: str):
        """Shutdown a kernel."""
        if kernel_id in self.kernels:
            await self.kernels[kernel_id].stop()
            del self.kernels[kernel_id]
            
            if self.active_kernel_id == kernel_id:
                self.active_kernel_id = next(iter(self.kernels.keys()), None)
                
    async def shutdown_all(self):
        """Shutdown all kernels."""
        for kernel_id in list(self.kernels.keys()):
            await self.shutdown_kernel(kernel_id)
            
    def get_kernel(self, kernel_id: Optional[str] = None) -> Optional[KernelConnection]:
        """Get a kernel connection by ID or return active kernel."""
        if kernel_id:
            return self.kernels.get(kernel_id)
        elif self.active_kernel_id:
            return self.kernels.get(self.active_kernel_id)
        return None
        
    def set_active_kernel(self, kernel_id: str):
        """Set the active kernel."""
        if kernel_id in self.kernels:
            self.active_kernel_id = kernel_id