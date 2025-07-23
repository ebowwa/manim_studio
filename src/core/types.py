"""Type definitions and Pydantic models for Manim Studio.

This module provides comprehensive type safety using Pydantic v2 models
for all core data structures in Manim Studio.
"""

from typing import Any, Dict, List, Optional, Union, Literal, Tuple
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from enum import Enum
import numpy as np


# Enums for constrained types
class AnimationType(str, Enum):
    """Supported animation types."""
    CREATE = "create"
    FADE_IN = "fadein"
    FADE_OUT = "fadeout"
    TRANSFORM = "transform"
    MOVE_TO = "moveto"
    ROTATE = "rotate"
    SCALE = "scale"
    WRITE = "write"
    UNWRITE = "unwrite"
    GROW_FROM_CENTER = "growfromcenter"
    SHRINK_TO_CENTER = "shrinktocenter"
    GROW_FROM_EDGE = "growfromedge"
    GROW_FROM_POINT = "growfrompoint"
    MORPH = "morph"
    RESTORE = "restore"
    SHIFT = "shift"
    COMPLEX_ANIMATION = "complex"


class ShapeType(str, Enum):
    """Supported shape types."""
    CIRCLE = "circle"
    SQUARE = "square"
    RECTANGLE = "rectangle"
    TRIANGLE = "triangle"
    POLYGON = "polygon"
    LINE = "line"
    ARROW = "arrow"
    DOT = "dot"
    ELLIPSE = "ellipse"
    ARC = "arc"
    SECTOR = "sector"
    ANNULUS = "annulus"
    CUSTOM = "custom"


class EffectType(str, Enum):
    """Supported effect types."""
    FADE = "fade"
    GLOW = "glow"
    SHADOW = "shadow"
    BLUR = "blur"
    RIPPLE = "ripple"
    WAVE = "wave"
    PARTICLE = "particle"
    SPARKLE = "sparkle"
    TRAIL = "trail"
    DISTORTION = "distortion"
    CHROMATIC = "chromatic"
    MORPH_GLOW = "morph_glow"


class CameraType(str, Enum):
    """Camera types."""
    CAMERA_2D = "2d"
    CAMERA_3D = "3d"


class RenderQuality(str, Enum):
    """Render quality presets."""
    LOW = "l"
    MEDIUM = "m"
    HIGH = "h"
    PRODUCTION = "p"
    ULTRA = "k"


# Base model configuration
class StrictModel(BaseModel):
    """Base model with strict validation."""
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        extra='forbid',
        str_strip_whitespace=True
    )


# Vector types
class Vector2D(StrictModel):
    """2D vector with x, y coordinates."""
    x: float = Field(default=0.0, description="X coordinate")
    y: float = Field(default=0.0, description="Y coordinate")
    
    @classmethod
    def from_list(cls, coords: List[float]) -> "Vector2D":
        """Create from [x, y] list."""
        if len(coords) != 2:
            raise ValueError("Vector2D requires exactly 2 coordinates")
        return cls(x=coords[0], y=coords[1])
    
    def to_list(self) -> List[float]:
        """Convert to [x, y] list."""
        return [self.x, self.y]


class Vector3D(StrictModel):
    """3D vector with x, y, z coordinates."""
    x: float = Field(default=0.0, description="X coordinate")
    y: float = Field(default=0.0, description="Y coordinate")
    z: float = Field(default=0.0, description="Z coordinate")
    
    @classmethod
    def from_list(cls, coords: List[float]) -> "Vector3D":
        """Create from [x, y, z] list."""
        if len(coords) != 3:
            raise ValueError("Vector3D requires exactly 3 coordinates")
        return cls(x=coords[0], y=coords[1], z=coords[2])
    
    def to_list(self) -> List[float]:
        """Convert to [x, y, z] list."""
        return [self.x, self.y, self.z]
    
    def to_numpy(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.x, self.y, self.z])


# Color type
class Color(StrictModel):
    """Color representation supporting hex, RGB, and named colors."""
    value: str = Field(description="Color value (hex, rgb, or name)")
    
    @field_validator('value')
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate color format."""
        v = v.strip()
        
        # Hex color
        if v.startswith('#'):
            if len(v) not in [4, 7]:  # #RGB or #RRGGBB
                raise ValueError(f"Invalid hex color: {v}")
            try:
                int(v[1:], 16)
            except ValueError:
                raise ValueError(f"Invalid hex color: {v}")
            return v.upper()
        
        # RGB format
        if v.startswith('rgb(') and v.endswith(')'):
            return v
        
        # Named colors - basic validation
        named_colors = {
            'white', 'black', 'red', 'green', 'blue', 'yellow',
            'cyan', 'magenta', 'gray', 'grey', 'orange', 'purple',
            'brown', 'pink', 'gold', 'silver'
        }
        if v.lower() in named_colors:
            return v.upper()
        
        # Manim color constants
        manim_colors = {
            'WHITE', 'BLACK', 'RED', 'GREEN', 'BLUE', 'YELLOW',
            'GOLD', 'RED_A', 'RED_B', 'RED_C', 'RED_D', 'RED_E',
            'BLUE_A', 'BLUE_B', 'BLUE_C', 'BLUE_D', 'BLUE_E',
            'GREEN_A', 'GREEN_B', 'GREEN_C', 'GREEN_D', 'GREEN_E',
            'YELLOW_A', 'YELLOW_B', 'YELLOW_C', 'YELLOW_D', 'YELLOW_E',
            'MAROON_A', 'MAROON_B', 'MAROON_C', 'MAROON_D', 'MAROON_E',
            'PURPLE_A', 'PURPLE_B', 'PURPLE_C', 'PURPLE_D', 'PURPLE_E',
            'TEAL_A', 'TEAL_B', 'TEAL_C', 'TEAL_D', 'TEAL_E',
            'PINK', 'LIGHT_PINK', 'ORANGE', 'LIGHT_BROWN', 'DARK_BROWN',
            'GRAY', 'LIGHT_GRAY', 'LIGHTER_GRAY', 'DARK_GRAY', 'DARKER_GRAY'
        }
        if v.upper() in manim_colors:
            return v.upper()
        
        raise ValueError(f"Invalid color format: {v}")


# Object models
class TextObject(StrictModel):
    """Text object configuration."""
    id: str = Field(description="Unique identifier")
    type: Literal["text"] = Field(default="text")
    content: str = Field(description="Text content")
    position: Vector3D = Field(default_factory=lambda: Vector3D())
    color: Color = Field(default_factory=lambda: Color(value="#FFFFFF"))
    font_size: int = Field(default=48, ge=1, le=200)
    font: str = Field(default="Arial")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    rotation: float = Field(default=0.0, description="Rotation in radians")
    scale: float = Field(default=1.0, gt=0.0)


class ShapeObject(StrictModel):
    """Shape object configuration."""
    id: str = Field(description="Unique identifier")
    type: ShapeType
    position: Vector3D = Field(default_factory=lambda: Vector3D())
    color: Color = Field(default_factory=lambda: Color(value="#FFFFFF"))
    fill_color: Optional[Color] = None
    stroke_color: Optional[Color] = None
    stroke_width: float = Field(default=2.0, ge=0.0)
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    rotation: float = Field(default=0.0)
    scale: Union[float, Vector3D] = Field(default=1.0)
    
    # Shape-specific parameters
    radius: Optional[float] = Field(default=None, gt=0.0, description="For circles")
    width: Optional[float] = Field(default=None, gt=0.0, description="For rectangles")
    height: Optional[float] = Field(default=None, gt=0.0, description="For rectangles")
    sides: Optional[int] = Field(default=None, ge=3, description="For polygons")
    points: Optional[List[Vector3D]] = Field(default=None, description="For custom shapes")
    
    @model_validator(mode='after')
    def validate_shape_params(self) -> 'ShapeObject':
        """Validate shape-specific parameters."""
        if self.type == ShapeType.CIRCLE and self.radius is None:
            self.radius = 1.0
        elif self.type in [ShapeType.SQUARE, ShapeType.RECTANGLE]:
            if self.width is None:
                self.width = 1.0
            if self.height is None:
                self.height = self.width if self.type == ShapeType.SQUARE else 0.5
        elif self.type == ShapeType.POLYGON and self.sides is None:
            raise ValueError("Polygon requires 'sides' parameter")
        return self


class Animation(StrictModel):
    """Animation configuration."""
    type: AnimationType
    target: str = Field(description="Target object ID")
    duration: float = Field(default=1.0, gt=0.0)
    start_time: float = Field(default=0.0, ge=0.0)
    
    # Animation-specific parameters
    end_position: Optional[Vector3D] = None
    end_scale: Optional[Union[float, Vector3D]] = None
    end_rotation: Optional[float] = None
    end_opacity: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    path: Optional[List[Vector3D]] = None
    easing: str = Field(default="smooth", description="Easing function")
    
    @model_validator(mode='after')
    def validate_animation_params(self) -> 'Animation':
        """Validate animation-specific parameters."""
        if self.type == AnimationType.MOVE_TO and self.end_position is None:
            raise ValueError("move_to animation requires end_position")
        if self.type == AnimationType.SCALE and self.end_scale is None:
            raise ValueError("scale animation requires end_scale")
        if self.type == AnimationType.ROTATE and self.end_rotation is None:
            raise ValueError("rotate animation requires end_rotation")
        if self.type == AnimationType.FADE_OUT and self.end_opacity is None:
            self.end_opacity = 0.0
        if self.type == AnimationType.FADE_IN and self.end_opacity is None:
            self.end_opacity = 1.0
        return self


class Effect(StrictModel):
    """Effect configuration."""
    type: EffectType
    params: Dict[str, Any] = Field(default_factory=dict)
    start_time: float = Field(default=0.0, ge=0.0)
    duration: Optional[float] = Field(default=None, gt=0.0)
    target: Optional[str] = Field(default=None, description="Target object ID")


class Camera2DConfig(StrictModel):
    """2D camera configuration."""
    position: Vector2D = Field(default_factory=lambda: Vector2D())
    zoom: float = Field(default=1.0, gt=0.0)
    background_color: Color = Field(default_factory=lambda: Color(value="#000000"))


class Camera3DConfig(StrictModel):
    """3D camera configuration."""
    position: Vector3D = Field(default_factory=lambda: Vector3D(x=0, y=-5, z=3))
    look_at: Vector3D = Field(default_factory=lambda: Vector3D())
    up_vector: Vector3D = Field(default_factory=lambda: Vector3D(x=0, y=0, z=1))
    fov: float = Field(default=60.0, gt=0.0, le=180.0, description="Field of view in degrees")
    near: float = Field(default=0.1, gt=0.0)
    far: float = Field(default=100.0, gt=0.0)
    
    @model_validator(mode='after')
    def validate_camera_distances(self) -> 'Camera3DConfig':
        """Validate near/far planes."""
        if self.near >= self.far:
            raise ValueError("Near plane must be less than far plane")
        return self


class SceneConfig(StrictModel):
    """Complete scene configuration."""
    name: str = Field(description="Scene name")
    duration: float = Field(gt=0.0, description="Total duration in seconds")
    fps: int = Field(default=60, ge=1, le=120)
    resolution: Tuple[int, int] = Field(default=(1920, 1080))
    background_color: Color = Field(default_factory=lambda: Color(value="#000000"))
    
    camera_type: CameraType = Field(default=CameraType.CAMERA_2D)
    camera: Union[Camera2DConfig, Camera3DConfig] = Field(default_factory=Camera2DConfig)
    
    objects: List[Union[TextObject, ShapeObject]] = Field(default_factory=list)
    animations: List[Animation] = Field(default_factory=list)
    effects: List[Effect] = Field(default_factory=list)
    
    @model_validator(mode='after')
    def validate_camera_config(self) -> 'SceneConfig':
        """Ensure camera config matches camera type."""
        if self.camera_type == CameraType.CAMERA_3D:
            if not isinstance(self.camera, Camera3DConfig):
                self.camera = Camera3DConfig()
        else:
            if not isinstance(self.camera, Camera2DConfig):
                self.camera = Camera2DConfig()
        return self
    
    @field_validator('resolution')
    @classmethod
    def validate_resolution(cls, v: Any) -> Tuple[int, int]:
        """Validate and convert resolution."""
        if isinstance(v, list) and len(v) == 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, str):
            # Parse "1920x1080" format
            parts = v.lower().replace('x', ' ').split()
            if len(parts) == 2:
                return (int(parts[0]), int(parts[1]))
        if isinstance(v, tuple) and len(v) == 2:
            return v
        raise ValueError("Resolution must be [width, height] or 'widthxheight'")


# Render configuration
class RenderConfig(StrictModel):
    """Render configuration."""
    quality: RenderQuality = Field(default=RenderQuality.HIGH)
    format: Literal["mp4", "gif", "png", "webm"] = Field(default="mp4")
    transparent: bool = Field(default=False)
    preview: bool = Field(default=True)
    output_dir: str = Field(default="user-data")
    save_last_frame: bool = Field(default=False)
    save_sections: bool = Field(default=False)
    

# Timeline models
class TimelineEvent(StrictModel):
    """Single timeline event."""
    time: float = Field(ge=0.0)
    type: Literal["animation", "effect", "camera", "custom"]
    action: str
    target: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)


class Timeline(StrictModel):
    """Timeline containing ordered events."""
    events: List[TimelineEvent] = Field(default_factory=list)
    duration: float = Field(gt=0.0)
    
    @model_validator(mode='after')
    def validate_event_times(self) -> 'Timeline':
        """Ensure all events are within timeline duration."""
        for event in self.events:
            if event.time > self.duration:
                raise ValueError(f"Event at {event.time}s exceeds timeline duration {self.duration}s")
        return self
    
    def add_event(self, event: TimelineEvent) -> None:
        """Add event maintaining time order."""
        self.events.append(event)
        self.events.sort(key=lambda e: e.time)


# Export models for YAML/JSON
class ExportConfig(StrictModel):
    """Configuration for exporting scenes."""
    include_metadata: bool = Field(default=True)
    include_comments: bool = Field(default=True)
    minify: bool = Field(default=False)
    format: Literal["yaml", "json"] = Field(default="yaml")


# Validation result models
class ValidationError(StrictModel):
    """Validation error details."""
    field: str
    message: str
    severity: Literal["error", "warning", "info"] = "error"
    line: Optional[int] = None
    column: Optional[int] = None


class ValidationResult(StrictModel):
    """Complete validation result."""
    valid: bool
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[ValidationError] = Field(default_factory=list)
    
    def add_error(self, field: str, message: str, line: Optional[int] = None) -> None:
        """Add validation error."""
        self.errors.append(ValidationError(
            field=field,
            message=message,
            severity="error",
            line=line
        ))
        self.valid = False
    
    def add_warning(self, field: str, message: str, line: Optional[int] = None) -> None:
        """Add validation warning."""
        self.warnings.append(ValidationError(
            field=field,
            message=message,
            severity="warning",
            line=line
        ))


# Type aliases for common patterns
ObjectType = Union[TextObject, ShapeObject]
CameraConfig = Union[Camera2DConfig, Camera3DConfig]
Position = Union[Vector2D, Vector3D, List[float]]
Scale = Union[float, Vector3D, List[float]]


# Conversion utilities
def position_to_vector(pos: Position) -> Union[Vector2D, Vector3D]:
    """Convert various position formats to Vector."""
    if isinstance(pos, (Vector2D, Vector3D)):
        return pos
    if isinstance(pos, list):
        if len(pos) == 2:
            return Vector2D.from_list(pos)
        elif len(pos) == 3:
            return Vector3D.from_list(pos)
    raise ValueError(f"Invalid position format: {pos}")


def scale_to_vector(scale: Scale) -> Union[float, Vector3D]:
    """Convert various scale formats."""
    if isinstance(scale, (int, float)):
        return float(scale)
    if isinstance(scale, Vector3D):
        return scale
    if isinstance(scale, list) and len(scale) == 3:
        return Vector3D.from_list(scale)
    raise ValueError(f"Invalid scale format: {scale}")