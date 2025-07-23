# Manim Studio MCP Interface

This MCP (Model Context Protocol) interface enables AI assistants to create Manim animations through a structured API. The interface uses the shared features architecture for consistency with other Manim Studio interfaces (API, GUI).

## Architecture

The MCP interface is now part of the unified interface architecture:

- **Main Interface**: `src/interfaces/mcp_interface.py` - The primary MCP implementation
- **Shared Features**: `src/interfaces/shared_features.py` - Core functionality shared across all interfaces
- **Configuration**: `mcp_config.json` - MCP server configuration

## Installation

The MCP interface uses the main project dependencies. No separate installation is needed.

## Running the Server

```bash
# From project root
python src/interfaces/mcp_interface.py

# Or configure in Claude Desktop using the mcp_config.json
```

## Available Tools

### Scene Management
- `create_scene` - Create a new animation scene
- `list_scenes` - List all created scenes
- `get_scene` - Get scene configuration
- `export_scene` - Export scene as YAML configuration
- `import_scene` - Import scene from YAML configuration
- `clear_workspace` - Clear all scenes and reset

### Object Creation
- `add_text` - Add text with styling options
- `add_shape` - Add circles, rectangles, or polygons

### Animation
- `add_animation` - Animate objects (fade, write, move, scale, rotate)
- `add_effect` - Add visual effects (particles, magical circles, glow)

### Rendering
- `prepare_render` - Prepare scene for rendering (generates script only)
  - Scripts are automatically saved to `user-data/mcp-scripts/` with timestamps
  - Duplicate scripts are detected and not re-saved
  - Metadata files (.json) are created alongside each script
- `render_scene` - Complete rendering pipeline (prepare and execute)
  - Automatically runs the manim command to generate the video
  - Supports preview mode to open the video after rendering
  - Tracks rendering progress and captures output logs

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
      "args": ["/path/to/manim_studio/src/interfaces/mcp/server.py"]
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

## Script Recovery

All MCP-generated scripts are automatically saved to `user-data/mcp-scripts/`. To recover and use these scripts:

```bash
# List all saved scripts
python src/interfaces/recover_scripts.py

# Render a specific saved script
python src/interfaces/recover_scripts.py <number>
```

Each saved script has an accompanying JSON metadata file with scene configuration and rendering details.
