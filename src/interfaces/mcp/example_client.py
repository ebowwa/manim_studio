"""Example MCP client for Manim Studio - demonstrates how to use the MCP server."""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def create_animated_logo():
    """Example: Create an animated logo with particles."""
    
    server_params = StdioServerParameters(
        command="python",
        args=["../mcp_interface.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # Create a new scene
            result = await session.call_tool(
                "create_scene",
                arguments={
                    "name": "AnimatedLogo",
                    "duration": 8.0,
                    "background_color": "#0a0a0a",
                    "resolution": [1920, 1080]
                }
            )
            print("Scene created:", result)
            
            # Add main logo text
            await session.call_tool(
                "add_text",
                arguments={
                    "id": "logo",
                    "text": "MANIM STUDIO",
                    "gradient": ["#FF6B6B", "#4ECDC4"],
                    "scale": 2.0,
                    "weight": "BOLD",
                    "position": [0, 0, 0]
                }
            )
            
            # Add subtitle
            await session.call_tool(
                "add_text",
                arguments={
                    "id": "subtitle",
                    "text": "Powered by MCP",
                    "color": "#FFFFFF",
                    "scale": 0.8,
                    "position": [0, -1.5, 0]
                }
            )
            
            # Add background circle
            await session.call_tool(
                "add_shape",
                arguments={
                    "id": "bg_circle",
                    "shape": "circle",
                    "radius": 3.0,
                    "color": "#4ECDC4",
                    "fill_color": "#4ECDC4",
                    "fill_opacity": 0.1,
                    "position": [0, 0, -1]
                }
            )
            
            # Animate logo entrance
            await session.call_tool(
                "add_animation",
                arguments={
                    "target": "logo",
                    "animation_type": "write",
                    "start_time": 0.5,
                    "duration": 2.0
                }
            )
            
            # Animate subtitle
            await session.call_tool(
                "add_animation",
                arguments={
                    "target": "subtitle",
                    "animation_type": "fadein",
                    "start_time": 2.0,
                    "duration": 1.0,
                    "params": {"shift": [0, 0.5, 0]}
                }
            )
            
            # Animate background circle
            await session.call_tool(
                "add_animation",
                arguments={
                    "target": "bg_circle",
                    "animation_type": "create",
                    "start_time": 0.0,
                    "duration": 1.5
                }
            )
            
            # Add particle effect
            await session.call_tool(
                "add_effect",
                arguments={
                    "type": "particle_system",
                    "start_time": 2.5,
                    "duration": 5.0,
                    "params": {
                        "position": [0, 0, 0],
                        "particle_count": 50,
                        "emit_rate": 20
                    }
                }
            )
            
            # Add magical circle effect
            await session.call_tool(
                "add_effect",
                arguments={
                    "type": "magical_circle",
                    "start_time": 3.0,
                    "duration": 4.0,
                    "params": {
                        "position": [0, 0, -0.5],
                        "radius": 2.5,
                        "rings": 2
                    }
                }
            )
            
            # Scale animation at the end
            await session.call_tool(
                "add_animation",
                arguments={
                    "target": "logo",
                    "animation_type": "scale",
                    "start_time": 6.0,
                    "duration": 1.5,
                    "params": {"factor": 1.2}
                }
            )
            
            # Save the configuration
            save_result = await session.call_tool(
                "save_config",
                arguments={
                    "path": "animated_logo.json"
                }
            )
            print("Configuration saved:", save_result)
            
            # Render the scene
            render_result = await session.call_tool(
                "prepare_render",
                arguments={
                    "output_path": "animated_logo.mp4",
                    "quality": "high"
                }
            )
            print("Render complete:", render_result)

async def create_data_visualization():
    """Example: Create a data visualization animation."""
    
    server_params = StdioServerParameters(
        command="python",
        args=["../mcp_interface.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Create scene
            await session.call_tool(
                "create_scene",
                arguments={
                    "name": "DataViz",
                    "duration": 10.0,
                    "background_color": "#1a1a1a"
                }
            )
            
            # Add title
            await session.call_tool(
                "add_text",
                arguments={
                    "id": "title",
                    "text": "Sales Data 2024",
                    "color": "#FFFFFF",
                    "scale": 1.2,
                    "position": [0, 3, 0]
                }
            )
            
            # Create bar chart bars
            data = [("Q1", 0.7, "#FF6B6B"), ("Q2", 0.9, "#4ECDC4"), 
                    ("Q3", 0.6, "#95E1D3"), ("Q4", 1.0, "#F38181")]
            
            for i, (label, height, color) in enumerate(data):
                x_pos = -3 + i * 2
                
                # Add bar
                await session.call_tool(
                    "add_shape",
                    arguments={
                        "id": f"bar_{label}",
                        "shape": "rectangle",
                        "width": 1.5,
                        "height": height * 3,
                        "color": color,
                        "fill_color": color,
                        "fill_opacity": 0.8,
                        "position": [x_pos, -1 + (height * 3) / 2, 0]
                    }
                )
                
                # Add label
                await session.call_tool(
                    "add_text",
                    arguments={
                        "id": f"label_{label}",
                        "text": label,
                        "color": "#FFFFFF",
                        "scale": 0.6,
                        "position": [x_pos, -2.5, 0]
                    }
                )
                
                # Animate bar
                await session.call_tool(
                    "add_animation",
                    arguments={
                        "target": f"bar_{label}",
                        "animation_type": "create",
                        "start_time": 1.0 + i * 0.5,
                        "duration": 1.0
                    }
                )
                
                # Animate label
                await session.call_tool(
                    "add_animation",
                    arguments={
                        "target": f"label_{label}",
                        "animation_type": "fadein",
                        "start_time": 1.5 + i * 0.5,
                        "duration": 0.5
                    }
                )
            
            # Animate title
            await session.call_tool(
                "add_animation",
                arguments={
                    "target": "title",
                    "animation_type": "write",
                    "start_time": 0.0,
                    "duration": 1.0
                }
            )
            
            # Render
            await session.call_tool(
                "prepare_render",
                arguments={
                    "output_path": "data_visualization.mp4",
                    "quality": "high"
                }
            )

async def main():
    """Run example animations."""
    print("Creating Animated Logo...")
    await create_animated_logo()
    
    print("\nCreating Data Visualization...")
    await create_data_visualization()
    
    print("\nAll examples completed!")

if __name__ == "__main__":
    asyncio.run(main())