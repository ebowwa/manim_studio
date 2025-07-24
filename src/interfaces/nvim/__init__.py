"""Neovim Interface for Manim Studio

This module provides Neovim integration for Manim Studio, including:
- Language Server Protocol (LSP) for YAML scene editing
- Buffer management for live preview
- Plugin configuration for Neovim integration
"""

from .lsp_server import ManimStudioLSP
from .plugin import NeovimPlugin
from .buffer_manager import BufferManager

__all__ = ['ManimStudioLSP', 'NeovimPlugin', 'BufferManager']