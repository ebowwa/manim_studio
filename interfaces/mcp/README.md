# Manim Studio MCP Server

This MCP (Model Context Protocol) server enables AI assistants to create Manim animations through a structured API.

## Installation

```bash
cd interfaces/mcp
pip install -r requirements.txt
```

## Running the Server

```bash
python server.py
```

## Available Tools

### Scene Management
- `create_scene` - Create a new animation scene
- `list_scenes` - List all created scenes
- `get_scene` - Get scene configuration
- `save_config` - Save scene to JSON/YAML file

### Object Creation
- `add_text` - Add text with styling options
- `add_shape` - Add circles, rectangles, or polygons

### Animation
- `add_animation` - Animate objects (fade, write, move, scale, rotate)
- `add_effect` - Add visual effects (particles, magical circles, glow)

### Rendering
- `preview_scene` - Quick low-quality preview
- `render_scene` - Full quality render to video file

## Example Usage

```python
# Create a scene
await call_tool("create_scene", {
    "name": "HelloWorld",
    "duration": 5.0,
    "background_color": "#1a1a1a"
})

# Add text
await call_tool("add_text", {
    "id": "title",
    "text": "Hello, Manim!",
    "gradient": ["#FF6B6B", "#4ECDC4"],
    "scale": 1.5
})

# Animate the text
await call_tool("add_animation", {
    "target": "title",
    "animation_type": "write",
    "start_time": 0,
    "duration": 2.0
})

# Render the scene
await call_tool("render_scene", {
    "output_path": "hello_world.mp4",
    "quality": "high"
})
```

## Integration with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "manim-studio": {
      "command": "python",
      "args": ["/path/to/manim_studio/interfaces/mcp/server.py"]
    }
  }
}
```

## Advanced Features

### Particle Effects
```python
await call_tool("add_effect", {
    "type": "particle_system",
    "start_time": 2.0,
    "duration": 3.0,
    "params": {
        "position": [0, 0, 0],
        "particle_count": 100,
        "emit_rate": 30
    }
})
```

### Magical Circles
```python
await call_tool("add_effect", {
    "type": "magical_circle",
    "start_time": 1.0,
    "duration": 4.0,
    "params": {
        "position": [0, 0, 0],
        "radius": 2.0,
        "rings": 3
    }
})
```

### Text Effects
```python
# First add text
await call_tool("add_text", {
    "id": "sparkle_text",
    "text": "Magic!"
})

# Then add sparkle effect
await call_tool("add_effect", {
    "type": "sparkle_text",
    "start_time": 0.5,
    "duration": 2.0,
    "params": {
        "target": "sparkle_text"
    }
})
```