#!/usr/bin/env python3
"""Create a simple animated movie using Manim Studio MCP interface"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.interfaces.mcp_interface import MCPInterface

async def create_simple_movie():
    """Create a simple animated movie with the specified requirements"""
    
    # Initialize the MCP interface
    mcp = MCPInterface()
    
    print("🎬 Creating simple animated movie...")
    
    # Step 1: Create a scene called "simple_movie" with duration 8 seconds and dark blue background
    print("\n1. Creating scene 'simple_movie'...")
    scene_result = await mcp.execute_tool("create_scene", {
        "name": "simple_movie",
        "duration": 8.0,
        "background_color": "#1e3a8a"  # Dark blue background
    })
    print(f"   Scene created: {scene_result.status}")
    if scene_result.status != "success":
        print(f"   Error: {scene_result.error}")
        return
    
    # Step 2: Add a title text "Welcome to Manim Studio!" at the top center
    print("\n2. Adding title text...")
    title_result = await mcp.execute_tool("add_text", {
        "id": "title",
        "content": "Welcome to Manim Studio!",
        "color": "#FFFFFF",
        "position": [0, 2.5, 0],  # Top center
        "font_size": 56
    })
    print(f"   Title added: {title_result.status}")
    if title_result.status != "success":
        print(f"   Error: {title_result.error}")
    
    # Step 3: Add a circle shape on the left side in red color
    print("\n3. Adding red circle on the left...")
    circle_result = await mcp.execute_tool("add_shape", {
        "id": "red_circle",
        "shape_type": "circle",
        "color": "#FF0000",  # Red color
        "size": 1.0,
        "position": [-4, 0, 0]  # Left side
    })
    print(f"   Circle added: {circle_result.status}")
    if circle_result.status != "success":
        print(f"   Error: {circle_result.error}")
    
    # Step 4: Add a square shape on the right side in blue color
    print("\n4. Adding blue square on the right...")
    square_result = await mcp.execute_tool("add_shape", {
        "id": "blue_square",
        "shape_type": "square",
        "color": "#0000FF",  # Blue color
        "size": 1.0,
        "position": [4, 0, 0]  # Right side
    })
    print(f"   Square added: {square_result.status}")
    if square_result.status != "success":
        print(f"   Error: {square_result.error}")
    
    # Step 5: Add animations
    print("\n5. Adding animations...")
    
    # Animation 1: Fade in the title text at the beginning
    print("   5a. Adding title fade-in animation...")
    title_anim = await mcp.execute_tool("add_animation", {
        "target": "title",
        "animation_type": "fade_in",
        "start_time": 0.0,
        "duration": 1.5,
        "easing": "ease_in_out"
    })
    print(f"      Title fade-in: {title_anim.status}")
    
    # Animation 2: Move the circle from left to right
    print("   5b. Adding circle movement animation...")
    circle_move = await mcp.execute_tool("add_animation", {
        "target": "red_circle",
        "animation_type": "move_to",
        "start_time": 1.0,
        "duration": 3.0,
        "easing": "ease_in_out",
        "properties": {
            "end_position": [4, -1.5, 0]  # Move to right side, lower position
        }
    })
    print(f"      Circle movement: {circle_move.status}")
    
    # Animation 3: Rotate the square 360 degrees
    print("   5c. Adding square rotation animation...")
    square_rotate = await mcp.execute_tool("add_animation", {
        "target": "blue_square",
        "animation_type": "rotate",
        "start_time": 2.0,
        "duration": 4.0,
        "easing": "linear",
        "properties": {
            "angle": 360  # Full rotation
        }
    })
    print(f"      Square rotation: {square_rotate.status}")
    
    # Animation 4: Fade out everything at the end
    print("   5d. Adding fade-out animations...")
    
    # Fade out title
    title_fadeout = await mcp.execute_tool("add_animation", {
        "target": "title",
        "animation_type": "fade_out",
        "start_time": 6.5,
        "duration": 1.5,
        "easing": "ease_in_out"
    })
    print(f"      Title fade-out: {title_fadeout.status}")
    
    # Fade out circle
    circle_fadeout = await mcp.execute_tool("add_animation", {
        "target": "red_circle", 
        "animation_type": "fade_out",
        "start_time": 6.5,
        "duration": 1.5,
        "easing": "ease_in_out"
    })
    print(f"      Circle fade-out: {circle_fadeout.status}")
    
    # Fade out square
    square_fadeout = await mcp.execute_tool("add_animation", {
        "target": "blue_square",
        "animation_type": "fade_out", 
        "start_time": 6.5,
        "duration": 1.5,
        "easing": "ease_in_out"
    })
    print(f"      Square fade-out: {square_fadeout.status}")
    
    # Step 6: Render the scene to "simple_movie.mp4" with high quality
    print("\n6. Rendering scene...")
    render_result = await mcp.execute_tool("render_scene", {
        "output_path": "simple_movie.mp4",
        "quality": "high",
        "preview": False,  # Don't auto-open preview
        "save_script": True
    })
    print(f"   Render result: {render_result.status}")
    
    if render_result.status == "success":
        print("\n🎉 Simple movie created successfully!")
        print(f"   Output file: simple_movie.mp4")
        if render_result.data and 'script_path' in render_result.data:
            print(f"   Script saved to: {render_result.data['script_path']}")
    else:
        print(f"\n❌ Rendering failed: {render_result.error}")
        if render_result.data and 'script_path' in render_result.data:
            print(f"   Script was saved to: {render_result.data['script_path']}")
            print("   You can run the script manually with: python [script_path]")
    
    return render_result

if __name__ == "__main__":
    # Run the simple movie creation
    result = asyncio.run(create_simple_movie())
    print(f"\n✅ Process completed with status: {result.status}")