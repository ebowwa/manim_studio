#!/usr/bin/env python
"""Demo of frame extraction feature in Manim Studio.

This example shows how to configure and use automatic frame extraction
during animation rendering.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from manim import *
from src.manim_studio.core.config import SceneConfig, AnimationConfig
from src.manim_studio.core.scene_builder import SceneBuilder
from src.manim_studio.core.render_hooks import auto_extract_frames


def create_demo_scene_config():
    """Create a demo scene configuration with frame extraction enabled."""
    scene_config = SceneConfig(
        name="FrameExtractionDemo",
        description="Demo of automatic frame extraction during rendering",
        duration=10.0,
        background_color="#1a1a1a",
        
        # Enable frame extraction
        frame_extraction={
            "enabled": True,
            "frame_interval": 15,  # Extract every 15 frames
            "analyze": True,  # Analyze extracted frames
            "generate_report": True,  # Generate PDF report
            "keyframe_extraction": False,  # Also extract keyframes
            "max_frames": 50,  # Limit to 50 frames max
            "output_dir": "extracted_frames/demo"  # Output directory
        }
    )
    
    # Add some animated objects
    scene_config.objects = {
        "title": {
            "type": "text",
            "text": "Frame Extraction Demo",
            "params": {
                "scale": 1.5,
                "color": "#00ff00",
                "position": [0, 2, 0]
            }
        },
        "circle": {
            "type": "shape",
            "shape": "circle",
            "params": {
                "radius": 1.0,
                "color": "#ff0000",
                "fill_color": "#ff0000",
                "fill_opacity": 0.5,
                "position": [-3, 0, 0]
            }
        },
        "square": {
            "type": "shape",
            "shape": "rectangle",
            "params": {
                "width": 2.0,
                "height": 2.0,
                "color": "#0000ff",
                "fill_color": "#0000ff",
                "fill_opacity": 0.5,
                "position": [3, 0, 0]
            }
        }
    }
    
    # Add animations
    scene_config.animations = [
        AnimationConfig(
            target="title",
            animation_type="write",
            start_time=0.0,
            duration=2.0
        ),
        AnimationConfig(
            target="circle",
            animation_type="fadein",
            start_time=1.0,
            duration=1.0,
            params={"shift": [0, 2, 0]}
        ),
        AnimationConfig(
            target="square",
            animation_type="fadein",
            start_time=1.5,
            duration=1.0,
            params={"shift": [0, -2, 0]}
        ),
        AnimationConfig(
            target="circle",
            animation_type="move",
            start_time=3.0,
            duration=2.0,
            params={"to": [0, 0, 0]}
        ),
        AnimationConfig(
            target="square",
            animation_type="rotate",
            start_time=3.5,
            duration=2.0,
            params={"angle": PI}
        ),
        AnimationConfig(
            target="circle",
            animation_type="scale",
            start_time=6.0,
            duration=1.0,
            params={"factor": 2.0}
        ),
        AnimationConfig(
            target="title",
            animation_type="fadeout",
            start_time=8.0,
            duration=1.0
        ),
        AnimationConfig(
            target="circle",
            animation_type="fadeout",
            start_time=8.5,
            duration=1.0
        ),
        AnimationConfig(
            target="square",
            animation_type="fadeout",
            start_time=9.0,
            duration=1.0
        )
    ]
    
    return scene_config


def create_manual_extraction_scene():
    """Create a scene with manual frame extraction control."""
    from src.manim_studio.core.render_hooks import FrameExtractionMixin
    
    class ManualExtractionScene(FrameExtractionMixin, Scene):
        def construct(self):
            # Enable frame extraction with custom settings
            self.enable_frame_extraction(
                frame_interval=10,
                analyze=True,
                output_dir="extracted_frames/manual",
                keyframe_extraction=True,
                keyframe_threshold=25.0
            )
            
            # Create animation
            text = Text("Manual Frame Extraction", color=YELLOW)
            circle = Circle(radius=1, color=BLUE, fill_opacity=0.5)
            
            self.play(Write(text))
            self.play(text.animate.shift(UP * 2))
            self.play(FadeIn(circle))
            self.play(
                circle.animate.scale(2).set_color(RED),
                text.animate.set_color(GREEN)
            )
            self.play(
                Rotate(circle, angle=2*PI),
                text.animate.shift(DOWN * 2)
            )
            self.play(FadeOut(text), FadeOut(circle))
    
    return ManualExtractionScene


def main():
    """Run the frame extraction demo."""
    print("Frame Extraction Demo")
    print("=" * 60)
    print()
    print("This demo shows two ways to use frame extraction:")
    print("1. Through scene configuration (automatic)")
    print("2. Using the FrameExtractionMixin (manual)")
    print()
    
    # Method 1: Using scene configuration
    print("Method 1: Building scene from configuration...")
    scene_config = create_demo_scene_config()
    builder = SceneBuilder()
    ConfiguredScene = builder.build_scene(scene_config)
    
    print(f"Scene will extract frames to: {scene_config.frame_extraction['output_dir']}")
    print(f"Frame interval: {scene_config.frame_extraction['frame_interval']}")
    print(f"Analysis enabled: {scene_config.frame_extraction['analyze']}")
    print()
    
    # Render the configured scene
    print("Rendering configured scene...")
    scene1 = ConfiguredScene()
    scene1.render()
    
    print("\n" + "=" * 60 + "\n")
    
    # Method 2: Using manual extraction
    print("Method 2: Using manual frame extraction...")
    ManualScene = create_manual_extraction_scene()
    scene2 = ManualScene()
    scene2.render()
    
    print("\n" + "=" * 60)
    print("Demo complete! Check the 'extracted_frames' directory for results.")
    print("You should find:")
    print("  - Extracted frame images")
    print("  - Analysis reports (if enabled)")
    print("  - Frame grid visualizations")
    print("=" * 60)


if __name__ == "__main__":
    main()