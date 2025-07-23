"""Configuration system v2 for Manim Studio using Pydantic.

This module provides a Pydantic-based configuration system that offers:
- Full type safety and validation
- Better error messages
- Automatic serialization/deserialization
- Backward compatibility with existing configs
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml

from pydantic import BaseModel, Field, field_validator, model_validator
from .types import (
    SceneConfig, AnimationType, ShapeType, EffectType,
    TextObject, ShapeObject, Animation, Effect,
    Camera2DConfig, Camera3DConfig, CameraType,
    RenderConfig, RenderQuality, ValidationResult,
    Vector3D, Color
)
from .yaml_validator import YamlValidator


class ManimStudioConfig(BaseModel):
    """Complete Manim Studio configuration."""
    scene: SceneConfig
    render: Optional[RenderConfig] = Field(default_factory=RenderConfig)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "ManimStudioConfig":
        """Load configuration from YAML file with validation."""
        path = Path(path)
        
        # First validate YAML syntax
        validator = YamlValidator()
        is_valid, errors, warnings = validator.validate_file(str(path))
        
        if not is_valid:
            error_msg = "YAML validation failed:\n"
            for err in errors:
                error_msg += f"  - {err.message}"
                if err.line:
                    error_msg += f" (line {err.line})"
                error_msg += "\n"
            raise ValueError(error_msg)
        
        # Load and parse YAML
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Convert to Pydantic model
        return cls.from_dict(data)
    
    @classmethod
    def from_json(cls, path: Union[str, Path]) -> "ManimStudioConfig":
        """Load configuration from JSON file."""
        path = Path(path)
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ManimStudioConfig":
        """Create configuration from dictionary with migration support."""
        # Handle legacy format
        if 'scene' not in data and 'name' in data:
            # Old format - wrap in scene
            data = {'scene': data}
        
        # Migrate old field names
        scene_data = data.get('scene', {})
        
        # Convert objects
        if 'objects' in scene_data:
            migrated_objects = []
            for obj in scene_data['objects']:
                migrated_obj = cls._migrate_object(obj)
                migrated_objects.append(migrated_obj)
            scene_data['objects'] = migrated_objects
        
        # Convert animations
        if 'animations' in scene_data:
            migrated_anims = []
            for anim in scene_data['animations']:
                migrated_anim = cls._migrate_animation(anim)
                migrated_anims.append(migrated_anim)
            scene_data['animations'] = migrated_anims
        
        # Convert camera
        if 'camera' in scene_data:
            scene_data['camera'] = cls._migrate_camera(
                scene_data.get('camera', {}),
                scene_data.get('camera_type', '2d')
            )
        
        data['scene'] = scene_data
        
        # Create render config if not present
        if 'render' not in data:
            data['render'] = {}
        
        return cls(**data)
    
    @staticmethod
    def _migrate_object(obj: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate old object format to new format."""
        # Ensure position is Vector3D format
        if 'position' in obj:
            pos = obj['position']
            if isinstance(pos, list):
                if len(pos) == 2:
                    pos.append(0)  # Add z=0
                obj['position'] = {'x': pos[0], 'y': pos[1], 'z': pos[2]}
        
        # Ensure color is Color format
        if 'color' in obj:
            if isinstance(obj['color'], str):
                obj['color'] = {'value': obj['color']}
        
        # Handle fill_color, stroke_color
        for color_field in ['fill_color', 'stroke_color']:
            if color_field in obj and isinstance(obj[color_field], str):
                obj[color_field] = {'value': obj[color_field]}
        
        # Ensure scale is proper format
        if 'scale' in obj:
            scale = obj['scale']
            if isinstance(scale, list) and len(scale) == 3:
                obj['scale'] = {'x': scale[0], 'y': scale[1], 'z': scale[2]}
        
        return obj
    
    @staticmethod
    def _migrate_animation(anim: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate old animation format to new format."""
        # Handle 'type' vs 'animation_type'
        if 'animation_type' in anim and 'type' not in anim:
            anim['type'] = anim.pop('animation_type')
        
        # Ensure vector fields are proper format
        vector_fields = ['end_position', 'path']
        for field in vector_fields:
            if field in anim:
                value = anim[field]
                if field == 'end_position' and isinstance(value, list):
                    if len(value) == 2:
                        value.append(0)
                    anim[field] = {'x': value[0], 'y': value[1], 'z': value[2]}
                elif field == 'path' and isinstance(value, list):
                    # Path is list of vectors
                    migrated_path = []
                    for point in value:
                        if isinstance(point, list):
                            if len(point) == 2:
                                point.append(0)
                            migrated_path.append({
                                'x': point[0], 
                                'y': point[1], 
                                'z': point[2]
                            })
                    anim[field] = migrated_path
        
        return anim
    
    @staticmethod
    def _migrate_camera(camera: Dict[str, Any], camera_type: str) -> Dict[str, Any]:
        """Migrate old camera format to new format."""
        if camera_type == '3d':
            # Ensure 3D vectors
            for field in ['position', 'look_at', 'up_vector']:
                if field in camera and isinstance(camera[field], list):
                    if len(camera[field]) == 3:
                        camera[field] = {
                            'x': camera[field][0],
                            'y': camera[field][1],
                            'z': camera[field][2]
                        }
        else:
            # 2D camera
            if 'position' in camera and isinstance(camera['position'], list):
                camera['position'] = {
                    'x': camera['position'][0],
                    'y': camera['position'][1]
                }
        
        # Ensure background_color is Color format
        if 'background_color' in camera and isinstance(camera['background_color'], str):
            camera['background_color'] = {'value': camera['background_color']}
        
        return camera
    
    def to_yaml(self, path: Union[str, Path]) -> None:
        """Save configuration to YAML file."""
        path = Path(path)
        with open(path, 'w') as f:
            yaml.dump(self.model_dump(exclude_none=True), f, sort_keys=False)
    
    def to_json(self, path: Union[str, Path]) -> None:
        """Save configuration to JSON file."""
        path = Path(path)
        with open(path, 'w') as f:
            json.dump(self.model_dump(exclude_none=True), f, indent=2)
    
    def validate_semantics(self) -> ValidationResult:
        """Perform semantic validation beyond Pydantic's structural validation."""
        result = ValidationResult(valid=True)
        
        # Check all animation targets exist
        object_ids = {obj.id for obj in self.scene.objects}
        for anim in self.scene.animations:
            if anim.target not in object_ids:
                result.add_error(
                    f"animations.{anim.target}",
                    f"Animation target '{anim.target}' not found in objects"
                )
        
        # Check all effect targets exist (if specified)
        for effect in self.scene.effects:
            if effect.target and effect.target not in object_ids:
                result.add_error(
                    f"effects.{effect.target}",
                    f"Effect target '{effect.target}' not found in objects"
                )
        
        # Check timeline consistency
        total_duration = self.scene.duration
        for anim in self.scene.animations:
            if anim.start_time + anim.duration > total_duration:
                result.add_warning(
                    f"animations.{anim.target}",
                    f"Animation extends beyond scene duration"
                )
        
        # Check for duplicate object IDs
        seen_ids = set()
        for obj in self.scene.objects:
            if obj.id in seen_ids:
                result.add_error(
                    "objects",
                    f"Duplicate object ID: '{obj.id}'"
                )
            seen_ids.add(obj.id)
        
        return result
    
    def get_object_by_id(self, object_id: str) -> Optional[Union[TextObject, ShapeObject]]:
        """Get object by ID."""
        for obj in self.scene.objects:
            if obj.id == object_id:
                return obj
        return None
    
    def get_animations_for_object(self, object_id: str) -> List[Animation]:
        """Get all animations for a specific object."""
        return [anim for anim in self.scene.animations if anim.target == object_id]
    
    def get_timeline_events(self) -> List[Dict[str, Any]]:
        """Get all events sorted by time."""
        events = []
        
        # Add animation events
        for anim in self.scene.animations:
            events.append({
                'time': anim.start_time,
                'type': 'animation_start',
                'animation': anim
            })
            events.append({
                'time': anim.start_time + anim.duration,
                'type': 'animation_end',
                'animation': anim
            })
        
        # Add effect events
        for effect in self.scene.effects:
            events.append({
                'time': effect.start_time,
                'type': 'effect_start',
                'effect': effect
            })
            if effect.duration:
                events.append({
                    'time': effect.start_time + effect.duration,
                    'type': 'effect_end',
                    'effect': effect
                })
        
        # Sort by time
        events.sort(key=lambda e: e['time'])
        return events


# Backward compatibility wrapper
def load_config(path: Union[str, Path]) -> ManimStudioConfig:
    """Load configuration from file (YAML or JSON)."""
    path = Path(path)
    if path.suffix in ['.yaml', '.yml']:
        return ManimStudioConfig.from_yaml(path)
    elif path.suffix == '.json':
        return ManimStudioConfig.from_json(path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")


# Example usage and migration guide
if __name__ == "__main__":
    # Example: Create a simple scene programmatically
    from .types import Vector3D, Color
    
    config = ManimStudioConfig(
        scene=SceneConfig(
            name="Example Scene",
            duration=5.0,
            objects=[
                TextObject(
                    id="title",
                    content="Hello Manim!",
                    position=Vector3D(x=0, y=2, z=0),
                    color=Color(value="#FFFFFF"),
                    font_size=72
                ),
                ShapeObject(
                    id="circle",
                    type=ShapeType.CIRCLE,
                    position=Vector3D(x=0, y=-1, z=0),
                    color=Color(value="#FF0000"),
                    radius=1.5
                )
            ],
            animations=[
                Animation(
                    type=AnimationType.FADE_IN,
                    target="title",
                    duration=1.0,
                    start_time=0.0
                ),
                Animation(
                    type=AnimationType.CREATE,
                    target="circle",
                    duration=1.5,
                    start_time=1.0
                )
            ]
        )
    )
    
    # Validate semantics
    validation = config.validate_semantics()
    if not validation.valid:
        print("Validation errors:")
        for error in validation.errors:
            print(f"  - {error.field}: {error.message}")
    
    # Save to file
    config.to_yaml("example_scene.yaml")