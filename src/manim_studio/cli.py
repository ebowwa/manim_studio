"""Command-line interface for Manim Studio."""

import argparse
import sys
from pathlib import Path
from manim import *
from .core import Config, SceneBuilder


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Manim Studio - Configuration-driven animation creation"
    )
    
    parser.add_argument(
        "config",
        help="Path to configuration file (YAML or JSON)"
    )
    
    parser.add_argument(
        "-s", "--scene",
        help="Name of scene to render (if config contains multiple scenes)"
    )
    
    parser.add_argument(
        "-q", "--quality",
        choices=["l", "m", "h", "p", "k"],
        default="h",
        help="Render quality: l=480p, m=720p, h=1080p, p=1440p, k=4K"
    )
    
    parser.add_argument(
        "-p", "--preview",
        action="store_true",
        help="Preview animation after rendering"
    )
    
    parser.add_argument(
        "--fps",
        type=int,
        help="Override FPS from config"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)
    
    try:
        config = Config(config_path)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Get scene configuration
    if args.scene:
        scene_name = args.scene
    else:
        # If no scene specified, try to get the default or first scene
        scenes = config.list_scenes()
        if not scenes:
            # Single scene configuration
            scene_name = config.get('name', 'Scene')
        else:
            scene_name = scenes[0]
    
    # Build the scene
    builder = SceneBuilder.from_config_file(str(config_path))
    
    try:
        if scene_name in config.list_scenes():
            scene_config = config.get_scene_config(scene_name)
            SceneClass = builder.build_scene(scene_config)
        else:
            # Single scene configuration (entire config is the scene)
            from .core.config import SceneConfig
            scene_config = SceneConfig.from_dict(config.data)
            SceneClass = builder.build_scene(scene_config)
    except Exception as e:
        print(f"Error building scene: {e}")
        sys.exit(1)
    
    # Set up Manim configuration
    manim_config = {
        "quality": args.quality + "_quality",
        "preview": args.preview,
        "write_to_movie": True,
        "save_last_frame": False,
    }
    
    if args.fps:
        manim_config["frame_rate"] = args.fps
    elif hasattr(scene_config, 'fps'):
        manim_config["frame_rate"] = scene_config.fps
    
    if args.output:
        manim_config["output_file"] = args.output
    
    # Configure Manim
    for key, value in manim_config.items():
        setattr(config, key, value)
    
    # Render the scene
    print(f"Rendering scene: {scene_name}")
    scene = SceneClass()
    scene.render()
    
    print("Rendering complete!")


if __name__ == "__main__":
    main()