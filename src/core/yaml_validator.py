"""
YAML configuration validation utilities for Manim Studio.

Provides comprehensive validation for YAML scene configuration files,
including syntax checking, schema validation, and semantic validation.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationResult:
    """Result of YAML validation."""
    severity: ValidationSeverity
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    path: Optional[str] = None

class YamlValidator:
    """Comprehensive YAML validator for Manim Studio scene files."""
    
    # Required top-level keys
    REQUIRED_KEYS = {'scene'}
    
    # Valid scene configuration keys
    SCENE_KEYS = {
        'name', 'duration', 'fps', 'resolution', 'background_color',
        'camera', 'objects', 'animations', 'effects', 'timeline'
    }
    
    # Valid camera types
    CAMERA_TYPES = {'2d', '3d'}
    
    # Valid animation types
    ANIMATION_TYPES = {
        'create', 'destroy', 'fade_in', 'fade_out', 'move', 'rotate',
        'scale', 'transform', 'morph', 'write', 'draw_border_then_fill'
    }
    
    # Valid effect types  
    EFFECT_TYPES = {
        'particle', 'glow', 'trail', 'ripple', 'explosion', 'magic_circle',
        'energy_beam', 'lightning', 'fire', 'smoke'
    }
    
    # Valid object types
    OBJECT_TYPES = {
        'circle', 'square', 'rectangle', 'triangle', 'polygon',
        'text', 'number', 'equation', 'arrow', 'line', 'dot',
        'vector', 'axes', 'graph', 'image', 'group', 'visual_array'
    }
    
    def __init__(self):
        self.results: List[ValidationResult] = []
    
    def validate_file(self, file_path: str) -> Tuple[bool, List[ValidationResult]]:
        """
        Validate a YAML file completely.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Tuple of (is_valid, validation_results)
        """
        self.results = []
        path = Path(file_path)
        
        if not path.exists():
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"File does not exist: {file_path}"
            ))
            return False, self.results
        
        # Check file extension
        if path.suffix not in ['.yaml', '.yml']:
            self.results.append(ValidationResult(
                ValidationSeverity.WARNING,
                f"File does not have .yaml or .yml extension: {path.suffix}"
            ))
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"Cannot read file: {e}"
            ))
            return False, self.results
        
        # Validate YAML syntax
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            line = getattr(e, 'problem_mark', None)
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"YAML syntax error: {e}",
                line=line.line + 1 if line else None,
                column=line.column + 1 if line else None
            ))
            return False, self.results
        
        if data is None:
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                "YAML file is empty or contains only whitespace"
            ))
            return False, self.results
        
        # Validate structure and content
        self._validate_structure(data)
        
        # Check for errors
        has_errors = any(r.severity == ValidationSeverity.ERROR for r in self.results)
        return not has_errors, self.results
    
    def _validate_structure(self, data: Any) -> None:
        """Validate the overall structure of the YAML data."""
        if not isinstance(data, dict):
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"Root element must be a dictionary, got {type(data).__name__}"
            ))
            return
        
        # Check required keys
        missing_keys = self.REQUIRED_KEYS - set(data.keys())
        if missing_keys:
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"Missing required keys: {', '.join(missing_keys)}"
            ))
        
        # Validate scene configuration
        if 'scene' in data:
            self._validate_scene(data['scene'])
        
        # Check for unexpected top-level keys
        unexpected_keys = set(data.keys()) - {'scene', 'metadata', 'version'}
        if unexpected_keys:
            self.results.append(ValidationResult(
                ValidationSeverity.WARNING,
                f"Unexpected top-level keys: {', '.join(unexpected_keys)}"
            ))
    
    def _validate_scene(self, scene: Any) -> None:
        """Validate scene configuration."""
        if not isinstance(scene, dict):
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"Scene must be a dictionary, got {type(scene).__name__}",
                path="scene"
            ))
            return
        
        # Check scene name
        if 'name' not in scene:
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                "Scene name is required",
                path="scene.name"
            ))
        elif not isinstance(scene['name'], str) or not scene['name'].strip():
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                "Scene name must be a non-empty string",
                path="scene.name"
            ))
        
        # Validate numeric fields
        self._validate_numeric_field(scene, 'duration', 'scene.duration', required=True, min_value=0.1)
        self._validate_numeric_field(scene, 'fps', 'scene.fps', required=False, min_value=1, max_value=120)
        
        # Validate resolution
        if 'resolution' in scene:
            self._validate_resolution(scene['resolution'])
        
        # Validate background color
        if 'background_color' in scene:
            self._validate_color(scene['background_color'], 'scene.background_color')
        
        # Validate camera
        if 'camera' in scene:
            self._validate_camera(scene['camera'])
        
        # Validate objects
        if 'objects' in scene:
            self._validate_objects(scene['objects'])
        
        # Validate animations
        if 'animations' in scene:
            self._validate_animations(scene['animations'])
        
        # Validate effects
        if 'effects' in scene:
            self._validate_effects(scene['effects'])
        
        # Check for unexpected scene keys
        unexpected_keys = set(scene.keys()) - self.SCENE_KEYS
        if unexpected_keys:
            self.results.append(ValidationResult(
                ValidationSeverity.WARNING,
                f"Unexpected scene keys: {', '.join(unexpected_keys)}",
                path="scene"
            ))
    
    def _validate_numeric_field(self, data: dict, field: str, path: str, 
                               required: bool = False, min_value: float = None, 
                               max_value: float = None) -> None:
        """Validate a numeric field."""
        if field not in data:
            if required:
                self.results.append(ValidationResult(
                    ValidationSeverity.ERROR,
                    f"Required field '{field}' is missing",
                    path=path
                ))
            return
        
        value = data[field]
        if not isinstance(value, (int, float)):
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"Field '{field}' must be a number, got {type(value).__name__}",
                path=path
            ))
            return
        
        if min_value is not None and value < min_value:
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"Field '{field}' must be >= {min_value}, got {value}",
                path=path
            ))
        
        if max_value is not None and value > max_value:
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"Field '{field}' must be <= {max_value}, got {value}",
                path=path
            ))
    
    def _validate_resolution(self, resolution: Any) -> None:
        """Validate resolution configuration."""
        path = "scene.resolution"
        if isinstance(resolution, str):
            valid_presets = {'480p', '720p', '1080p', '1440p', '2160p', '4k'}
            if resolution.lower() not in valid_presets:
                self.results.append(ValidationResult(
                    ValidationSeverity.ERROR,
                    f"Invalid resolution preset: {resolution}. Valid presets: {', '.join(valid_presets)}",
                    path=path
                ))
        elif isinstance(resolution, list) and len(resolution) == 2:
            if not all(isinstance(x, int) and x > 0 for x in resolution):
                self.results.append(ValidationResult(
                    ValidationSeverity.ERROR,
                    "Resolution array must contain two positive integers",
                    path=path
                ))
        else:
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                "Resolution must be a string preset or [width, height] array",
                path=path
            ))
    
    def _validate_color(self, color: Any, path: str) -> None:
        """Validate color specification."""
        if isinstance(color, str):
            # Check hex colors
            if color.startswith('#'):
                if len(color) not in [4, 7]:  # #RGB or #RRGGBB
                    self.results.append(ValidationResult(
                        ValidationSeverity.ERROR,
                        f"Invalid hex color format: {color}",
                        path=path
                    ))
            # Named colors are hard to validate without importing manim
        elif isinstance(color, list):
            if len(color) not in [3, 4]:  # RGB or RGBA
                self.results.append(ValidationResult(
                    ValidationSeverity.ERROR,
                    "Color array must have 3 (RGB) or 4 (RGBA) values",
                    path=path
                ))
            elif not all(isinstance(x, (int, float)) and 0 <= x <= 1 for x in color):
                self.results.append(ValidationResult(
                    ValidationSeverity.ERROR,
                    "Color values must be numbers between 0 and 1",
                    path=path
                ))
        else:
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                "Color must be a string or RGB/RGBA array",
                path=path
            ))
    
    def _validate_camera(self, camera: Any) -> None:
        """Validate camera configuration."""
        path = "scene.camera"
        if not isinstance(camera, dict):
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"Camera must be a dictionary, got {type(camera).__name__}",
                path=path
            ))
            return
        
        # Validate camera type
        if 'type' in camera:
            if camera['type'] not in self.CAMERA_TYPES:
                self.results.append(ValidationResult(
                    ValidationSeverity.ERROR,
                    f"Invalid camera type: {camera['type']}. Valid types: {', '.join(self.CAMERA_TYPES)}",
                    path=f"{path}.type"
                ))
        
        # Validate position (if present)
        if 'position' in camera:
            pos = camera['position']
            if not (isinstance(pos, list) and len(pos) == 3 and 
                   all(isinstance(x, (int, float)) for x in pos)):
                self.results.append(ValidationResult(
                    ValidationSeverity.ERROR,
                    "Camera position must be [x, y, z] array of numbers",
                    path=f"{path}.position"
                ))
        
        # Validate 3D camera specific parameters
        if 'phi' in camera:
            phi = camera['phi']
            if not isinstance(phi, (int, float)):
                self.results.append(ValidationResult(
                    ValidationSeverity.ERROR,
                    "Camera phi must be a number",
                    path=f"{path}.phi"
                ))
            elif not (0 <= phi <= 3.14159):  # 0 to π
                self.results.append(ValidationResult(
                    ValidationSeverity.ERROR,
                    f"Camera phi must be between 0 and π (3.14159), got {phi}",
                    path=f"{path}.phi"
                ))
        
        if 'theta' in camera:
            theta = camera['theta']
            if not isinstance(theta, (int, float)):
                self.results.append(ValidationResult(
                    ValidationSeverity.ERROR,
                    "Camera theta must be a number",
                    path=f"{path}.theta"
                ))
            elif not (0 <= theta <= 6.28318):  # 0 to 2π
                self.results.append(ValidationResult(
                    ValidationSeverity.ERROR,
                    f"Camera theta must be between 0 and 2π (6.28318), got {theta}",
                    path=f"{path}.theta"
                ))
        
        # Validate distance
        if 'distance' in camera:
            self._validate_numeric_field(camera, 'distance', f'{path}.distance', 
                                       required=False, min_value=0.1)
    
    def _validate_objects(self, objects: Any) -> None:
        """Validate objects configuration."""
        path = "scene.objects"
        if not isinstance(objects, list):
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"Objects must be a list, got {type(objects).__name__}",
                path=path
            ))
            return
        
        for i, obj in enumerate(objects):
            self._validate_object(obj, f"{path}[{i}]")
    
    def _validate_object(self, obj: Any, path: str) -> None:
        """Validate a single object."""
        if not isinstance(obj, dict):
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"Object must be a dictionary, got {type(obj).__name__}",
                path=path
            ))
            return
        
        # Check required fields
        if 'type' not in obj:
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                "Object type is required",
                path=f"{path}.type"
            ))
        elif obj['type'] not in self.OBJECT_TYPES:
            self.results.append(ValidationResult(
                ValidationSeverity.WARNING,
                f"Unknown object type: {obj['type']}. Known types: {', '.join(sorted(self.OBJECT_TYPES))}",
                path=f"{path}.type"
            ))
        
        if 'name' not in obj:
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                "Object name is required",
                path=f"{path}.name"
            ))
        elif not isinstance(obj['name'], str) or not obj['name'].strip():
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                "Object name must be a non-empty string",
                path=f"{path}.name"
            ))
    
    def _validate_animations(self, animations: Any) -> None:
        """Validate animations configuration."""
        path = "scene.animations"
        if not isinstance(animations, list):
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"Animations must be a list, got {type(animations).__name__}",
                path=path
            ))
            return
        
        for i, anim in enumerate(animations):
            self._validate_animation(anim, f"{path}[{i}]")
    
    def _validate_animation(self, anim: Any, path: str) -> None:
        """Validate a single animation."""
        if not isinstance(anim, dict):
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"Animation must be a dictionary, got {type(anim).__name__}",
                path=path
            ))
            return
        
        # Required fields
        required_fields = ['type', 'target']
        for field in required_fields:
            if field not in anim:
                self.results.append(ValidationResult(
                    ValidationSeverity.ERROR,
                    f"Animation field '{field}' is required",
                    path=f"{path}.{field}"
                ))
        
        # Validate animation type
        if 'type' in anim and anim['type'] not in self.ANIMATION_TYPES:
            self.results.append(ValidationResult(
                ValidationSeverity.WARNING,
                f"Unknown animation type: {anim['type']}. Known types: {', '.join(sorted(self.ANIMATION_TYPES))}",
                path=f"{path}.type"
            ))
        
        # Validate timing
        self._validate_numeric_field(anim, 'start_time', f"{path}.start_time", min_value=0)
        self._validate_numeric_field(anim, 'duration', f"{path}.duration", min_value=0.1)
    
    def _validate_effects(self, effects: Any) -> None:
        """Validate effects configuration."""
        path = "scene.effects"
        if not isinstance(effects, list):
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"Effects must be a list, got {type(effects).__name__}",
                path=path
            ))
            return
        
        for i, effect in enumerate(effects):
            self._validate_effect(effect, f"{path}[{i}]")
    
    def _validate_effect(self, effect: Any, path: str) -> None:
        """Validate a single effect."""
        if not isinstance(effect, dict):
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                f"Effect must be a dictionary, got {type(effect).__name__}",
                path=path
            ))
            return
        
        # Required fields
        if 'type' not in effect:
            self.results.append(ValidationResult(
                ValidationSeverity.ERROR,
                "Effect type is required",
                path=f"{path}.type"
            ))
        elif effect['type'] not in self.EFFECT_TYPES:
            self.results.append(ValidationResult(
                ValidationSeverity.WARNING,
                f"Unknown effect type: {effect['type']}. Known types: {', '.join(sorted(self.EFFECT_TYPES))}",
                path=f"{path}.type"
            ))
        
        # Validate timing
        self._validate_numeric_field(effect, 'start_time', f"{path}.start_time", min_value=0)
        self._validate_numeric_field(effect, 'duration', f"{path}.duration", min_value=0.1)

def validate_yaml_file(file_path: str, verbose: bool = False) -> bool:
    """
    Validate a YAML scene file and print results.
    
    Args:
        file_path: Path to YAML file to validate
        verbose: Whether to show all validation results or just errors
        
    Returns:
        True if validation passes, False otherwise
    """
    validator = YamlValidator()
    is_valid, results = validator.validate_file(file_path)
    
    if not results:
        print(f"✅ {file_path}: Valid YAML scene file")
        return True
    
    # Print results
    error_count = sum(1 for r in results if r.severity == ValidationSeverity.ERROR)
    warning_count = sum(1 for r in results if r.severity == ValidationSeverity.WARNING)
    
    status = "✅" if is_valid else "❌"
    print(f"{status} {file_path}: {error_count} errors, {warning_count} warnings")
    
    for result in results:
        if not verbose and result.severity != ValidationSeverity.ERROR:
            continue
        
        icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[result.severity.value]
        location = ""
        if result.line:
            location = f" (line {result.line}"
            if result.column:
                location += f", col {result.column}"
            location += ")"
        elif result.path:
            location = f" ({result.path})"
        
        print(f"  {icon} {result.message}{location}")
    
    return is_valid