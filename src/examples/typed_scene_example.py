"""Example of creating a Manim Studio scene using full type safety with Pydantic.

This demonstrates how to use the new typed configuration system to create
scenes with full validation and type safety.
"""

from pathlib import Path
from typing import List, Optional

# Import Pydantic models
from src.core.types import (
    SceneConfig, TextObject, ShapeObject, Animation,
    AnimationType, ShapeType, EffectType, Effect,
    Vector3D, Color, RenderConfig, RenderQuality,
    CameraType, Camera3DConfig
)
from src.core.config_v2 import ManimStudioConfig


def create_typed_scene() -> ManimStudioConfig:
    """Create a fully typed scene configuration."""
    
    # Create objects with full type safety
    title = TextObject(
        id="main_title",
        content="Type-Safe Manim Studio",
        position=Vector3D(x=0, y=2, z=0),
        color=Color(value="#FFFFFF"),
        font_size=72,
        font="Arial"
    )
    
    subtitle = TextObject(
        id="subtitle",
        content="Powered by Pydantic v2",
        position=Vector3D(x=0, y=1, z=0),
        color=Color(value="#888888"),
        font_size=36
    )
    
    # Create shapes
    circle = ShapeObject(
        id="circle_1",
        type=ShapeType.CIRCLE,
        position=Vector3D(x=-3, y=-1, z=0),
        color=Color(value="#FF0000"),
        radius=1.0
    )
    
    square = ShapeObject(
        id="square_1",
        type=ShapeType.SQUARE,
        position=Vector3D(x=0, y=-1, z=0),
        color=Color(value="#00FF00"),
        width=2.0
    )
    
    triangle = ShapeObject(
        id="triangle_1",
        type=ShapeType.TRIANGLE,
        position=Vector3D(x=3, y=-1, z=0),
        color=Color(value="#0000FF"),
        scale=1.5
    )
    
    # Create animations with validation
    animations: List[Animation] = [
        # Fade in title
        Animation(
            type=AnimationType.FADE_IN,
            target="main_title",
            duration=1.0,
            start_time=0.0
        ),
        # Write subtitle
        Animation(
            type=AnimationType.WRITE,
            target="subtitle",
            duration=1.5,
            start_time=0.5
        ),
        # Create shapes with staggered timing
        Animation(
            type=AnimationType.CREATE,
            target="circle_1",
            duration=1.0,
            start_time=2.0
        ),
        Animation(
            type=AnimationType.GROW_FROM_CENTER,
            target="square_1",
            duration=1.0,
            start_time=2.3
        ),
        Animation(
            type=AnimationType.GROW_FROM_POINT,
            target="triangle_1",
            duration=1.0,
            start_time=2.6
        ),
        # Animate shapes
        Animation(
            type=AnimationType.ROTATE,
            target="square_1",
            duration=2.0,
            start_time=4.0,
            end_rotation=3.14159  # PI radians
        ),
        Animation(
            type=AnimationType.SCALE,
            target="circle_1",
            duration=2.0,
            start_time=4.0,
            end_scale=2.0
        ),
        Animation(
            type=AnimationType.MOVE_TO,
            target="triangle_1",
            duration=2.0,
            start_time=4.0,
            end_position=Vector3D(x=3, y=1, z=0)
        )
    ]
    
    # Create effects
    effects: List[Effect] = [
        Effect(
            type=EffectType.GLOW,
            target="main_title",
            start_time=1.0,
            duration=5.0,
            params={"intensity": 0.5, "color": "#FFFF00"}
        ),
        Effect(
            type=EffectType.RIPPLE,
            start_time=2.0,
            duration=2.0,
            params={"center": [0, -1, 0], "amplitude": 0.3}
        )
    ]
    
    # Create scene configuration
    scene = SceneConfig(
        name="Typed Example Scene",
        duration=7.0,
        fps=60,
        resolution=(1920, 1080),
        background_color=Color(value="#000000"),
        objects=[title, subtitle, circle, square, triangle],
        animations=animations,
        effects=effects
    )
    
    # Create render configuration
    render = RenderConfig(
        quality=RenderQuality.HIGH,
        format="mp4",
        preview=True,
        output_dir="user-data"
    )
    
    # Create complete configuration
    config = ManimStudioConfig(
        scene=scene,
        render=render,
        metadata={
            "author": "Manim Studio",
            "version": "2.0.0",
            "created_with": "Pydantic Types"
        }
    )
    
    return config


def create_3d_typed_scene() -> ManimStudioConfig:
    """Create a 3D scene with full type safety."""
    
    # 3D camera configuration
    camera = Camera3DConfig(
        position=Vector3D(x=5, y=-5, z=3),
        look_at=Vector3D(x=0, y=0, z=0),
        fov=60.0
    )
    
    # Create 3D objects
    objects: List[ShapeObject] = []
    
    # Create a grid of shapes in 3D space
    for i in range(3):
        for j in range(3):
            shape = ShapeObject(
                id=f"shape_{i}_{j}",
                type=ShapeType.CIRCLE if (i + j) % 2 == 0 else ShapeType.SQUARE,
                position=Vector3D(x=(i-1)*2, y=(j-1)*2, z=0),
                color=Color(value=f"#{i*80:02x}{j*80:02x}FF"),
                radius=0.5 if (i + j) % 2 == 0 else None,
                width=1.0 if (i + j) % 2 == 1 else None
            )
            objects.append(shape)
    
    # Create animations for 3D movement
    animations: List[Animation] = []
    for i, obj in enumerate(objects):
        animations.append(Animation(
            type=AnimationType.CREATE,
            target=obj.id,
            duration=0.5,
            start_time=i * 0.1
        ))
        
        # Add vertical movement
        animations.append(Animation(
            type=AnimationType.MOVE_TO,
            target=obj.id,
            duration=2.0,
            start_time=2.0,
            end_position=Vector3D(
                x=obj.position.x,
                y=obj.position.y,
                z=1.5 if i % 2 == 0 else -1.5
            )
        ))
    
    # Create 3D scene
    scene = SceneConfig(
        name="3D Typed Example",
        duration=5.0,
        camera_type=CameraType.CAMERA_3D,
        camera=camera,
        objects=objects,
        animations=animations
    )
    
    return ManimStudioConfig(scene=scene)


def validate_and_save_scene() -> None:
    """Demonstrate validation and saving."""
    
    # Create scene
    config = create_typed_scene()
    
    # Validate semantics
    validation = config.validate_semantics()
    
    if validation.valid:
        print("✅ Scene validation passed!")
    else:
        print("❌ Scene validation failed:")
        for error in validation.errors:
            print(f"  - {error.field}: {error.message}")
        return
    
    # Save to different formats
    output_dir = Path("user-data/typed_examples")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as YAML
    yaml_path = output_dir / "typed_scene.yaml"
    config.to_yaml(yaml_path)
    print(f"📝 Saved YAML to: {yaml_path}")
    
    # Save as JSON
    json_path = output_dir / "typed_scene.json"
    config.to_json(json_path)
    print(f"📝 Saved JSON to: {json_path}")
    
    # Show timeline
    print("\n📅 Timeline Events:")
    for event in config.get_timeline_events():
        print(f"  {event['time']:.1f}s: {event['type']} - {event.get('animation', event.get('effect', {}))}")


if __name__ == "__main__":
    # Run examples
    print("🎯 Creating 2D typed scene...")
    validate_and_save_scene()
    
    print("\n🎯 Creating 3D typed scene...")
    config_3d = create_3d_typed_scene()
    config_3d.to_yaml(Path("user-data/typed_examples/typed_scene_3d.yaml"))
    print("✅ 3D scene created!")