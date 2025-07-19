"""Configuration system for Manim Studio."""

import json
from pathlib import Path
try:
    import yaml
except ImportError:
    yaml = None
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field


@dataclass
class EffectConfig:
    """Configuration for a single effect."""
    type: str
    params: Dict[str, Any] = field(default_factory=dict)
    start_time: float = 0.0
    duration: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EffectConfig':
        return cls(**data)


@dataclass
class AnimationConfig:
    """Configuration for an animation sequence."""
    target: str  # Target object or group
    animation_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    start_time: float = 0.0
    duration: float = 1.0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnimationConfig':
        return cls(**data)


@dataclass
class SceneConfig:
    """Configuration for a complete scene."""
    name: str
    description: str = ""
    duration: float = 10.0
    background_color: str = "#000000"
    resolution: tuple = (1920, 1080)
    fps: int = 60
    
    # Scene elements
    objects: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    effects: List[EffectConfig] = field(default_factory=list)
    animations: List[AnimationConfig] = field(default_factory=list)
    
    # Asset references
    assets: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SceneConfig':
        """Create SceneConfig from dictionary."""
        effects = [EffectConfig.from_dict(e) for e in data.get('effects', [])]
        animations = [AnimationConfig.from_dict(a) for a in data.get('animations', [])]
        
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            duration=data.get('duration', 10.0),
            background_color=data.get('background_color', '#000000'),
            resolution=tuple(data.get('resolution', [1920, 1080])),
            fps=data.get('fps', 60),
            objects=data.get('objects', {}),
            effects=effects,
            animations=animations,
            assets=data.get('assets', {})
        )


class Config:
    """Main configuration manager."""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.config_path = Path(config_path) if config_path else None
        self.data: Dict[str, Any] = {}
        
        if self.config_path and self.config_path.exists():
            self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        if not self.config_path:
            raise ValueError("No config path specified")
        
        with open(self.config_path, 'r') as f:
            if self.config_path.suffix == '.json':
                self.data = json.load(f)
            elif self.config_path.suffix in ['.yml', '.yaml']:
                if yaml is None:
                    raise ImportError("PyYAML is required for YAML config files. Please install it with: pip install pyyaml")
                self.data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported config format: {self.config_path.suffix}")
    
    def save(self) -> None:
        """Save configuration to file."""
        if not self.config_path:
            raise ValueError("No config path specified")
        
        with open(self.config_path, 'w') as f:
            if self.config_path.suffix == '.json':
                json.dump(self.data, f, indent=2)
            elif self.config_path.suffix in ['.yml', '.yaml']:
                yaml.dump(self.data, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self.data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        keys = key.split('.')
        target = self.data
        
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
    
    def get_scene_config(self, scene_name: str) -> SceneConfig:
        """Get configuration for a specific scene."""
        scenes = self.get('scenes', {})
        if scene_name not in scenes:
            raise ValueError(f"Scene '{scene_name}' not found in configuration")
        
        return SceneConfig.from_dict(scenes[scene_name])
    
    def list_scenes(self) -> List[str]:
        """List all available scenes."""
        return list(self.get('scenes', {}).keys())