"""
Text Policy Enforcement
Ensures all text creation goes through TextManager
"""

import functools
import warnings
from typing import Any, Callable
from manim import Text, MathTex, Tex, MarkupText


class TextPolicyViolation(UserWarning):
    """Warning for direct text creation bypassing TextManager"""
    pass


def warn_direct_text_usage(func_name: str, message: str = None):
    """Issue warning when direct text functions are used"""
    default_message = (
        f"Direct use of {func_name} is deprecated. "
        "Please use TextManager for consistent text handling. "
        "See src/core/TEXT_MIGRATION_GUIDE.md for migration instructions."
    )
    
    warnings.warn(
        message or default_message,
        TextPolicyViolation,
        stacklevel=3
    )


# Monkey patch text classes to issue warnings
_original_text_init = Text.__init__
_original_mathtex_init = MathTex.__init__  
_original_tex_init = Tex.__init__
_original_markuptext_init = MarkupText.__init__


def _warned_text_init(self, *args, **kwargs):
    warn_direct_text_usage("Text()")
    return _original_text_init(self, *args, **kwargs)


def _warned_mathtex_init(self, *args, **kwargs):
    warn_direct_text_usage("MathTex()")
    return _original_mathtex_init(self, *args, **kwargs)


def _warned_tex_init(self, *args, **kwargs):
    warn_direct_text_usage("Tex()")
    return _original_tex_init(self, *args, **kwargs)


def _warned_markuptext_init(self, *args, **kwargs):
    warn_direct_text_usage("MarkupText()")
    return _original_markuptext_init(self, *args, **kwargs)


def enforce_text_policy(enabled: bool = True):
    """
    Enable or disable text policy enforcement
    
    Args:
        enabled: If True, direct text creation will issue warnings
    """
    if enabled:
        # Patch text classes to warn about direct usage
        Text.__init__ = _warned_text_init
        MathTex.__init__ = _warned_mathtex_init
        Tex.__init__ = _warned_tex_init
        MarkupText.__init__ = _warned_markuptext_init
    else:
        # Restore original behavior
        Text.__init__ = _original_text_init
        MathTex.__init__ = _original_mathtex_init
        Tex.__init__ = _original_tex_init
        MarkupText.__init__ = _original_markuptext_init


def text_manager_only(func: Callable) -> Callable:
    """
    Decorator to ensure a function only uses TextManager for text
    
    Usage:
        @text_manager_only
        def my_scene_method(self):
            # Will warn if direct Text() is used
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Temporarily enable policy during function execution
        original_state = getattr(Text.__init__, '__name__', None) == '_warned_text_init'
        
        if not original_state:
            enforce_text_policy(True)
        
        try:
            return func(*args, **kwargs)
        finally:
            if not original_state:
                enforce_text_policy(False)
    
    return wrapper


# Enable policy by default in development
import os
if os.getenv('MANIM_STUDIO_DEV', '').lower() in ('true', '1', 'yes'):
    enforce_text_policy(True)


# Provide access to TextManager for quick imports
def get_text_manager(scene):
    """Quick helper to get TextManager for a scene"""
    from .text_manager import TextManager
    return TextManager(scene)


__all__ = [
    'TextPolicyViolation',
    'enforce_text_policy', 
    'text_manager_only',
    'get_text_manager'
]