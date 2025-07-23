#!/usr/bin/env python3
"""Example of using the MCP interface directly to create animations"""

from src.config.manim_config import config
import asyncio
from src.interfaces.mcp_interface import MCPInterface

async def create_example_animation():
    # Initialize the MCP interface
    mcp = MCPInterface()
    
    # Create a new scene
    print("Creating scene...")
    scene_result = await mcp.execute_tool("create_scene", {
        "name": "MCPDemoScene",
        "duration": 10.0,
        "description": "A demo scene created with MCP interface"
    })
    print(f"Scene created: {scene_result.status}")
    
    # Add a title text
    print("\nAdding title text...")
    title_result = await mcp.execute_tool("add_text", {
        "scene_name": "MCPDemoScene",
        "content": "MCP Interface Demo",
        "id": "title",
        "font_size": 72,
        "color": "#FFD700",
        "gradient_colors": ["#FFD700", "#FF6B6B", "#4ECDC4"],
        "position": [0, 2, 0]
    })
    print(f"Title added: {title_result.status}")
    
    # Add a circle
    print("\nAdding circle...")
    circle_result = await mcp.execute_tool("add_shape", {
        "scene_name": "MCPDemoScene",
        "shape_type": "circle",
        "id": "main_circle",
        "size": 1.5,
        "color": "#4ECDC4",
        "position": [0, -0.5, 0]
    })
    print(f"Circle added: {circle_result.status}")
    
    # Add animations
    print("\nAdding animations...")
    
    # Animate title entrance
    anim1 = await mcp.execute_tool("add_animation", {
        "scene_name": "MCPDemoScene",
        "animation_type": "write",
        "target": "title",
        "start_time": 0.5,
        "duration": 2.0
    })
    print(f"Title animation added: {anim1.status}")
    
    # Animate circle entrance with fade
    anim2 = await mcp.execute_tool("add_animation", {
        "scene_name": "MCPDemoScene",
        "animation_type": "fadein",
        "target": "main_circle",
        "start_time": 2.0,
        "duration": 1.0
    })
    print(f"Circle fade animation added: {anim2.status}")
    
    # Scale up the circle
    anim3 = await mcp.execute_tool("add_animation", {
        "scene_name": "MCPDemoScene",
        "animation_type": "scale",
        "target": "main_circle",
        "properties": {"scale_factor": 1.5},
        "start_time": 3.5,
        "duration": 1.0
    })
    print(f"Circle scale animation added: {anim3.status}")
    
    # Add magical effect
    print("\nAdding magical effect...")
    effect_result = await mcp.execute_tool("add_effect", {
        "scene_name": "MCPDemoScene",
        "effect_type": "glow",
        "target": "main_circle",
        "color": "#FFD700",
        "intensity": 2.0,
        "start_time": 4.5,
        "duration": 2.0
    })
    print(f"Glow effect added: {effect_result.status}")
    
    # Prepare render script
    print("\nPreparing render script...")
    script_result = await mcp.execute_tool("prepare_render", {
        "scene_name": "MCPDemoScene",
        "output_path": "user-data/mcp-scripts/demo_scene.py"
    })
    print(f"Script prepared: {script_result.status}")
    
    # Export to YAML for reference
    print("\nExporting to YAML...")
    yaml_result = await mcp.execute_tool("export_scene", {
        "scene_name": "MCPDemoScene",
        "filepath": "user-data/mcp_demo_scene.yaml"
    })
    print(f"YAML exported: {yaml_result.status}")
    
    # Render the scene
    print("\nRendering scene...")
    render_result = await mcp.execute_tool("render_scene", {
        "scene_name": "MCPDemoScene",
        "quality": "low",
        "preview": True,
        "output_path": "user-data/mcp_demo_video.mp4"
    })
    print(f"Render complete: {render_result.status}")
    
    return script_result

if __name__ == "__main__":
    # Run the example
    result = asyncio.run(create_example_animation())
    print(f"\nExample complete! Script saved to: {result.get('script_path', 'Unknown')}")