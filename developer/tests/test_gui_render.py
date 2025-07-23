#!/usr/bin/env python3
"""Test script to verify GUI rendering functionality."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.interfaces.shared_features import SharedFeatures, SceneDefinition, ObjectDefinition, AnimationDefinition

def test_render():
    """Test the rendering functionality programmatically."""
    print("Testing Manim Studio rendering functionality...")
    
    # Initialize shared features
    features = SharedFeatures()
    
    # Create a simple scene
    scene_def = SceneDefinition(
        name="TestScene",
        duration=3.0,
        background_color="#000000",
        resolution=(1920, 1080),
        fps=30
    )
    
    # Create scene
    result = features.create_scene(scene_def)
    print(f"Create scene: {result.status} - {result.message}")
    if result.status == "error":
        print(f"Error: {result.error}")
        return
    
    # Add a text object
    text_obj = ObjectDefinition(
        id="test_text",
        type="text",
        content="Testing GUI Render",
        position=(0, 0, 0),
        color="#FFFFFF",
        scale=1.0
    )
    
    result = features.add_object(text_obj)
    print(f"Add text: {result.status} - {result.message}")
    
    # Add a simple animation
    anim = AnimationDefinition(
        target_id="test_text",
        animation_type="FadeIn",
        start_time=0.5,
        duration=1.0
    )
    
    result = features.add_animation(anim)
    print(f"Add animation: {result.status} - {result.message}")
    
    # Test render
    print("\nTesting render functionality...")
    result = features.render_scene(
        output_path="test_output.mp4",
        quality="low",  # Use low quality for faster testing
        preview=False
    )
    
    print(f"\nRender result: {result.status}")
    if result.status == "success":
        print(f"Message: {result.message}")
        if result.data:
            print(f"Output file: {result.data.get('output_file', 'Unknown')}")
            print(f"Script saved: {result.data.get('permanent_script_path', 'Not saved')}")
    else:
        print(f"Error: {result.error}")
        if result.data:
            print("\nStdout:")
            print(result.data.get('stdout', ''))
            print("\nStderr:")
            print(result.data.get('stderr', ''))

if __name__ == "__main__":
    test_render()