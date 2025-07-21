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
    
    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.type:
            raise ValueError("Effect type cannot be empty")
        if self.start_time < 0:
            raise ValueError("Start time cannot be negative")
        if self.duration is not None and self.duration <= 0:
            raise ValueError("Duration must be positive if specified")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EffectConfig':
        """Create EffectConfig from dictionary with proper defaults."""
        return cls(
            type=data.get('type', ''),
            params=data.get('params', {}),
            start_time=data.get('start_time', 0.0),
            duration=data.get('duration')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert EffectConfig to dictionary."""
        result = {
            'type': self.type,
            'params': self.params,
            'start_time': self.start_time
        }
        if self.duration is not None:
            result['duration'] = self.duration
        return result
    
    def copy(self) -> 'EffectConfig':
        """Create a deep copy of the effect configuration."""
        return EffectConfig(
            type=self.type,
            params=self.params.copy(),
            start_time=self.start_time,
            duration=self.duration
        )


@dataclass
class AnimationConfig:
    """Configuration for an animation sequence."""
    target: str  # Target object or group
    animation_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    start_time: float = 0.0
    duration: float = 1.0
    
    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.target:
            raise ValueError("Animation target cannot be empty")
        if not self.animation_type:
            raise ValueError("Animation type cannot be empty")
        if self.start_time < 0:
            raise ValueError("Start time cannot be negative")
        if self.duration <= 0:
            raise ValueError("Duration must be positive")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnimationConfig':
        """Create AnimationConfig from dictionary with proper defaults."""
        return cls(
            target=data.get('target', ''),
            animation_type=data.get('animation_type', ''),
            params=data.get('params', {}),
            start_time=data.get('start_time', 0.0),
            duration=data.get('duration', 1.0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert AnimationConfig to dictionary."""
        return {
            'target': self.target,
            'animation_type': self.animation_type,
            'params': self.params,
            'start_time': self.start_time,
            'duration': self.duration
        }
    
    def copy(self) -> 'AnimationConfig':
        """Create a deep copy of the animation configuration."""
        return AnimationConfig(
            target=self.target,
            animation_type=self.animation_type,
            params=self.params.copy(),
            start_time=self.start_time,
            duration=self.duration
        )
    
    def overlaps_with(self, other: 'AnimationConfig') -> bool:
        """Check if this animation overlaps with another animation."""
        if self.target != other.target:
            return False
        
        self_end = self.start_time + self.duration
        other_end = other.start_time + other.duration
        
        return not (self_end <= other.start_time or self.start_time >= other_end)


@dataclass
class CameraConfig:
    """Configuration for camera settings and animations."""
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 5.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    zoom: float = 1.0
    fov: float = 60.0  # Field of view in degrees
    near_clip: float = 0.1
    far_clip: float = 100.0
    
    def __post_init__(self):
        """Validate camera parameters."""
        if len(self.position) != 3:
            raise ValueError("Camera position must have 3 coordinates (x, y, z)")
        if len(self.rotation) != 3:
            raise ValueError("Camera rotation must have 3 angles (x, y, z)")
        if self.zoom <= 0:
            raise ValueError("Camera zoom must be positive")
        if not 0 < self.fov < 180:
            raise ValueError("Field of view must be between 0 and 180 degrees")
        if self.near_clip <= 0:
            raise ValueError("Near clip plane must be positive")
        if self.far_clip <= self.near_clip:
            raise ValueError("Far clip plane must be greater than near clip plane")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CameraConfig':
        """Create CameraConfig from dictionary with proper defaults."""
        return cls(
            position=data.get('position', [0.0, 0.0, 5.0]),
            rotation=data.get('rotation', [0.0, 0.0, 0.0]),
            zoom=data.get('zoom', 1.0),
            fov=data.get('fov', 60.0),
            near_clip=data.get('near_clip', 0.1),
            far_clip=data.get('far_clip', 100.0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert CameraConfig to dictionary."""
        return {
            'position': self.position,
            'rotation': self.rotation,
            'zoom': self.zoom,
            'fov': self.fov,
            'near_clip': self.near_clip,
            'far_clip': self.far_clip
        }
    
    def copy(self) -> 'CameraConfig':
        """Create a deep copy of the camera configuration."""
        return CameraConfig(
            position=self.position.copy(),
            rotation=self.rotation.copy(),
            zoom=self.zoom,
            fov=self.fov,
            near_clip=self.near_clip,
            far_clip=self.far_clip
        )


@dataclass
class SceneConfig:
    """Configuration for a complete scene."""
    name: str
    description: str = ""
    duration: float = 10.0
    background_color: str = "#000000"
    resolution: tuple = (1920, 1080)
    fps: int = 60
    
    # Camera configuration
    camera: Optional[CameraConfig] = None
    
    # Scene elements
    objects: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    effects: List[EffectConfig] = field(default_factory=list)
    animations: List[AnimationConfig] = field(default_factory=list)
    
    # Asset references
    assets: Dict[str, str] = field(default_factory=dict)
    
    # Frame extraction configuration
    frame_extraction: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.name:
            raise ValueError("Scene name cannot be empty")
        if self.duration <= 0:
            raise ValueError("Duration must be positive")
        if self.fps <= 0:
            raise ValueError("FPS must be positive")
        if not isinstance(self.resolution, tuple) or len(self.resolution) != 2:
            raise ValueError("Resolution must be a tuple of (width, height)")
        if self.resolution[0] <= 0 or self.resolution[1] <= 0:
            raise ValueError("Resolution dimensions must be positive")
        
        # Validate color format
        if not self._is_valid_color(self.background_color):
            raise ValueError(f"Invalid background color format: {self.background_color}")
    
    def _is_valid_color(self, color: str) -> bool:
        """Check if color is in valid hex format."""
        if not color.startswith('#'):
            return False
        hex_part = color[1:]
        return len(hex_part) in [3, 6] and all(c in '0123456789ABCDEFabcdef' for c in hex_part)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SceneConfig':
        """Create SceneConfig from dictionary."""
        effects = [EffectConfig.from_dict(e) for e in data.get('effects', [])]
        animations = [AnimationConfig.from_dict(a) for a in data.get('animations', [])]
        
        # Handle camera config if present
        camera = None
        if 'camera' in data and data['camera'] is not None:
            camera = CameraConfig.from_dict(data['camera'])
        
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            duration=data.get('duration', 10.0),
            background_color=data.get('background_color', '#000000'),
            resolution=tuple(data.get('resolution', [1920, 1080])),
            fps=data.get('fps', 60),
            camera=camera,
            objects=data.get('objects', {}),
            effects=effects,
            animations=animations,
            assets=data.get('assets', {}),
            frame_extraction=data.get('frame_extraction')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SceneConfig to dictionary."""
        result = {
            'name': self.name,
            'description': self.description,
            'duration': self.duration,
            'background_color': self.background_color,
            'resolution': list(self.resolution),
            'fps': self.fps,
            'objects': self.objects,
            'effects': [e.to_dict() for e in self.effects],
            'animations': [a.to_dict() for a in self.animations],
            'assets': self.assets
        }
        
        # Include camera config if present
        if self.camera is not None:
            result['camera'] = self.camera.to_dict()
            
        # Include frame extraction config if present
        if self.frame_extraction is not None:
            result['frame_extraction'] = self.frame_extraction
        
        return result
    
    def add_effect(self, effect: EffectConfig) -> None:
        """Add an effect to the scene."""
        self.effects.append(effect)
    
    def add_animation(self, animation: AnimationConfig) -> None:
        """Add an animation to the scene."""
        self.animations.append(animation)
    
    def add_object(self, name: str, config: Dict[str, Any]) -> None:
        """Add an object to the scene."""
        if name in self.objects:
            raise ValueError(f"Object '{name}' already exists in scene")
        self.objects[name] = config
    
    def add_asset(self, name: str, path: str) -> None:
        """Add an asset reference to the scene."""
        if name in self.assets:
            raise ValueError(f"Asset '{name}' already exists in scene")
        self.assets[name] = path
    
    def get_animations_for_target(self, target: str) -> List[AnimationConfig]:
        """Get all animations for a specific target."""
        return [anim for anim in self.animations if anim.target == target]
    
    def get_effects_at_time(self, time: float) -> List[EffectConfig]:
        """Get all effects active at a specific time."""
        active_effects = []
        for effect in self.effects:
            if effect.duration is None:
                # Effect runs for entire scene duration
                if effect.start_time <= time:
                    active_effects.append(effect)
            else:
                # Effect has limited duration
                effect_end = effect.start_time + effect.duration
                if effect.start_time <= time < effect_end:
                    active_effects.append(effect)
        return active_effects
    
    def validate_timeline(self) -> List[str]:
        """Validate the timeline for conflicts and return any warnings."""
        warnings = []
        
        # Check for animation conflicts
        for i, anim1 in enumerate(self.animations):
            for anim2 in self.animations[i+1:]:
                if anim1.overlaps_with(anim2):
                    warnings.append(
                        f"Animation conflict: '{anim1.animation_type}' and "
                        f"'{anim2.animation_type}' overlap on target '{anim1.target}'"
                    )
        
        # Check if animations/effects exceed scene duration
        for anim in self.animations:
            if anim.start_time + anim.duration > self.duration:
                warnings.append(
                    f"Animation '{anim.animation_type}' on '{anim.target}' "
                    f"extends beyond scene duration"
                )
        
        for effect in self.effects:
            if effect.duration and effect.start_time + effect.duration > self.duration:
                warnings.append(
                    f"Effect '{effect.type}' extends beyond scene duration"
                )
        
        return warnings


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