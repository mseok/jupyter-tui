"""Base classes and interfaces for output renderers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from rich.console import Console, ConsoleOptions, RenderResult
from rich.segment import Segment
from rich.style import Style


class OutputRenderer(ABC):
    """Abstract base class for output renderers."""
    
    @abstractmethod
    def can_render(self, mime_type: str) -> bool:
        """Check if this renderer can handle the given MIME type."""
        pass
        
    @abstractmethod
    def render(self, data: Any, metadata: Dict[str, Any] = None) -> RenderResult:
        """Render the output data."""
        pass


class RendererRegistry:
    """Registry for output renderers."""
    
    def __init__(self):
        self.renderers: List[OutputRenderer] = []
        
    def register(self, renderer: OutputRenderer):
        """Register a renderer."""
        self.renderers.append(renderer)
        
    def get_renderer(self, mime_type: str) -> Optional[OutputRenderer]:
        """Get appropriate renderer for MIME type."""
        for renderer in self.renderers:
            if renderer.can_render(mime_type):
                return renderer
        return None
        
    def render(self, mime_type: str, data: Any, metadata: Dict[str, Any] = None) -> RenderResult:
        """Render data with appropriate renderer."""
        renderer = self.get_renderer(mime_type)
        if renderer:
            return renderer.render(data, metadata)
        else:
            # Fallback to plain text
            return str(data)