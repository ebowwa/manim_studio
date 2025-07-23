# Manim Studio Type System Guide

This guide explains the comprehensive type system implemented in Manim Studio using Pydantic v2.

## Overview

Manim Studio now uses Pydantic for:
- **Type Safety**: All configurations are strongly typed
- **Validation**: Automatic validation of input data
- **Error Messages**: Clear, actionable error messages
- **Serialization**: Easy conversion between Python objects, YAML, and JSON

## Core Type Modules

### 1. `src/core/types.py`
The main type definitions module containing all Pydantic models:

```python
from src.core.types import (
    SceneConfig, TextObject, ShapeObject, Animation,
    AnimationType, ShapeType, EffectType, Effect,
    Vector3D, Color, RenderConfig
)
```

### 2. `src/core/config_v2.py`
The new configuration system with backward compatibility:

```python
from src.core.config_v2 import ManimStudioConfig

# Load from YAML with validation
config = ManimStudioConfig.from_yaml("scene.yaml")

# Validate semantics
validation = config.validate_semantics()
```

## Key Type Definitions

### Vectors
```python
# 2D Vector
vec2d = Vector2D(x=1.0, y=2.0)

# 3D Vector  
vec3d = Vector3D(x=1.0, y=2.0, z=3.0)

# From list
vec = Vector3D.from_list([1, 2, 3])
```

### Colors
```python
# Hex color
color1 = Color(value="#FF0000")

# Named color
color2 = Color(value="RED")

# Manim constant
color3 = Color(value="BLUE_A")
```

### Objects
```python
# Text object
text = TextObject(
    id="title",
    content="Hello World",
    position=Vector3D(x=0, y=0, z=0),
    color=Color(value="#FFFFFF"),
    font_size=48
)

# Shape object
circle = ShapeObject(
    id="circle_1",
    type=ShapeType.CIRCLE,
    radius=1.0,
    color=Color(value="#00FF00")
)
```

### Animations
```python
# Movement animation
move = Animation(
    type=AnimationType.MOVE_TO,
    target="circle_1",
    duration=2.0,
    end_position=Vector3D(x=3, y=0, z=0)
)

# Scale animation
scale = Animation(
    type=AnimationType.SCALE,
    target="circle_1", 
    duration=1.0,
    end_scale=2.0
)
```

## Type Safety Benefits

### 1. Compile-Time Checking
```python
# This will be caught by type checkers
text = TextObject(
    id="test",
    content=123,  # ❌ Type error: expected str
    font_size="big"  # ❌ Type error: expected int
)
```

### 2. Runtime Validation
```python
# This will raise a validation error
try:
    shape = ShapeObject(
        id="shape",
        type="invalid_type",  # ❌ Not in ShapeType enum
        radius=-1.0  # ❌ Must be positive
    )
except ValidationError as e:
    print(e)
```

### 3. Clear Error Messages
```python
# Pydantic provides detailed error messages
ValidationError: 2 validation errors for ShapeObject
type
  Input should be 'circle', 'square', 'rectangle', etc.
radius
  Input should be greater than 0
```

## Migration Guide

### From Dataclasses to Pydantic

**Before (dataclass):**
```python
@dataclass
class EffectConfig:
    type: str
    params: Dict[str, Any] = field(default_factory=dict)
```

**After (Pydantic):**
```python
class Effect(BaseModel):
    type: EffectType
    params: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        # Custom validation logic
        return v
```

### From Dictionaries to Models

**Before:**
```python
config = {
    "scene": {
        "name": "My Scene",
        "duration": 5.0,
        "objects": [...]
    }
}
```

**After:**
```python
config = ManimStudioConfig(
    scene=SceneConfig(
        name="My Scene",
        duration=5.0,
        objects=[...]
    )
)
```

## Best Practices

### 1. Use Type Hints Everywhere
```python
def create_animation(
    target: str,
    duration: float,
    animation_type: AnimationType
) -> Animation:
    return Animation(
        type=animation_type,
        target=target,
        duration=duration
    )
```

### 2. Leverage Validation
```python
class CustomObject(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    value: float = Field(ge=0, le=1)  # 0 <= value <= 1
    
    @model_validator(mode='after')
    def validate_custom_logic(self):
        # Add custom validation
        return self
```

### 3. Use Enums for Constants
```python
# Instead of strings
animation_type = "create"  # ❌

# Use enums
animation_type = AnimationType.CREATE  # ✅
```

### 4. Handle Validation Errors
```python
try:
    config = ManimStudioConfig.from_yaml("scene.yaml")
except ValidationError as e:
    for error in e.errors():
        print(f"Field: {error['loc']}")
        print(f"Error: {error['msg']}")
```

## Advanced Features

### Custom Validators
```python
class AdvancedShape(ShapeObject):
    @field_validator('color')
    @classmethod
    def validate_color_brightness(cls, v: Color) -> Color:
        # Custom validation for color brightness
        return v
```

### Computed Fields
```python
class AnimatedObject(BaseModel):
    start_pos: Vector3D
    end_pos: Vector3D
    
    @property
    def distance(self) -> float:
        return np.linalg.norm(
            self.end_pos.to_numpy() - self.start_pos.to_numpy()
        )
```

### Serialization Control
```python
class OptimizedConfig(BaseModel):
    model_config = ConfigDict(
        # Exclude None values when serializing
        exclude_none=True,
        # Custom field serialization
        json_encoders={
            Vector3D: lambda v: v.to_list()
        }
    )
```

## Performance Considerations

1. **Validation Overhead**: Pydantic validation has minimal overhead
2. **Lazy Loading**: Use validators only when needed
3. **Caching**: Pydantic caches validation schemas

## Testing with Types

```python
import pytest
from pydantic import ValidationError

def test_shape_validation():
    # Valid shape
    shape = ShapeObject(
        id="test",
        type=ShapeType.CIRCLE,
        radius=1.0
    )
    assert shape.radius == 1.0
    
    # Invalid shape
    with pytest.raises(ValidationError):
        ShapeObject(
            id="test",
            type=ShapeType.CIRCLE,
            radius=-1.0  # Negative radius
        )
```

## IDE Support

Modern IDEs provide excellent support for Pydantic:
- **Auto-completion**: All fields are auto-completed
- **Type checking**: Errors shown in real-time
- **Documentation**: Field descriptions shown on hover

## Conclusion

The new type system provides:
- ✅ Full type safety
- ✅ Runtime validation
- ✅ Better error messages
- ✅ Easier maintenance
- ✅ Better IDE support
- ✅ Automatic documentation

Start using types in your Manim Studio projects today!