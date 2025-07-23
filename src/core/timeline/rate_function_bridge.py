"""
Unified Rate Function Bridge for Manim Studio

This module provides a unified interface for both Manim's native rate functions
and the custom easing system, allowing seamless integration between the two.
"""

from typing import Union, Callable, Dict, Any, Optional
from enum import Enum
import numpy as np

# Import Manim rate functions
from manim import (
    linear, smooth, double_smooth,
    there_and_back, there_and_back_with_pause,
    rush_into, rush_from, slow_into,
    not_quite_there, wiggle,
    squish_rate_func, lingering,
    exponential_decay
)

# Import our custom easing system
from .easing import EasingFunction, EasingLibrary, EasingPresets


class RateFunctionSource(Enum):
    """Identifies the source of a rate function."""
    MANIM = "manim"
    CUSTOM = "custom"
    USER_DEFINED = "user_defined"


class UnifiedRateFunction:
    """
    Bridges Manim rate functions and custom easings.
    
    This class provides a unified interface to access rate functions from:
    - Manim's built-in rate functions
    - Custom EasingFunction enum values
    - Preset easing configurations
    - User-defined callable functions
    """
    
    # Map of Manim function names to actual functions
    MANIM_FUNCTIONS: Dict[str, Callable[[float], float]] = {
        # Basic
        'linear': linear,
        'smooth': smooth,
        'double_smooth': double_smooth,
        # 'triple_smooth': triple_smooth,  # Not available in this manim version
        
        # There and back variations
        'there_and_back': there_and_back,
        'there_and_back_with_pause': there_and_back_with_pause,
        
        # Rush functions
        'rush_into': rush_into,
        'rush_from': rush_from,
        'slow_into': slow_into,
        
        # Special effects
        'not_quite_there': not_quite_there,
        'wiggle': wiggle,
        'squish_rate_func': squish_rate_func,
        'lingering': lingering,
        'exponential_decay': exponential_decay,
    }
    
    # Aliases for common alternative names
    ALIASES: Dict[str, str] = {
        'ease': 'smooth',
        'ease_in_out': 'smooth',
        'there_and_back_pause': 'there_and_back_with_pause',
        'rush_in': 'rush_into',
        'rush_out': 'rush_from',
    }
    
    @classmethod
    def get(cls, 
            rate_func: Union[str, EasingFunction, Callable[[float], float]],
            params: Optional[Dict[str, Any]] = None) -> Callable[[float], float]:
        """
        Get a rate function from any source.
        
        Args:
            rate_func: Can be:
                - A string name of a Manim function or preset
                - An EasingFunction enum value
                - A callable function
            params: Optional parameters for parametric easings
            
        Returns:
            A callable rate function that maps [0, 1] -> [0, 1]
        """
        # If it's already a callable, return it
        if callable(rate_func):
            return rate_func
        
        # If it's a string, check various sources
        if isinstance(rate_func, str):
            # Check aliases first
            rate_func_name = cls.ALIASES.get(rate_func.lower(), rate_func)
            
            # Check Manim functions
            if rate_func_name in cls.MANIM_FUNCTIONS:
                return cls.MANIM_FUNCTIONS[rate_func_name]
            
            # Check if it's an EasingFunction enum name
            try:
                easing_enum = EasingFunction[rate_func_name.upper()]
                return EasingLibrary.get_easing_function(easing_enum, params)
            except KeyError:
                pass
            
            # Try custom presets
            try:
                return EasingPresets.create_easing_from_preset(rate_func_name)
            except AttributeError:
                pass
            
            # Default to linear if not found
            print(f"Warning: Rate function '{rate_func}' not found, using linear")
            return linear
        
        # If it's an EasingFunction enum
        if isinstance(rate_func, EasingFunction):
            return EasingLibrary.get_easing_function(rate_func, params)
        
        # Default to linear
        return linear
    
    @classmethod
    def get_source(cls, rate_func: Union[str, EasingFunction, Callable]) -> RateFunctionSource:
        """Identify the source of a rate function."""
        if callable(rate_func) and not isinstance(rate_func, EasingFunction):
            # Check if it's a known Manim function
            for name, func in cls.MANIM_FUNCTIONS.items():
                if func is rate_func:
                    return RateFunctionSource.MANIM
            return RateFunctionSource.USER_DEFINED
        
        if isinstance(rate_func, str):
            rate_func_name = cls.ALIASES.get(rate_func.lower(), rate_func)
            if rate_func_name in cls.MANIM_FUNCTIONS:
                return RateFunctionSource.MANIM
            return RateFunctionSource.CUSTOM
        
        if isinstance(rate_func, EasingFunction):
            return RateFunctionSource.CUSTOM
        
        return RateFunctionSource.USER_DEFINED
    
    @classmethod
    def create_composed_rate_function(cls, 
                                    *rate_funcs: Union[str, EasingFunction, Callable],
                                    weights: Optional[list[float]] = None) -> Callable[[float], float]:
        """
        Create a composed rate function from multiple rate functions.
        
        Args:
            *rate_funcs: Rate functions to compose
            weights: Optional weights for each function (defaults to equal weights)
            
        Returns:
            A new rate function that combines the inputs
        """
        funcs = [cls.get(rf) for rf in rate_funcs]
        
        if weights is None:
            weights = [1.0 / len(funcs)] * len(funcs)
        else:
            # Normalize weights
            total = sum(weights)
            weights = [w / total for w in weights]
        
        def composed(t: float) -> float:
            return sum(w * f(t) for w, f in zip(weights, funcs))
        
        return composed
    
    @classmethod
    def create_sequential_rate_function(cls,
                                      *rate_funcs: Union[str, EasingFunction, Callable],
                                      durations: Optional[list[float]] = None) -> Callable[[float], float]:
        """
        Create a rate function that applies different functions sequentially.
        
        Args:
            *rate_funcs: Rate functions to apply in sequence
            durations: Relative duration for each function (defaults to equal)
            
        Returns:
            A new rate function that applies functions sequentially
        """
        funcs = [cls.get(rf) for rf in rate_funcs]
        
        if durations is None:
            durations = [1.0 / len(funcs)] * len(funcs)
        
        # Normalize durations to sum to 1
        total = sum(durations)
        durations = [d / total for d in durations]
        
        # Calculate cumulative durations
        cumulative = [0.0]
        for d in durations:
            cumulative.append(cumulative[-1] + d)
        
        def sequential(t: float) -> float:
            # Find which segment we're in
            for i in range(len(funcs)):
                if cumulative[i] <= t <= cumulative[i + 1]:
                    # Map t to local segment time
                    local_t = (t - cumulative[i]) / durations[i]
                    return funcs[i](local_t)
            
            # Edge case: t > 1
            return funcs[-1](1.0)
        
        return sequential


def rate_function(name: str = None, 
                 source: RateFunctionSource = None) -> Callable:
    """
    Decorator to register custom rate functions.
    
    Usage:
        @rate_function(name="my_custom_ease")
        def my_ease(t: float) -> float:
            return t * t
    """
    def decorator(func: Callable[[float], float]) -> Callable[[float], float]:
        # Register the function if name is provided
        if name:
            UnifiedRateFunction.MANIM_FUNCTIONS[name] = func
        return func
    
    return decorator


# Convenience functions for common operations
def get_rate_function(rate_func: Union[str, EasingFunction, Callable],
                     params: Optional[Dict[str, Any]] = None) -> Callable[[float], float]:
    """Convenience function to get a rate function."""
    return UnifiedRateFunction.get(rate_func, params)


def compose_rate_functions(*rate_funcs, weights=None) -> Callable[[float], float]:
    """Convenience function to compose rate functions."""
    return UnifiedRateFunction.create_composed_rate_function(*rate_funcs, weights=weights)


def chain_rate_functions(*rate_funcs, durations=None) -> Callable[[float], float]:
    """Convenience function to chain rate functions sequentially."""
    return UnifiedRateFunction.create_sequential_rate_function(*rate_funcs, durations=durations)