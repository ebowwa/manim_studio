"""Base class for all effects in the Manim Studio system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, Union
from manim import *


class BaseEffect(ABC):
    """Abstract base class for all effects.
    
    This class defines the interface that all effects must implement
    and provides common functionality for effect management.
    """
    
    def __init__(self):
        self._mobjects = VGroup()
        self._animations = []
        self._config = {}
    
    @abstractmethod
    def create(self) -> VGroup:
        """Create and return the visual elements of the effect.
        
        Returns:
            VGroup: The created visual elements
        """
        pass
    
    @abstractmethod
    def animate(self, scene: Scene) -> None:
        """Execute the effect's animation on the given scene.
        
        Args:
            scene: The Manim scene to animate on
        """
        pass
    
    def update_config(self, **kwargs) -> None:
        """Update the effect's configuration.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        self._config.update(kwargs)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            The configuration value
        """
        return self._config.get(key, default)
    
    def cleanup(self) -> None:
        """Clean up any resources used by the effect."""
        self._mobjects = VGroup()
        self._animations = []
    
    @property
    def mobjects(self) -> VGroup:
        """Get all mobjects associated with this effect."""
        return self._mobjects
    
    def add_mobjects(self, *mobjects: Mobject) -> None:
        """Add mobjects to the effect.
        
        Args:
            *mobjects: Mobjects to add
        """
        for mobject in mobjects:
            self._mobjects.add(mobject)
    
    def remove_mobjects(self, *mobjects: Mobject) -> None:
        """Remove mobjects from the effect.
        
        Args:
            *mobjects: Mobjects to remove
        """
        for mobject in mobjects:
            self._mobjects.remove(mobject)
    
    def validate_config(self, required_keys: list) -> bool:
        """Validate that all required configuration keys are present.
        
        Args:
            required_keys: List of required configuration keys
            
        Returns:
            bool: True if all required keys are present
            
        Raises:
            ValueError: If any required keys are missing
        """
        missing_keys = [key for key in required_keys if key not in self._config]
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
        return True
