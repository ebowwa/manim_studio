"""Registry system for managing effects."""

from typing import Dict, Type, Optional, List
from .base_effect import BaseEffect


class EffectRegistry:
    """Central registry for all available effects."""
    
    _instance = None
    _effects: Dict[str, Type[BaseEffect]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, name: str, effect_class: Type[BaseEffect]) -> None:
        """Register an effect class.
        
        Args:
            name: Name to register the effect under
            effect_class: The effect class to register
        """
        if not issubclass(effect_class, BaseEffect):
            raise TypeError(f"{effect_class} must be a subclass of BaseEffect")
        
        cls._effects[name] = effect_class
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseEffect]]:
        """Get an effect class by name.
        
        Args:
            name: Name of the effect
            
        Returns:
            The effect class or None if not found
        """
        return cls._effects.get(name)
    
    @classmethod
    def list_effects(cls) -> List[str]:
        """List all registered effect names."""
        return list(cls._effects.keys())
    
    @classmethod
    def create_effect(cls, name: str, **kwargs) -> Optional[BaseEffect]:
        """Create an effect instance by name.
        
        Args:
            name: Name of the effect
            **kwargs: Parameters to pass to the effect constructor
            
        Returns:
            An instance of the effect or None if not found
        """
        effect_class = cls.get(name)
        if effect_class:
            return effect_class(**kwargs)
        return None
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered effects."""
        cls._effects.clear()


def register_effect(name: str):
    """Decorator to register an effect class.
    
    Usage:
        @register_effect("particle_burst")
        class ParticleBurst(BaseEffect):
            ...
    """
    def decorator(effect_class: Type[BaseEffect]):
        EffectRegistry.register(name, effect_class)
        return effect_class
    return decorator