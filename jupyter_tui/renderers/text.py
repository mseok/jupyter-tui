"""Text and plain output renderers."""

from typing import Dict, Any
from rich.text import Text
from rich.syntax import Syntax
from rich.console import RenderResult
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
import json

from .base import OutputRenderer


class PlainTextRenderer(OutputRenderer):
    """Renderer for plain text output."""
    
    def can_render(self, mime_type: str) -> bool:
        return mime_type in ['text/plain', 'text']
        
    def render(self, data: Any, metadata: Dict[str, Any] = None) -> RenderResult:
        if isinstance(data, str):
            return Text(data)
        return Text(str(data))


class HTMLRenderer(OutputRenderer):
    """Renderer for HTML output (extracts text content)."""
    
    def can_render(self, mime_type: str) -> bool:
        return mime_type == 'text/html'
        
    def render(self, data: Any, metadata: Dict[str, Any] = None) -> RenderResult:
        # Simple HTML text extraction (could be improved with BeautifulSoup)
        import re
        if isinstance(data, str):
            # Remove HTML tags
            text = re.sub('<[^<]+?>', '', data)
            # Decode HTML entities
            text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            return Panel(Text(text.strip()), title="HTML Output", border_style="blue")
        return Text(str(data))


class MarkdownRenderer(OutputRenderer):
    """Renderer for Markdown output."""
    
    def can_render(self, mime_type: str) -> bool:
        return mime_type == 'text/markdown'
        
    def render(self, data: Any, metadata: Dict[str, Any] = None) -> RenderResult:
        from rich.markdown import Markdown
        if isinstance(data, str):
            return Markdown(data)
        return Text(str(data))


class JSONRenderer(OutputRenderer):
    """Renderer for JSON output."""
    
    def can_render(self, mime_type: str) -> bool:
        return mime_type == 'application/json'
        
    def render(self, data: Any, metadata: Dict[str, Any] = None) -> RenderResult:
        from rich.json import JSON
        if isinstance(data, (dict, list)):
            return JSON(json.dumps(data, indent=2))
        elif isinstance(data, str):
            return JSON(data)
        return Text(str(data))


class LaTeXRenderer(OutputRenderer):
    """Renderer for LaTeX output (converts to Unicode approximation)."""
    
    def can_render(self, mime_type: str) -> bool:
        return mime_type in ['text/latex', 'application/x-latex']
        
    def render(self, data: Any, metadata: Dict[str, Any] = None) -> RenderResult:
        # Simple LaTeX to Unicode conversion (very basic)
        latex_map = {
            r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ',
            r'\epsilon': 'ε', r'\theta': 'θ', r'\lambda': 'λ', r'\mu': 'μ',
            r'\pi': 'π', r'\sigma': 'σ', r'\tau': 'τ', r'\phi': 'φ',
            r'\infty': '∞', r'\sum': '∑', r'\int': '∫', r'\partial': '∂',
            r'\leq': '≤', r'\geq': '≥', r'\neq': '≠', r'\approx': '≈',
            r'\times': '×', r'\div': '÷', r'\pm': '±', r'\cdot': '·',
            r'^2': '²', r'^3': '³', r'^n': 'ⁿ',
        }
        
        text = str(data)
        for latex, unicode_char in latex_map.items():
            text = text.replace(latex, unicode_char)
            
        return Panel(Text(text, style="italic cyan"), title="LaTeX", border_style="cyan")


class ErrorRenderer(OutputRenderer):
    """Renderer for error output."""
    
    def can_render(self, mime_type: str) -> bool:
        return mime_type == 'error'
        
    def render(self, data: Any, metadata: Dict[str, Any] = None) -> RenderResult:
        if isinstance(data, dict):
            ename = data.get('ename', 'Error')
            evalue = data.get('evalue', '')
            traceback = data.get('traceback', [])
            
            error_text = Text()
            error_text.append(f"{ename}: {evalue}\n", style="bold red")
            
            for line in traceback:
                # Simple ANSI color code handling
                line = line.replace('\x1b[0;31m', '').replace('\x1b[0m', '')
                error_text.append(line + '\n', style="red")
                
            return Panel(error_text, title="Error", border_style="red")
        return Text(str(data), style="red")


class DataFrameRenderer(OutputRenderer):
    """Renderer for pandas DataFrame representations."""
    
    def can_render(self, mime_type: str) -> bool:
        return mime_type == 'text/html' or (mime_type == 'text/plain' and 'dataframe' in str(type(mime_type)).lower())
        
    def render(self, data: Any, metadata: Dict[str, Any] = None) -> RenderResult:
        # For DataFrames displayed as HTML, we extract the table structure
        if isinstance(data, str) and '<table' in data:
            # Very basic HTML table extraction
            import re
            
            # Extract rows
            rows = re.findall(r'<tr>(.*?)</tr>', data, re.DOTALL)
            if rows:
                table = Table()
                
                # Process header row if exists
                if rows and '<th>' in rows[0]:
                    headers = re.findall(r'<th[^>]*>(.*?)</th>', rows[0])
                    for header in headers:
                        table.add_column(header.strip())
                    rows = rows[1:]
                    
                # Process data rows
                for row in rows[:20]:  # Limit display
                    cells = re.findall(r'<td[^>]*>(.*?)</td>', row)
                    cleaned_cells = [re.sub('<[^<]+?>', '', cell).strip() for cell in cells]
                    if cleaned_cells:
                        table.add_row(*cleaned_cells)
                        
                if len(rows) > 20:
                    table.add_row(*['...' for _ in range(len(table.columns))])
                    
                return Panel(table, title="DataFrame", border_style="green")
                
        return Text(str(data)[:1000] + '...' if len(str(data)) > 1000 else str(data))