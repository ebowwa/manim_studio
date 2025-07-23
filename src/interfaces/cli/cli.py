"""Command-line interface for Manim Studio."""

import argparse
import sys
from pathlib import Path
from manim import *
from src.core import Config, SceneBuilder
from src.core.yaml_validator import validate_yaml_file
from src.core.cache import configure_cache


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Manim Studio - Configuration-driven animation creation",
        epilog="""
Frame Extraction:
  Frame extraction can be enabled in your configuration file by adding a
  'frame_extraction' section to your scene config:
  
  frame_extraction:
    enabled: true
    frame_interval: 30      # Extract every 30 frames
    analyze: true           # Generate quality analysis
    output_dir: "frames"    # Output directory
  
  See docs/frame_extraction.md for full documentation.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
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
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching"
    )
    
    parser.add_argument(
        "--cache-dir",
        help="Custom cache directory"
    )
    
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear cache before rendering"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate YAML configuration and exit (don't render)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed validation results (warnings and info)"
    )
    
    args = parser.parse_args()
    
    # Configure caching
    cache_config = {
        'enabled': not args.no_cache
    }
    if args.cache_dir:
        cache_config['cache_dir'] = args.cache_dir
    
    configure_cache(**cache_config)
    
    # Clear cache if requested
    if args.clear_cache:
        from .core import get_cache
        cache = get_cache()
        cache.clear()
        print("Cache cleared.")
    
    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)
    
    # Validate YAML if it's a YAML file
    if config_path.suffix.lower() in ['.yaml', '.yml']:
        is_valid = validate_yaml_file(str(config_path), verbose=args.verbose)
        if not is_valid:
            print(f"❌ YAML validation failed for: {config_path}")
            sys.exit(1)
        if args.validate_only:
            print(f"✅ YAML validation passed for: {config_path}")
            sys.exit(0)
    elif args.validate_only:
        print(f"ℹ️  Validation skipped for non-YAML file: {config_path}")
        sys.exit(0)
    
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
            # Check if config has 'scene' key
            if 'scene' in config.data:
                scene_name = config.data['scene'].get('name', 'Scene')
            else:
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
            from src.core.config import SceneConfig
            # Check if config has 'scene' key (single scene format)
            if 'scene' in config.data:
                scene_config = SceneConfig.from_dict(config.data['scene'])
            else:
                # Assume entire config is the scene
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
        "media_dir": "user-data",
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