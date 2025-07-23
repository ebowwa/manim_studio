#!/usr/bin/env python3
"""Test script to interact with MCP interface directly"""

import asyncio
import json
import sys
import os

# Add project root to path
sys.path.insert(0, '/Users/ebowwa/apps/manim_studio')

from src.interfaces.mcp_interface import MCPInterface

async def create_simple_film():
    """Create a simple film using the MCP interface"""
    interface = MCPInterface()
    
    print("Creating simple film...")
    
    # Create scene
    result = await interface.execute_tool("create_scene", {
        "name": "simple_film",
        "duration": 8.0,
        "background_color": "#1a1a2e",
        "resolution": [1920, 1080],
        "fps": 30
    })
    print(f"Create scene: {result.status} - {result.message}")
    
    # Add title text
    result = await interface.execute_tool("add_text", {
        "id": "title",
        "content": "Welcome to Manim Studio!",
        "color": "#FFD700",
        "position": [0, 2, 0],
        "font_size": 64
    })
    print(f"Add title: {result.status} - {result.message}")
    
    # Add a circle
    result = await interface.execute_tool("add_shape", {
        "id": "circle1",
        "shape_type": "circle",
        "color": "#FF6B6B",
        "size": 1.5,
        "position": [-4, 0, 0]
    })
    print(f"Add circle: {result.status} - {result.message}")
    
    # Add a square
    result = await interface.execute_tool("add_shape", {
        "id": "square1", 
        "shape_type": "square",
        "color": "#4ECDC4",
        "size": 1.2,
        "position": [4, -1, 0]
    })
    print(f"Add square: {result.status} - {result.message}")
    
    # Add animations
    # Title fade in
    result = await interface.execute_tool("add_animation", {
        "target": "title",
        "animation_type": "fade_in",
        "start_time": 0.5,
        "duration": 1.0,
        "easing": "ease_out"
    })
    print(f"Title fade in: {result.status} - {result.message}")
    
    # Circle moves to center
    result = await interface.execute_tool("add_animation", {
        "target": "circle1",
        "animation_type": "move_to",
        "start_time": 2.0,
        "duration": 2.0,
        "easing": "ease_in_out",
        "properties": {"end_position": [0, 0, 0]}
    })
    print(f"Circle move: {result.status} - {result.message}")
    
    # Square rotation
    result = await interface.execute_tool("add_animation", {
        "target": "square1",
        "animation_type": "rotate",
        "start_time": 3.0,
        "duration": 2.0,
        "easing": "linear",
        "properties": {"angle": 360}
    })
    print(f"Square rotate: {result.status} - {result.message}")
    
    # Fade out all at end
    for obj_id in ["title", "circle1", "square1"]:
        result = await interface.execute_tool("add_animation", {
            "target": obj_id,
            "animation_type": "fade_out",
            "start_time": 6.5,
            "duration": 1.0,
            "easing": "ease_in"
        })
        print(f"Fade out {obj_id}: {result.status} - {result.message}")
    
    # Render the film
    output_path = "/Users/ebowwa/apps/manim_studio/user-data/simple_film.mp4"
    result = await interface.execute_tool("render_scene", {
        "output_path": output_path,
        "quality": "medium",
        "preview": False,
        "save_script": True
    })
    print(f"Render: {result.status} - {result.message}")
    
    if result.status == "success":
        print(f"🎬 Film created successfully at: {output_path}")
    else:
        print(f"❌ Render failed: {result.error}")

if __name__ == "__main__":
    asyncio.run(create_simple_film())