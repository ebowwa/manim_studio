"""LSP Server for Manim Studio YAML Scene Editing

Provides Language Server Protocol implementation for enhanced YAML editing
with Manim Studio specific features like validation, completion, and hover.
"""

import asyncio
import json
import logging
import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

# LSP imports
try:
    from pygls.server import LanguageServer
    from pygls.lsp.types import (
        CompletionList, CompletionItem, CompletionItemKind,
        Diagnostic, DiagnosticSeverity, Position, Range,
        Hover, MarkupContent, MarkupKind,
        TextDocumentSyncKind, WorkspaceEdit, TextEdit
    )
    from pygls.lsp.methods import (
        TEXT_DOCUMENT_DID_OPEN, TEXT_DOCUMENT_DID_CHANGE,
        TEXT_DOCUMENT_COMPLETION, TEXT_DOCUMENT_HOVER,
        TEXT_DOCUMENT_DID_SAVE, INITIALIZE
    )
    LSP_AVAILABLE = True
except ImportError:
    LSP_AVAILABLE = False
    # Create dummy classes for type hints
    class LanguageServer: pass
    class CompletionList: pass
    class CompletionItem: pass
    class Diagnostic: pass

# Import shared features
from src.interfaces.shared import (
    ManimStudioCore, 
    AnimationType, 
    ShapeType, 
    RenderQuality,
    InterfaceResult
)

# Import YAML validator
try:
    from src.core.yaml_validator import YAMLValidator
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False

logger = logging.getLogger(__name__)


class ManimStudioLSP:
    """Language Server Protocol implementation for Manim Studio."""
    
    def __init__(self):
        if not LSP_AVAILABLE:
            raise ImportError(
                "pygls package required for LSP functionality. "
                "Install with: pip install pygls"
            )
        
        self.server = LanguageServer("manim-studio-lsp", "v0.1.0")
        from src.interfaces.shared import shared_core
        self.core = shared_core
        
        # YAML validator
        if VALIDATOR_AVAILABLE:
            self.validator = YAMLValidator()
        else:
            self.validator = None
        
        # Document cache
        self.documents = {}
        
        # Setup LSP handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup LSP method handlers."""
        
        @self.server.feature(INITIALIZE)
        def initialize(params):
            """Initialize the language server."""
            logger.info("Initializing Manim Studio LSP")
            return {
                "capabilities": {
                    "textDocumentSync": {
                        "openClose": True,
                        "change": TextDocumentSyncKind.Incremental,
                        "save": {"includeText": True}
                    },
                    "completionProvider": {
                        "triggerCharacters": [":", "-", " "],
                        "resolveProvider": False
                    },
                    "hoverProvider": True,
                    "diagnosticProvider": {
                        "interFileDependencies": False,
                        "workspaceDiagnostics": False
                    }
                }
            }
        
        @self.server.feature(TEXT_DOCUMENT_DID_OPEN)
        async def did_open(params):
            """Handle document open."""
            doc = params.text_document
            self.documents[doc.uri] = doc.text
            await self.validate_document(doc.uri, doc.text)
        
        @self.server.feature(TEXT_DOCUMENT_DID_CHANGE)
        async def did_change(params):
            """Handle document changes."""
            doc = params.text_document
            if doc.uri in self.documents:
                # Apply incremental changes
                content = self.documents[doc.uri]
                for change in params.content_changes:
                    if hasattr(change, 'range') and change.range:
                        # Incremental change
                        lines = content.split('\n')
                        start_line = change.range.start.line
                        start_char = change.range.start.character
                        end_line = change.range.end.line
                        end_char = change.range.end.character
                        
                        # Replace the specified range
                        if start_line == end_line:
                            line = lines[start_line]
                            lines[start_line] = line[:start_char] + change.text + line[end_char:]
                        else:
                            # Multi-line change
                            new_lines = change.text.split('\n')
                            lines[start_line] = lines[start_line][:start_char] + new_lines[0]
                            lines = lines[:start_line + 1] + new_lines[1:] + lines[end_line + 1:]
                            if len(new_lines) > 1:
                                lines[start_line + len(new_lines) - 1] += lines[end_line][end_char:]
                        
                        content = '\n'.join(lines)
                    else:
                        # Full document change
                        content = change.text
                
                self.documents[doc.uri] = content
                await self.validate_document(doc.uri, content)
        
        @self.server.feature(TEXT_DOCUMENT_DID_SAVE)
        async def did_save(params):
            """Handle document save."""
            doc = params.text_document
            if hasattr(params, 'text') and params.text:
                self.documents[doc.uri] = params.text
                await self.validate_document(doc.uri, params.text)
        
        @self.server.feature(TEXT_DOCUMENT_COMPLETION)
        async def completion(params):
            """Provide completion suggestions."""
            doc_uri = params.text_document.uri
            position = params.position
            
            if doc_uri in self.documents:
                content = self.documents[doc_uri]
                return await self.get_completions(content, position)
            
            return CompletionList(is_incomplete=False, items=[])
        
        @self.server.feature(TEXT_DOCUMENT_HOVER)
        async def hover(params):
            """Provide hover information."""
            doc_uri = params.text_document.uri
            position = params.position
            
            if doc_uri in self.documents:
                content = self.documents[doc_uri]
                return await self.get_hover_info(content, position)
            
            return None
    
    async def validate_document(self, uri: str, content: str):
        """Validate YAML document and send diagnostics."""
        if not self.validator:
            return
        
        try:
            # Convert file URI to path
            path = Path(urlparse(uri).path)
            
            # Validate the content
            result = self.validator.validate_content(content, str(path))
            
            diagnostics = []
            
            # Convert validation errors to LSP diagnostics
            for error in result.get('errors', []):
                diagnostic = Diagnostic(
                    range=Range(
                        start=Position(line=error.get('line', 0) - 1, character=0),
                        end=Position(line=error.get('line', 0) - 1, character=100)
                    ),
                    message=error['message'],
                    severity=DiagnosticSeverity.Error,
                    source="manim-studio"
                )
                diagnostics.append(diagnostic)
            
            # Convert validation warnings to LSP diagnostics
            for warning in result.get('warnings', []):
                diagnostic = Diagnostic(
                    range=Range(
                        start=Position(line=warning.get('line', 0) - 1, character=0),
                        end=Position(line=warning.get('line', 0) - 1, character=100)
                    ),
                    message=warning['message'],
                    severity=DiagnosticSeverity.Warning,
                    source="manim-studio"
                )
                diagnostics.append(diagnostic)
            
            # Send diagnostics to client
            self.server.publish_diagnostics(uri, diagnostics)
            
        except Exception as e:
            logger.error(f"Error validating document: {e}")
            # Send syntax error diagnostic
            diagnostic = Diagnostic(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=0, character=100)
                ),
                message=f"Validation error: {str(e)}",
                severity=DiagnosticSeverity.Error,
                source="manim-studio"
            )
            self.server.publish_diagnostics(uri, [diagnostic])
    
    async def get_completions(self, content: str, position: Position) -> CompletionList:
        """Generate completion suggestions based on cursor position."""
        lines = content.split('\n')
        current_line = ""
        if position.line < len(lines):
            current_line = lines[position.line][:position.character]
        
        items = []
        
        # Determine context and provide appropriate completions
        if self._is_in_scene_section(content, position):
            items.extend(self._get_scene_completions(current_line))
        elif self._is_in_objects_section(content, position):
            items.extend(self._get_object_completions(current_line))
        elif self._is_in_animations_section(content, position):
            items.extend(self._get_animation_completions(current_line))
        else:
            # Root level completions
            items.extend(self._get_root_completions(current_line))
        
        return CompletionList(is_incomplete=False, items=items)
    
    def _get_scene_completions(self, current_line: str) -> List[CompletionItem]:
        """Scene-specific completions."""
        completions = []
        
        if "name:" not in current_line:
            completions.append(CompletionItem(
                label="name",
                insert_text="name: ",
                kind=CompletionItemKind.Property,
                detail="Scene name (required)"
            ))
        
        if "duration:" not in current_line:
            completions.append(CompletionItem(
                label="duration",
                insert_text="duration: 5.0",
                kind=CompletionItemKind.Property,
                detail="Scene duration in seconds"
            ))
        
        if "background_color:" not in current_line:
            completions.append(CompletionItem(
                label="background_color",
                insert_text="background_color: \"#000000\"",
                kind=CompletionItemKind.Property,
                detail="Background color (hex)"
            ))
        
        if "resolution:" not in current_line:
            completions.append(CompletionItem(
                label="resolution",
                insert_text="resolution: \"1920x1080\"",
                kind=CompletionItemKind.Property,
                detail="Video resolution"
            ))
        
        if "fps:" not in current_line:
            completions.append(CompletionItem(
                label="fps",
                insert_text="fps: 60",
                kind=CompletionItemKind.Property,
                detail="Frames per second"
            ))
        
        return completions
    
    def _get_object_completions(self, current_line: str) -> List[CompletionItem]:
        """Object-specific completions."""
        completions = []
        
        # Object types
        if "type:" in current_line or current_line.strip().endswith("type:"):
            for shape in ShapeType:
                completions.append(CompletionItem(
                    label=shape.value,
                    insert_text=f'"{shape.value}"',
                    kind=CompletionItemKind.Value,
                    detail=f"Shape type: {shape.value}"
                ))
            
            # Text object
            completions.append(CompletionItem(
                label="text",
                insert_text='"text"',
                kind=CompletionItemKind.Value,
                detail="Text object"
            ))
        
        # Common object properties
        else:
            completions.extend([
                CompletionItem(
                    label="id",
                    insert_text="id: ",
                    kind=CompletionItemKind.Property,
                    detail="Unique object identifier"
                ),
                CompletionItem(
                    label="type",
                    insert_text="type: ",
                    kind=CompletionItemKind.Property,
                    detail="Object type"
                ),
                CompletionItem(
                    label="position",
                    insert_text="position: [0, 0, 0]",
                    kind=CompletionItemKind.Property,
                    detail="Object position [x, y, z]"
                ),
                CompletionItem(
                    label="color",
                    insert_text="color: \"#FFFFFF\"",
                    kind=CompletionItemKind.Property,
                    detail="Object color (hex)"
                ),
                CompletionItem(
                    label="size",
                    insert_text="size: 1.0",
                    kind=CompletionItemKind.Property,
                    detail="Object size/scale"
                )
            ])
        
        return completions
    
    def _get_animation_completions(self, current_line: str) -> List[CompletionItem]:
        """Animation-specific completions."""
        completions = []
        
        # Animation types
        if "type:" in current_line or current_line.strip().endswith("type:"):
            for anim in AnimationType:
                completions.append(CompletionItem(
                    label=anim.value,
                    insert_text=f'"{anim.value}"',
                    kind=CompletionItemKind.Value,
                    detail=f"Animation type: {anim.value}"
                ))
        
        # Easing functions
        elif "easing:" in current_line or current_line.strip().endswith("easing:"):
            easing_types = [
                "linear", "ease_in", "ease_out", "ease_in_out",
                "bounce", "elastic", "back", "expo"
            ]
            for easing in easing_types:
                completions.append(CompletionItem(
                    label=easing,
                    insert_text=f'"{easing}"',
                    kind=CompletionItemKind.Value,
                    detail=f"Easing function: {easing}"
                ))
        
        # Common animation properties
        else:
            completions.extend([
                CompletionItem(
                    label="target",
                    insert_text="target: ",
                    kind=CompletionItemKind.Property,
                    detail="Target object ID"
                ),
                CompletionItem(
                    label="type",
                    insert_text="type: ",
                    kind=CompletionItemKind.Property,
                    detail="Animation type"
                ),
                CompletionItem(
                    label="start_time",
                    insert_text="start_time: 0.0",
                    kind=CompletionItemKind.Property,
                    detail="Animation start time (seconds)"
                ),
                CompletionItem(
                    label="duration",
                    insert_text="duration: 1.0",
                    kind=CompletionItemKind.Property,
                    detail="Animation duration (seconds)"
                ),
                CompletionItem(
                    label="easing",
                    insert_text="easing: ",
                    kind=CompletionItemKind.Property,
                    detail="Easing function"
                )
            ])
        
        return completions
    
    def _get_root_completions(self, current_line: str) -> List[CompletionItem]:
        """Root-level completions."""
        return [
            CompletionItem(
                label="scene",
                insert_text="scene:\n  name: \n  duration: 5.0",
                kind=CompletionItemKind.Class,
                detail="Scene configuration"
            ),
            CompletionItem(
                label="objects",
                insert_text="objects:\n  - id: \n    type: ",
                kind=CompletionItemKind.Class,
                detail="Scene objects"
            ),
            CompletionItem(
                label="animations",
                insert_text="animations:\n  - target: \n    type: ",
                kind=CompletionItemKind.Class,
                detail="Scene animations"
            )
        ]
    
    def _is_in_scene_section(self, content: str, position: Position) -> bool:
        """Check if cursor is in scene section."""
        lines = content.split('\n')
        for i in range(position.line, -1, -1):
            if i < len(lines):
                line = lines[i].strip()
                if line.startswith('scene:'):
                    return True
                elif line and not line.startswith(' ') and not line.startswith('\t'):
                    return False
        return False
    
    def _is_in_objects_section(self, content: str, position: Position) -> bool:
        """Check if cursor is in objects section."""
        lines = content.split('\n')
        for i in range(position.line, -1, -1):
            if i < len(lines):
                line = lines[i].strip()
                if line.startswith('objects:'):
                    return True
                elif line and not line.startswith(' ') and not line.startswith('\t') and not line.startswith('-'):
                    return False
        return False
    
    def _is_in_animations_section(self, content: str, position: Position) -> bool:
        """Check if cursor is in animations section."""
        lines = content.split('\n')
        for i in range(position.line, -1, -1):
            if i < len(lines):
                line = lines[i].strip()
                if line.startswith('animations:'):
                    return True
                elif line and not line.startswith(' ') and not line.startswith('\t') and not line.startswith('-'):
                    return False
        return False
    
    async def get_hover_info(self, content: str, position: Position) -> Optional[Hover]:
        """Provide hover information for current cursor position."""
        lines = content.split('\n')
        if position.line >= len(lines):
            return None
        
        current_line = lines[position.line]
        word_at_cursor = self._get_word_at_position(current_line, position.character)
        
        if not word_at_cursor:
            return None
        
        # Provide documentation for known properties
        hover_docs = {
            "name": "**Scene Name**\n\nUnique identifier for the scene. Used in output filenames and references.",
            "duration": "**Scene Duration**\n\nTotal duration of the scene in seconds. Determines how long the animation runs.",
            "background_color": "**Background Color**\n\nScene background color in hex format (e.g., #000000 for black).",
            "resolution": "**Resolution**\n\nVideo resolution in format 'WIDTHxHEIGHT' (e.g., '1920x1080').",
            "fps": "**Frames Per Second**\n\nVideo frame rate. Higher values create smoother animation but larger files.",
            "type": "**Object/Animation Type**\n\nSpecifies the type of object or animation. See available options in completion.",
            "position": "**Position**\n\nObject position in 3D space as [x, y, z] coordinates.",
            "color": "**Color**\n\nObject color in hex format (e.g., #FF0000 for red).",
            "size": "**Size**\n\nObject scale factor. 1.0 is default size, 2.0 is double size.",
            "target": "**Animation Target**\n\nID of the object to animate. Must match an existing object ID.",
            "start_time": "**Start Time**\n\nWhen the animation begins in seconds from scene start.",
            "easing": "**Easing Function**\n\nControls animation timing curve for smooth motion."
        }
        
        if word_at_cursor in hover_docs:
            return Hover(
                contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=hover_docs[word_at_cursor]
                )
            )
        
        # Check for shape types
        if word_at_cursor in [shape.value for shape in ShapeType]:
            return Hover(
                contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"**Shape Type: {word_at_cursor}**\n\nCreates a {word_at_cursor} shape object."
                )
            )
        
        # Check for animation types
        if word_at_cursor in [anim.value for anim in AnimationType]:
            return Hover(
                contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"**Animation Type: {word_at_cursor}**\n\nApplies {word_at_cursor} animation to target object."
                )
            )
        
        return None
    
    def _get_word_at_position(self, line: str, character: int) -> str:
        """Extract word at specific character position."""
        if character >= len(line):
            return ""
        
        # Find word boundaries
        start = character
        end = character
        
        # Move backwards to find start
        while start > 0 and line[start - 1].isalnum() or line[start - 1] == '_':
            start -= 1
        
        # Move forwards to find end
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        
        return line[start:end]
    
    async def start_server(self, host: str = "localhost", port: int = 8088):
        """Start the LSP server."""
        if not LSP_AVAILABLE:
            raise ImportError("pygls package required for LSP server")
        
        logger.info(f"Starting Manim Studio LSP server on {host}:{port}")
        await self.server.start_tcp(host, port)
    
    def start_stdio(self):
        """Start the LSP server using stdio."""
        if not LSP_AVAILABLE:
            raise ImportError("pygls package required for LSP server")
        
        logger.info("Starting Manim Studio LSP server with stdio")
        self.server.start_io()


async def main():
    """Main entry point for LSP server."""
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr  # Use stderr to avoid interfering with LSP communication
    )
    
    lsp = ManimStudioLSP()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--tcp":
        # TCP mode
        host = sys.argv[2] if len(sys.argv) > 2 else "localhost"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8088
        await lsp.start_server(host, port)
    else:
        # Stdio mode (default for most LSP clients)
        lsp.start_stdio()


if __name__ == "__main__":
    if LSP_AVAILABLE:
        asyncio.run(main())
    else:
        print("Error: pygls package required for LSP functionality.")
        print("Install with: pip install pygls")
        exit(1)