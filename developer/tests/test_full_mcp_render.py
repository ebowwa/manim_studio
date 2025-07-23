#!/usr/bin/env python3
"""Full test of MCP rendering with the fix"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.interfaces.shared_features import ManimStudioCore

# Create a simple animation
core = ManimStudioCore()

# Create scene
print("Creating scene...")
result = core.create_scene("mcp_test", duration=5.0, background_color="#1a1a1a")
print(f"Scene created: {result.status}")

# Add some objects
print("\nAdding objects...")
core.add_text("title", "MCP Fixed!", color="#FFD700", position=[0, 2, 0], font_size=72)
core.add_shape("circle1", "circle", color="#FF0000", size=0.8, position=[-2, -1, 0])
core.add_shape("square1", "square", color="#00FF00", size=0.8, position=[0, -1, 0])
core.add_shape("triangle1", "triangle", color="#0000FF", size=0.8, position=[2, -1, 0])

# Add animations
print("\nAdding animations...")
core.add_animation("title", "write", start_time=0, duration=1.5)
core.add_animation("circle1", "fadein", start_time=1, duration=0.5)
core.add_animation("square1", "fadein", start_time=1.5, duration=0.5)
core.add_animation("triangle1", "fadein", start_time=2, duration=0.5)

# Animate the shapes
core.add_animation("circle1", "rotate", start_time=3, duration=1, properties={"angle": 3.14159})
core.add_animation("square1", "scale", start_time=3, duration=1, properties={"scale": 1.5})
core.add_animation("triangle1", "move", start_time=3, duration=1, properties={"position": [2, 1, 0]})

# Render the scene
print("\nRendering scene...")
result = core.render_scene("user-data/mcp_fixed_test.mp4", quality="low", save_script=True)

if result.status == "success":
    print(f"\nRender successful!")
    print(f"Output file: {result.data.get('output_file', 'Check user-data/')}")
    if 'permanent_script_path' in result.data:
        print(f"Script saved: {result.data['permanent_script_path']}")
else:
    print(f"\nRender failed: {result.error}")
    if result.data:
        print("\nError details:")
        print(result.data.get('stderr', ''))