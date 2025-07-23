#!/usr/bin/env python3
"""Test GUI features directly without circular imports."""

import os
import sys
import json

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now we can import from interfaces
from src.interfaces.shared_state import SharedState
from src.interfaces.shared_features import (
    SharedFeatures, SceneDefinition, ObjectDefinition, 
    AnimationDefinition, RenderQuality, InterfaceResult
)

def test_gui_rendering():
    """Test the GUI rendering functionality directly."""
    print("Testing GUI rendering functionality...\n")
    
    # Initialize shared features
    features = SharedFeatures()
    print("✅ SharedFeatures initialized")
    
    # Create a scene
    scene_def = SceneDefinition(
        name="GUITestScene",
        duration=5.0,
        background_color="#1a1a1a",
        resolution=(1920, 1080),
        fps=30
    )
    
    result = features.create_scene(scene_def)
    print(f"\n1. Create scene: {result.status}")
    if result.status == "error":
        print(f"   Error: {result.error}")
        return
    print(f"   Message: {result.message}")
    
    # Add a text object
    text_obj = ObjectDefinition(
        id="title_text",
        type="text",
        content="GUI Rendering Works!",
        position=(0, 2, 0),
        color="#FFD700",  # Gold color
        scale=1.2
    )
    
    result = features.add_object(text_obj)
    print(f"\n2. Add text object: {result.status}")
    if result.status == "error":
        print(f"   Error: {result.error}")
        return
    
    # Add a shape
    shape_obj = ObjectDefinition(
        id="demo_circle",
        type="circle",
        position=(0, -1, 0),
        color="#FF6B6B",
        scale=0.8
    )
    
    result = features.add_object(shape_obj)
    print(f"\n3. Add circle: {result.status}")
    
    # Add animations
    animations = [
        AnimationDefinition(
            target_id="title_text",
            animation_type="FadeIn",
            start_time=0.5,
            duration=1.0
        ),
        AnimationDefinition(
            target_id="demo_circle",
            animation_type="GrowFromCenter",
            start_time=1.5,
            duration=1.0
        ),
        AnimationDefinition(
            target_id="title_text",
            animation_type="Indicate",
            start_time=3.0,
            duration=1.0,
            parameters={"color": "#00FF00"}
        )
    ]
    
    for i, anim in enumerate(animations):
        result = features.add_animation(anim)
        print(f"\n4.{i+1}. Add animation {anim.animation_type}: {result.status}")
    
    # Test rendering
    print("\n5. Testing render functionality...")
    
    # First test prepare_render
    result = features.prepare_render(
        output_path="gui_test_output.mp4",
        quality=RenderQuality.LOW
    )
    
    print(f"\n   Prepare render: {result.status}")
    if result.status == "success":
        print(f"   Script path: {result.data.get('script_path', 'N/A')}")
        print(f"   Render command: {result.data.get('render_command', 'N/A')[:100]}...")
        
        # Show the generated script
        script_path = result.data.get('script_path')
        if script_path and os.path.exists(script_path):
            print("\n   Generated Manim script preview:")
            print("   " + "-" * 50)
            with open(script_path, 'r') as f:
                lines = f.readlines()[:20]  # First 20 lines
                for line in lines:
                    print(f"   {line.rstrip()}")
            print("   " + "-" * 50)
    else:
        print(f"   Error: {result.error}")
        return
    
    # Now test full render
    print("\n6. Testing full render pipeline...")
    result = features.render_scene(
        output_path="gui_test_output.mp4",
        quality=RenderQuality.LOW,
        preview=False
    )
    
    print(f"\n   Render result: {result.status}")
    if result.status == "success":
        print(f"   Message: {result.message}")
        if result.data:
            print(f"   Output file: {result.data.get('output_file', 'Unknown')}")
            print(f"   Script saved: {result.data.get('permanent_script_path', 'Not saved')}")
            
            # Check if file exists
            output_file = result.data.get('output_file')
            if output_file and os.path.exists(output_file):
                print(f"\n   ✅ Video successfully created!")
                print(f"   File size: {os.path.getsize(output_file)} bytes")
                print(f"   Location: {output_file}")
            else:
                print(f"\n   ⚠️ Video file not found at: {output_file}")
    else:
        print(f"   Error: {result.error}")
        if result.data:
            print("\n   Stdout:")
            print(result.data.get('stdout', '')[:500])
            print("\n   Stderr:")
            print(result.data.get('stderr', '')[:500])
    
    print("\n" + "="*60)
    print("GUI rendering test complete!")

if __name__ == "__main__":
    test_gui_rendering()