"""Example of using the configuration system programmatically."""

from manim import *
from src.core import Config, SceneBuilder
from pathlib import Path


def render_from_config(config_path: str):
    """Render a scene from configuration file."""
    # Load configuration
    config = Config(config_path)
    
    # Create scene builder
    builder = SceneBuilder.from_config_file(config_path)
    
    # Get scene configuration
    scene_config = config.get_scene_config("MagicalShowcase")
    
    # Build the scene class
    SceneClass = builder.build_scene(scene_config)
    
    # Create and render the scene
    scene = SceneClass()
    scene.render()


def create_custom_config():
    """Create a configuration programmatically."""
    from src.core.config import SceneConfig, EffectConfig, AnimationConfig
    
    # Create scene configuration
    scene = SceneConfig(
        name="CustomScene",
        description="A programmatically created scene",
        duration=10.0,
        background_color="#1a1a1a",
        objects={
            "title": {
                "type": "text",
                "text": "Dynamic Configuration",
                "params": {
                    "gradient": ["#FF6B6B", "#4ECDC4"],
                    "scale": 1.5,
                    "position": [0, 0, 0]
                }
            }
        },
        effects=[
            EffectConfig(
                type="particle_system",
                start_time=1.0,
                params={
                    "n_emitters": 2,
                    "particles_per_second": 15,
                    "particle_color": "#FFD93D"
                }
            )
        ],
        animations=[
            AnimationConfig(
                target="title",
                animation_type="write",
                start_time=0.0,
                duration=2.0
            )
        ]
    )
    
    # Build and render
    builder = SceneBuilder()
    SceneClass = builder.build_scene(scene)
    
    scene_instance = SceneClass()
    scene_instance.render()


if __name__ == "__main__":
    # Example 1: Render from YAML config
    config_path = Path(__file__).parent.parent / "configs" / "example_scene.yaml"
    if config_path.exists():
        print("Rendering from YAML configuration...")
        render_from_config(str(config_path))
    
    # Example 2: Create configuration programmatically
    print("Creating scene programmatically...")
    create_custom_config()