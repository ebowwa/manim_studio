#!/usr/bin/env python3
"""Simple test of MCP rendering"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.interfaces.shared_features import ManimStudioCore

# Create a simple animation
core = ManimStudioCore()

# Create scene
print("Creating scene...")
result = core.create_scene("simple_test", duration=3.0)
print(f"Scene created: {result.status}")

# Add text
print("\nAdding text...")
core.add_text("title", "MCP Works!", color="#FFD700", position=[0, 0, 0], font_size=72)

# Add simple fade in animation
print("\nAdding animation...")
core.add_animation("title", "fadein", start_time=0, duration=1.5)

# Render the scene
print("\nRendering scene...")
result = core.render_scene("user-data/simple_mcp_test.mp4", quality="low", save_script=True)

if result.status == "success":
    print(f"\nRender successful!")
    print(f"Output file: {result.data.get('output_file', 'Check user-data/')}")
    if 'permanent_script_path' in result.data:
        print(f"Script saved: {result.data['permanent_script_path']}")
else:
    print(f"\nRender failed: {result.error}")