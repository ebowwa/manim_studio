"""Shared State Module

This module provides a single shared instance of ManimStudioCore
that all interfaces can use, ensuring they work with the same data.
"""

from src.interfaces.shared_features import ManimStudioCore

# Single shared instance used by all interfaces
shared_core = ManimStudioCore()