"""Output renderers for different MIME types."""

from .base import OutputRenderer, RendererRegistry
from .text import (
    PlainTextRenderer, HTMLRenderer, MarkdownRenderer,
    JSONRenderer, LaTeXRenderer, ErrorRenderer, DataFrameRenderer
)

def create_default_registry() -> RendererRegistry:
    """Create a renderer registry with default renderers."""
    registry = RendererRegistry()
    
    # Register renderers in priority order
    registry.register(ErrorRenderer())
    registry.register(DataFrameRenderer())
    registry.register(JSONRenderer())
    registry.register(MarkdownRenderer())
    registry.register(LaTeXRenderer())
    registry.register(HTMLRenderer())
    registry.register(PlainTextRenderer())
    
    return registry

__all__ = [
    'OutputRenderer', 'RendererRegistry', 'create_default_registry',
    'PlainTextRenderer', 'HTMLRenderer', 'MarkdownRenderer',
    'JSONRenderer', 'LaTeXRenderer', 'ErrorRenderer', 'DataFrameRenderer'
]