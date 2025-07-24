"""Neovim Plugin for Manim Studio Integration

Provides Neovim-specific functionality for Manim Studio including:
- Plugin configuration and setup
- Keybinding management
- Command definitions
- Integration with LSP server
"""

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import shared features
from src.interfaces.shared import (
    ManimStudioCore, 
    AnimationType, 
    ShapeType, 
    RenderQuality,
    InterfaceResult
)

logger = logging.getLogger(__name__)


class NeovimPlugin:
    """Neovim plugin interface for Manim Studio."""
    
    def __init__(self):
        from src.interfaces.shared import shared_core
        self.core = shared_core
        self.plugin_config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default plugin configuration."""
        return {
            "lsp": {
                "enabled": True,
                "server_cmd": ["python", "-m", "src.interfaces.nvim.lsp_server"],
                "filetypes": ["yaml"],
                "root_patterns": [".git", "CLAUDE.md", "manim_studio.yaml"]
            },
            "keybindings": {
                "render_scene": "<leader>mr",
                "preview_scene": "<leader>mp", 
                "validate_yaml": "<leader>mv",
                "toggle_preview": "<leader>mt",
                "insert_object": "<leader>mo",
                "insert_animation": "<leader>ma"
            },
            "commands": {
                "ManimRender": "render current scene",
                "ManimPreview": "preview current scene",
                "ManimValidate": "validate YAML",
                "ManimInsertObject": "insert object template",
                "ManimInsertAnimation": "insert animation template",
                "ManimTogglePreview": "toggle live preview"
            },
            "preview": {
                "enabled": True,
                "auto_render": False,
                "quality": "low",
                "update_delay": 2000  # ms
            }
        }
    
    def generate_nvim_config(self) -> str:
        """Generate Neovim configuration in Lua."""
        config = f"""-- Manim Studio Neovim Plugin Configuration
-- Generated automatically - customize as needed

local M = {{}}

-- Plugin configuration
M.config = {json.dumps(self.plugin_config, indent=2)}

-- Setup LSP
function M.setup_lsp()
  local lspconfig = require('lspconfig')
  
  -- Register Manim Studio LSP
  local configs = require('lspconfig.configs')
  
  if not configs.manim_studio_lsp then
    configs.manim_studio_lsp = {{
      default_config = {{
        cmd = {json.dumps(self.plugin_config['lsp']['server_cmd'])},
        filetypes = {json.dumps(self.plugin_config['lsp']['filetypes'])},
        root_dir = function(fname)
          return lspconfig.util.root_pattern(unpack({json.dumps(self.plugin_config['lsp']['root_patterns'])}))(fname)
            or lspconfig.util.find_git_ancestor(fname)
            or vim.fn.getcwd()
        end,
        settings = {{}},
        init_options = {{
          manim_studio = {{
            version = "0.1.0"
          }}
        }}
      }},
    }}
  end
  
  -- Setup the LSP
  lspconfig.manim_studio_lsp.setup({{
    on_attach = function(client, bufnr)
      -- Enable completion triggered by <c-x><c-o>
      vim.api.nvim_buf_set_option(bufnr, 'omnifunc', 'v:lua.vim.lsp.omnifunc')
      
      -- Mappings
      local bufopts = {{ noremap=true, silent=true, buffer=bufnr }}
      vim.keymap.set('n', 'gD', vim.lsp.buf.declaration, bufopts)
      vim.keymap.set('n', 'gd', vim.lsp.buf.definition, bufopts)
      vim.keymap.set('n', 'K', vim.lsp.buf.hover, bufopts)
      vim.keymap.set('n', '<C-k>', vim.lsp.buf.signature_help, bufopts)
      vim.keymap.set('n', '<space>rn', vim.lsp.buf.rename, bufopts)
      vim.keymap.set('n', '<space>ca', vim.lsp.buf.code_action, bufopts)
      vim.keymap.set('n', 'gr', vim.lsp.buf.references, bufopts)
      vim.keymap.set('n', '<space>f', function() vim.lsp.buf.format {{ async = true }} end, bufopts)
    end,
    flags = {{
      debounce_text_changes = 150,
    }},
    capabilities = require('cmp_nvim_lsp').default_capabilities()
  }})
end

-- Setup keybindings
function M.setup_keybindings()
  local keybindings = M.config.keybindings
  
  -- Render current scene
  vim.keymap.set('n', keybindings.render_scene, function()
    M.render_current_scene()
  end, {{ desc = 'Render current Manim scene' }})
  
  -- Preview current scene
  vim.keymap.set('n', keybindings.preview_scene, function()
    M.preview_current_scene()
  end, {{ desc = 'Preview current Manim scene' }})
  
  -- Validate YAML
  vim.keymap.set('n', keybindings.validate_yaml, function()
    M.validate_current_file()
  end, {{ desc = 'Validate Manim YAML' }})
  
  -- Toggle preview
  vim.keymap.set('n', keybindings.toggle_preview, function()
    M.toggle_live_preview()
  end, {{ desc = 'Toggle live preview' }})
  
  -- Insert object template
  vim.keymap.set('n', keybindings.insert_object, function()
    M.insert_object_template()
  end, {{ desc = 'Insert object template' }})
  
  -- Insert animation template
  vim.keymap.set('n', keybindings.insert_animation, function()
    M.insert_animation_template()
  end, {{ desc = 'Insert animation template' }})
end

-- Setup commands
function M.setup_commands()
  local commands = M.config.commands
  
  -- Render command
  vim.api.nvim_create_user_command('ManimRender', function(opts)
    local quality = opts.args ~= "" and opts.args or "medium"
    M.render_current_scene(quality)
  end, {{
    nargs = '?',
    complete = function()
      return {{'low', 'medium', 'high', 'ultra'}}
    end,
    desc = commands.ManimRender
  }})
  
  -- Preview command
  vim.api.nvim_create_user_command('ManimPreview', function()
    M.preview_current_scene()
  end, {{ desc = commands.ManimPreview }})
  
  -- Validate command
  vim.api.nvim_create_user_command('ManimValidate', function()
    M.validate_current_file()
  end, {{ desc = commands.ManimValidate }})
  
  -- Insert object command
  vim.api.nvim_create_user_command('ManimInsertObject', function(opts)
    local object_type = opts.args ~= "" and opts.args or nil
    M.insert_object_template(object_type)
  end, {{
    nargs = '?',
    complete = function()
      return {{'text', 'circle', 'square', 'triangle', 'rectangle'}}
    end,
    desc = commands.ManimInsertObject
  }})
  
  -- Insert animation command
  vim.api.nvim_create_user_command('ManimInsertAnimation', function(opts)
    local anim_type = opts.args ~= "" and opts.args or nil
    M.insert_animation_template(anim_type)
  end, {{
    nargs = '?',
    complete = function()
      return {{'fadein', 'fadeout', 'move', 'scale', 'rotate'}}
    end,
    desc = commands.ManimInsertAnimation
  }})
  
  -- Toggle preview command
  vim.api.nvim_create_user_command('ManimTogglePreview', function()
    M.toggle_live_preview()
  end, {{ desc = commands.ManimTogglePreview }})
end

-- Core functions
function M.render_current_scene(quality)
  quality = quality or M.config.preview.quality
  local filepath = vim.fn.expand('%:p')
  
  if not filepath or filepath == '' then
    vim.notify('No file open', vim.log.levels.ERROR)
    return
  end
  
  -- Create temporary output path
  local temp_dir = vim.fn.tempname()
  vim.fn.mkdir(temp_dir, 'p')
  local output_path = temp_dir .. '/rendered_scene.mp4'
  
  -- Call Python rendering function
  local cmd = {{
    'python', '-c',
    string.format([[
import sys
sys.path.insert(0, '%s')
from src.interfaces.nvim.plugin import render_yaml_file
result = render_yaml_file('%s', '%s', '%s')
print(result)
    ]], vim.fn.getcwd(), filepath, output_path, quality)
  }}
  
  vim.fn.jobstart(cmd, {{
    on_stdout = function(_, data)
      if data and #data > 0 then
        for _, line in ipairs(data) do
          if line ~= '' then
            vim.notify('Render: ' .. line, vim.log.levels.INFO)
          end
        end
      end
    end,
    on_stderr = function(_, data)
      if data and #data > 0 then
        for _, line in ipairs(data) do
          if line ~= '' then
            vim.notify('Render Error: ' .. line, vim.log.levels.ERROR)
          end
        end
      end
    end,
    on_exit = function(_, code)
      if code == 0 then
        vim.notify('Render completed: ' .. output_path, vim.log.levels.INFO)
        -- Optionally open the video
        if vim.fn.has('mac') == 1 then
          vim.fn.system('open "' .. output_path .. '"')
        end
      else
        vim.notify('Render failed with code: ' .. code, vim.log.levels.ERROR)
      end
    end
  }})
end

function M.preview_current_scene()
  M.render_current_scene('low')  -- Use low quality for fast preview
end

function M.validate_current_file()
  local filepath = vim.fn.expand('%:p')
  
  if not filepath or filepath == '' then
    vim.notify('No file open', vim.log.levels.ERROR)
    return
  end
  
  -- Call Python validation function
  local cmd = {{
    'python', '-c',
    string.format([[
import sys
sys.path.insert(0, '%s')
from src.interfaces.nvim.plugin import validate_yaml_file
result = validate_yaml_file('%s')
print(result)
    ]], vim.fn.getcwd(), filepath)
  }}
  
  vim.fn.jobstart(cmd, {{
    on_stdout = function(_, data)
      if data and #data > 0 then
        for _, line in ipairs(data) do
          if line ~= '' then
            vim.notify('Validation: ' .. line, vim.log.levels.INFO)
          end
        end
      end
    end,
    on_stderr = function(_, data)
      if data and #data > 0 then
        for _, line in ipairs(data) do
          if line ~= '' then
            vim.notify('Validation Error: ' .. line, vim.log.levels.ERROR)
          end
        end
      end
    end
  }})
end

function M.insert_object_template(object_type)
  object_type = object_type or 'circle'
  
  local template = string.format([[  - id: %s_1
    type: %s
    position: [0, 0, 0]
    color: "#FFFFFF"
    size: 1.0]], object_type, object_type)
  
  -- Insert at cursor
  local cursor = vim.api.nvim_win_get_cursor(0)
  local lines = vim.split(template, '\\n')
  vim.api.nvim_buf_set_lines(0, cursor[1], cursor[1], false, lines)
  
  vim.notify('Inserted ' .. object_type .. ' template', vim.log.levels.INFO)
end

function M.insert_animation_template(anim_type)
  anim_type = anim_type or 'fadein'
  
  local template = string.format([[  - target: object_id
    type: %s
    start_time: 0.0
    duration: 1.0
    easing: ease_in_out]], anim_type)
  
  -- Insert at cursor
  local cursor = vim.api.nvim_win_get_cursor(0)
  local lines = vim.split(template, '\\n')
  vim.api.nvim_buf_set_lines(0, cursor[1], cursor[1], false, lines)
  
  vim.notify('Inserted ' .. anim_type .. ' animation template', vim.log.levels.INFO)
end

-- Live preview toggle (placeholder for future implementation)
function M.toggle_live_preview()
  -- TODO: Implement live preview functionality
  vim.notify('Live preview toggle - not yet implemented', vim.log.levels.WARN)
end

-- Setup function
function M.setup(opts)
  opts = opts or {{}}
  
  -- Merge user configuration
  M.config = vim.tbl_deep_extend('force', M.config, opts)
  
  -- Only setup if we're in a Manim Studio project
  if vim.fn.findfile('CLAUDE.md', '.;') ~= '' or 
     vim.fn.finddir('.git', '.;') ~= '' then
    
    if M.config.lsp.enabled then
      M.setup_lsp()
    end
    
    M.setup_keybindings()
    M.setup_commands()
    
    vim.notify('Manim Studio plugin loaded', vim.log.levels.INFO)
  end
end

return M"""
        
        return config
    
    def generate_plugin_files(self, plugin_dir: Optional[Path] = None) -> Dict[str, str]:
        """Generate all plugin files for Neovim."""
        if plugin_dir is None:
            plugin_dir = Path.home() / ".config" / "nvim" / "lua" / "manim_studio"
        
        plugin_dir = Path(plugin_dir)
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = {}
        
        # Main plugin file
        init_lua = plugin_dir / "init.lua"
        init_lua.write_text(self.generate_nvim_config())
        files_created["init.lua"] = str(init_lua)
        
        # Plugin spec for lazy.nvim
        plugin_spec = self._generate_lazy_spec()
        spec_file = plugin_dir / "lazy_spec.lua"
        spec_file.write_text(plugin_spec)
        files_created["lazy_spec.lua"] = str(spec_file)
        
        # Installation instructions
        readme = self._generate_readme()
        readme_file = plugin_dir / "README.md"
        readme_file.write_text(readme)
        files_created["README.md"] = str(readme_file)
        
        return files_created
    
    def _generate_lazy_spec(self) -> str:
        """Generate lazy.nvim plugin specification."""
        return '''-- Lazy.nvim plugin specification for Manim Studio
-- Add this to your lazy.nvim setup

return {
  -- Core LSP support
  {
    "neovim/nvim-lspconfig",
    config = function()
      require("manim_studio").setup()
    end,
    ft = {"yaml"},
    cond = function()
      -- Only load in Manim Studio projects
      return vim.fn.findfile('CLAUDE.md', '.;') ~= '' or
             vim.fn.finddir('.git', '.;') ~= ''
    end
  },
  
  -- Optional: Enhanced completion
  {
    "hrsh7th/nvim-cmp",
    dependencies = {
      "hrsh7th/cmp-nvim-lsp",
      "hrsh7th/cmp-buffer",
      "hrsh7th/cmp-path",
    },
    opts = function(_, opts)
      local cmp = require("cmp")
      opts.sources = cmp.config.sources(vim.list_extend(opts.sources or {}, {
        { name = "nvim_lsp" },
        { name = "buffer" },
        { name = "path" },
      }))
    end
  },
  
  -- Optional: File tree integration
  {
    "nvim-tree/nvim-tree.lua",
    opts = function(_, opts)
      opts.filters = opts.filters or {}
      opts.filters.custom = vim.list_extend(opts.filters.custom or {}, {
        "user-data",  -- Hide Manim output directory
        ".DS_Store"
      })
    end
  }
}'''
    
    def _generate_readme(self) -> str:
        """Generate README with installation instructions."""
        return '''# Manim Studio Neovim Plugin

Neovim integration for Manim Studio providing LSP support, YAML validation, and rendering commands.

## Features

- **LSP Integration**: Syntax highlighting, completion, and validation for Manim YAML files
- **Rendering Commands**: Render scenes directly from Neovim
- **Live Preview**: Quick preview of animations (low quality for speed)
- **Template Insertion**: Insert object and animation templates
- **Keybindings**: Convenient shortcuts for common operations

## Installation

### Prerequisites

1. Neovim 0.8+ with LSP support
2. Python 3.8+ with Manim Studio installed
3. The `pygls` package: `pip install pygls`

### Using lazy.nvim

Add to your `lazy.nvim` configuration:

```lua
{
  "manim-studio",
  dir = "~/.config/nvim/lua/manim_studio",
  config = function()
    require("manim_studio").setup({
      -- Optional: customize configuration
      keybindings = {
        render_scene = "<leader>mr",
        preview_scene = "<leader>mp",
      },
      preview = {
        quality = "low",
        auto_render = false
      }
    })
  end,
  ft = {"yaml"},
  cond = function()
    return vim.fn.findfile('CLAUDE.md', '.;') ~= ''
  end
}
```

### Manual Installation

1. Copy the plugin files to `~/.config/nvim/lua/manim_studio/`
2. Add to your `init.lua`:

```lua
require("manim_studio").setup()
```

## Usage

### Keybindings (default)

- `<leader>mr` - Render current scene
- `<leader>mp` - Preview current scene (low quality)
- `<leader>mv` - Validate YAML file
- `<leader>mt` - Toggle live preview
- `<leader>mo` - Insert object template
- `<leader>ma` - Insert animation template

### Commands

- `:ManimRender [quality]` - Render scene with specified quality
- `:ManimPreview` - Quick preview render
- `:ManimValidate` - Validate current YAML file
- `:ManimInsertObject [type]` - Insert object template
- `:ManimInsertAnimation [type]` - Insert animation template
- `:ManimTogglePreview` - Toggle live preview mode

### LSP Features

When editing `.yaml` files in a Manim Studio project:

- **Completion**: Auto-complete for object types, animation types, properties
- **Hover**: Documentation on hover for properties and values
- **Diagnostics**: Real-time validation and error reporting
- **Formatting**: Automatic YAML formatting

## Configuration

Default configuration options:

```lua
{
  lsp = {
    enabled = true,
    server_cmd = {"python", "-m", "src.interfaces.nvim.lsp_server"},
    filetypes = {"yaml"},
    root_patterns = {".git", "CLAUDE.md", "manim_studio.yaml"}
  },
  keybindings = {
    render_scene = "<leader>mr",
    preview_scene = "<leader>mp",
    validate_yaml = "<leader>mv",
    toggle_preview = "<leader>mt",
    insert_object = "<leader>mo",
    insert_animation = "<leader>ma"
  },
  preview = {
    enabled = true,
    auto_render = false,
    quality = "low",
    update_delay = 2000
  }
}
```

## Troubleshooting

### LSP Not Starting

1. Check that `pygls` is installed: `pip install pygls`
2. Verify Python path in LSP configuration
3. Check that you're in a Manim Studio project directory

### Rendering Errors

1. Ensure Manim Studio is properly installed
2. Check that the YAML file is valid
3. Verify output directory permissions

### Performance Issues

1. Use "low" quality for previews
2. Disable auto-render if enabled
3. Increase update delay for live preview

## Development

To extend the plugin:

1. Modify `init.lua` for new features
2. Update LSP server in `lsp_server.py` for language features
3. Add new commands and keybindings as needed

## License

Part of the Manim Studio project.
'''
    
    # Python utility functions for Neovim integration
    def render_yaml_file(self, filepath: str, output_path: str, quality: str = "medium") -> str:
        """Render a YAML file to video (called from Neovim)."""
        try:
            # Import scene from YAML
            with open(filepath, 'r') as f:
                yaml_content = yaml.safe_load(f)
            
            # Import the scene
            import_result = self.core.import_scene(yaml_content)
            if import_result.status != "success":
                return f"Error importing scene: {import_result.error}"
            
            # Render the scene
            render_result = self.core.render_scene(
                output_path=output_path,
                quality=quality,
                preview=False,
                save_script=True
            )
            
            if render_result.status == "success":
                return f"Render completed: {output_path}"
            else:
                return f"Render failed: {render_result.error}"
                
        except Exception as e:
            logger.error(f"Error rendering YAML file: {e}")
            return f"Error: {str(e)}"
    
    def validate_yaml_file(self, filepath: str) -> str:
        """Validate a YAML file (called from Neovim)."""
        try:
            # Try to import the YAML validator
            try:
                from src.core.yaml_validator import YAMLValidator
                validator = YAMLValidator()
                
                # Validate the file
                result = validator.validate_file(filepath)
                
                if result['valid']:
                    return "YAML is valid"
                else:
                    errors = len(result.get('errors', []))
                    warnings = len(result.get('warnings', []))
                    return f"Validation failed: {errors} errors, {warnings} warnings"
                    
            except ImportError:
                # Fallback to basic YAML parsing
                with open(filepath, 'r') as f:
                    yaml.safe_load(f)
                return "YAML syntax is valid (basic validation)"
                
        except Exception as e:
            logger.error(f"Error validating YAML file: {e}")
            return f"Validation error: {str(e)}"


# Standalone functions for Neovim integration
def render_yaml_file(filepath: str, output_path: str, quality: str = "medium") -> str:
    """Standalone function for rendering YAML files from Neovim."""
    plugin = NeovimPlugin()
    return plugin.render_yaml_file(filepath, output_path, quality)


def validate_yaml_file(filepath: str) -> str:
    """Standalone function for validating YAML files from Neovim."""
    plugin = NeovimPlugin()
    return plugin.validate_yaml_file(filepath)


def generate_plugin_config(output_dir: Optional[str] = None) -> Dict[str, str]:
    """Generate Neovim plugin configuration files."""
    plugin = NeovimPlugin()
    
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path.home() / ".config" / "nvim" / "lua" / "manim_studio"
    
    return plugin.generate_plugin_files(output_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python plugin.py <command> [args...]")
        print("Commands:")
        print("  generate [output_dir] - Generate plugin files")
        print("  render <yaml_file> <output_file> [quality] - Render YAML file")
        print("  validate <yaml_file> - Validate YAML file")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "generate":
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        files = generate_plugin_config(output_dir)
        print("Generated plugin files:")
        for name, path in files.items():
            print(f"  {name}: {path}")
    
    elif command == "render":
        if len(sys.argv) < 4:
            print("Usage: python plugin.py render <yaml_file> <output_file> [quality]")
            sys.exit(1)
        
        yaml_file = sys.argv[2]
        output_file = sys.argv[3]
        quality = sys.argv[4] if len(sys.argv) > 4 else "medium"
        
        result = render_yaml_file(yaml_file, output_file, quality)
        print(result)
    
    elif command == "validate":
        if len(sys.argv) < 3:
            print("Usage: python plugin.py validate <yaml_file>")
            sys.exit(1)
        
        yaml_file = sys.argv[2]
        result = validate_yaml_file(yaml_file)
        print(result)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)