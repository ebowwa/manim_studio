# Neovim Interface for Manim Studio

This directory contains the Neovim integration for Manim Studio, providing a comprehensive development environment for creating animations with YAML configurations.

## Components

### 1. LSP Server (`lsp_server.py`)
Language Server Protocol implementation providing:
- **Syntax validation** for YAML scene files
- **Auto-completion** for object types, animation types, and properties
- **Hover documentation** for configuration options
- **Real-time error checking** and diagnostics

### 2. Plugin Configuration (`plugin.py`)
Neovim plugin generator providing:
- **Keybinding setup** for common operations
- **Command definitions** for rendering and validation
- **Integration scripts** for seamless workflow
- **Configuration management** for plugin customization

### 3. Buffer Manager (`buffer_manager.py`)
Buffer synchronization and live preview system:
- **Real-time buffer tracking** and change detection
- **Auto-rendering** with configurable delays
- **Live preview** generation for quick feedback
- **Validation callbacks** for error reporting

## Quick Start

### 1. Install Dependencies
```bash
pip install pygls  # For LSP functionality
```

### 2. Generate Plugin Files
```bash
# From the project root
python -m src.interfaces.cli.cli --interface nvim-plugin
```

This creates plugin files in `~/.config/nvim/lua/manim_studio/`

### 3. Configure Neovim

Add to your Neovim configuration (lazy.nvim example):
```lua
{
  "manim-studio",
  dir = "~/.config/nvim/lua/manim_studio",
  config = function()
    require("manim_studio").setup()
  end,
  ft = {"yaml"},
  cond = function()
    return vim.fn.findfile('CLAUDE.md', '.;') ~= ''
  end
}
```

### 4. Start LSP Server

The LSP server starts automatically when editing YAML files in a Manim Studio project, or manually:
```bash
python -m src.interfaces.cli.cli --interface nvim-lsp
```

## Features

### LSP Features
- **Auto-completion** for:
  - Object types (circle, square, text, etc.)
  - Animation types (fadein, fadeout, move, scale, etc.)
  - Properties (position, color, duration, easing)
  - Easing functions (linear, ease_in_out, bounce, etc.)

- **Hover documentation** for all configuration options
- **Real-time validation** with error highlighting
- **Diagnostics** showing line-specific errors and warnings

### Plugin Commands
- `:ManimRender [quality]` - Render current scene
- `:ManimPreview` - Quick low-quality preview
- `:ManimValidate` - Validate YAML configuration
- `:ManimInsertObject [type]` - Insert object template
- `:ManimInsertAnimation [type]` - Insert animation template

### Default Keybindings
- `<leader>mr` - Render scene
- `<leader>mp` - Preview scene
- `<leader>mv` - Validate YAML
- `<leader>mt` - Toggle live preview
- `<leader>mo` - Insert object template
- `<leader>ma` - Insert animation template

## Configuration

### Plugin Configuration
```lua
require("manim_studio").setup({
  lsp = {
    enabled = true,
    filetypes = {"yaml"},
  },
  keybindings = {
    render_scene = "<leader>mr",
    preview_scene = "<leader>mp",
  },
  preview = {
    quality = "low",
    auto_render = false,
    update_delay = 2000  -- ms
  }
})
```

### LSP Server Options
The LSP server can be started in different modes:
```bash
# Stdio (default for editors)
python -m src.interfaces.nvim.lsp_server

# TCP mode for debugging
python -m src.interfaces.nvim.lsp_server --tcp localhost 8088
```

## Architecture

```
src/interfaces/nvim/
├── __init__.py           # Module exports
├── lsp_server.py         # LSP implementation
├── plugin.py             # Neovim plugin generator
├── buffer_manager.py     # Buffer and preview management
└── README.md            # This file
```

### Integration with Shared Components

The Neovim interface leverages the shared architecture:
- Uses `shared_core` for scene management and rendering
- Integrates with YAML validator for real-time validation
- Follows the same patterns as MCP, GUI, and API interfaces

## Usage Examples

### Basic Workflow
1. Open a YAML scene file in Neovim
2. Get auto-completion as you type object and animation definitions
3. Use `<leader>mv` to validate your configuration
4. Use `<leader>mp` for quick preview
5. Use `<leader>mr` for final render

### Advanced Usage
```lua
-- Custom configuration
require("manim_studio").setup({
  preview = {
    auto_render = true,  -- Enable auto-rendering
    quality = "medium",  -- Higher quality previews
    update_delay = 1000  -- Faster response
  }
})
```

### Buffer Manager Integration
```python
from src.interfaces.nvim.buffer_manager import BufferManager

# Create manager with auto-render
manager = BufferManager(auto_render=True, render_delay=2.0)

# Register a file
buffer_state = manager.register_buffer("scene.yaml")

# Update content (triggers validation and optional render)
manager.update_buffer("scene.yaml", updated_content)
```

## Troubleshooting

### LSP Not Starting
1. Check `pygls` installation: `pip install pygls`
2. Verify Python path in LSP configuration
3. Ensure you're in a Manim Studio project directory

### Completion Not Working
1. Restart LSP: `:LspRestart`
2. Check LSP status: `:LspInfo`
3. Verify file type detection: `:set ft?`

### Rendering Issues
1. Check YAML validation first
2. Verify Manim Studio installation
3. Check output directory permissions

### Performance Issues
1. Disable auto-render for large files
2. Use "low" quality for previews
3. Increase render delay

## Development

### Adding New LSP Features
1. Extend completion providers in `lsp_server.py`
2. Add hover documentation for new properties
3. Update validation in buffer manager

### Adding New Plugin Commands
1. Add command definition in `plugin.py`
2. Implement corresponding Lua function
3. Add keybinding if needed

### Testing
```bash
# Test LSP server
python -m src.interfaces.nvim.lsp_server --tcp

# Test plugin generation
python -m src.interfaces.nvim.plugin generate

# Test buffer manager
python -m src.interfaces.nvim.buffer_manager scene.yaml
```

## Integration with Other Interfaces

The Neovim interface works alongside other Manim Studio interfaces:
- **MCP**: Use MCP for programmatic scene creation, Neovim for manual editing
- **GUI**: Use GUI for visual scene building, Neovim for fine-tuning
- **API**: Use API for external integrations, Neovim for development

## Future Enhancements

Planned features:
- **Snippet support** for common animation patterns
- **Live preview pane** within Neovim
- **Debugging support** for animation sequences
- **Integration with Git** for version control
- **Collaborative editing** features
- **Performance profiling** for complex scenes

## Contributing

When contributing to the Neovim interface:
1. Follow the shared architecture patterns
2. Update both Python and Lua components
3. Add tests for new features
4. Update documentation
5. Consider backward compatibility