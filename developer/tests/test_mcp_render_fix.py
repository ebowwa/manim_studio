#!/usr/bin/env python3
"""Test script to verify MCP render command fix"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.interfaces.shared_features import ManimStudioCore, InterfaceResult

# Create a simple test
core = ManimStudioCore()

# Create a scene
result = core.create_scene("test_scene", duration=3.0)
print(f"Create scene: {result.status}")

# Add a simple text
result = core.add_text("hello", "Hello MCP!", color="#FFD700", position=[0, 0, 0])
print(f"Add text: {result.status}")

# Add fade in animation
result = core.add_animation("hello", "fadein", start_time=0, duration=1)
print(f"Add animation: {result.status}")

# Test prepare_render to see the command
result = core.prepare_render("test_output.mp4", quality="low", save_script=False)
print(f"\nPrepare render: {result.status}")
if result.status == "success":
    print(f"Render command: {result.data['render_command']}")
    print(f"Script path: {result.data['script_path']}")
    
    # Read the generated script
    with open(result.data['script_path'], 'r') as f:
        print("\nGenerated script preview:")
        print("=" * 50)
        print(f.read()[:500] + "...")