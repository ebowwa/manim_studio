# Manim Studio - Project Guidelines for Claude

## MCP Script Preservation

All MCP-generated scripts are now automatically saved to prevent losing work. The system:

1. **Saves scripts permanently** to `/user-data/mcp-scripts/` with timestamps
2. **Avoids duplicates** by checking content hash before saving
3. **Creates metadata files** (.json) alongside each script with scene configuration
4. **Recovery tool** available at `interfaces/mcp/recover_scripts.py`:
   - List all saved scripts: `python interfaces/mcp/recover_scripts.py`
   - Render a specific script: `python interfaces/mcp/recover_scripts.py <number>`

## Important Configuration: Media Directory

All Manim output should be directed to the `user-data` directory, NOT the default `media` directory.

### How this is enforced:

1. **Python Config Module**: `src/config/manim_config.py`
   - This module must be imported BEFORE any Manim imports
   - It sets the media directory to `user-data`
   - All test files have been updated to import this first

2. **Shell Scripts**: 
   - All shell scripts that run manim commands must include `--media_dir user-data`
   - This includes render scripts in `developer/scripts/` and `developer/examples/`

3. **CLI Override**: 
   - The `manim-studio` CLI in `src/cli.py` sets `"media_dir": "user-data"` by default

### If you see media/ being created:
- Check that the file imports `from src.config.manim_config import config` before any Manim imports
- For shell scripts, ensure `--media_dir user-data` is included in the manim command
- The `media/` directory is already in `.gitignore` so it won't be committed


## Project Structure

- Main source code: `src/`
- Tests: `developer/tests/`
- Examples: `developer/examples/`
- Scripts: `developer/scripts/`
- User data output: `user-data/`
# Manim Studio - Rendering Instructions

## Quick Start

To render YAML scenes in Manim Studio, follow these steps:

### 1. Navigate to the Project Directory
```bash
cd /Users/ebowwa/apps/manim_studio
```

### 2. Activate the Virtual Environment
```bash
source venv/bin/activate
```

### 3. Render Your Scene
```bash
# Using the installed CLI command (requires pip install -e .)
manim-studio scenes/your_scene.yaml -q l -p

# OR run directly with Python (no installation needed)
python main.py scenes/your_scene.yaml -q l -p
```

## Command Options

### Basic Rendering
```bash
# Render with preview (opens video after rendering)
manim-studio scenes/complete_alchemy_story.yaml -q l -p
# OR: python main.py scenes/complete_alchemy_story.yaml -q l -p

# Render without preview (faster)
manim-studio scenes/complete_alchemy_story.yaml -q l
# OR: python main.py scenes/complete_alchemy_story.yaml -q l
```

### Quality Settings
- `-q l` - Low quality (480p) - fastest
- `-q m` - Medium quality (720p)
- `-q h` - High quality (1080p)
- `-q p` - Production quality (1440p)
- `-q k` - 4K quality - slowest

### Performance Options
```bash
# Reduce frame rate for faster rendering
manim-studio scenes/complete_alchemy_story.yaml -q l --fps 15
# OR: python main.py scenes/complete_alchemy_story.yaml -q l --fps 15

# Save with custom filename
manim-studio scenes/complete_alchemy_story.yaml -q l -o my_video.mp4
# OR: python main.py scenes/complete_alchemy_story.yaml -q l -o my_video.mp4
```

### Background Rendering
```bash
# Run in background and save output to log file
manim-studio scenes/complete_alchemy_story.yaml -q l > render.log 2>&1 &

# Check progress
tail -f render.log

# Find the process if needed
ps aux | grep manim-studio
```

## Using the Convenience Script

Instead of the full command, you can use the provided script:

```bash
# Make sure you're in the project directory
cd /Users/ebowwa/apps/manim_studio

# Run the script
./scripts/render_yaml_scene.sh scenes/complete_alchemy_story.yaml

# With specific quality
./scripts/render_yaml_scene.sh scenes/complete_alchemy_story.yaml SceneName high
```

## Available Example Scenes

- `scenes/lyras_alchemy.yaml` - Simple magical effects demo (15 seconds)
- `scenes/complete_alchemy_story.yaml` - Full story with chapters (2 minutes)
- `scenes/simple_demo.yaml` - Basic shapes and animations (30 seconds)
- `configs/example_scene.yaml` - Another example configuration

## Troubleshooting

### If rendering is taking too long:
1. Use lower quality: `-q l`
2. Reduce FPS: `--fps 15`
3. Remove preview: don't use `-p` flag
4. Check CPU usage: `top` or `htop`

### If you get module errors:
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall manim-studio
pip install -e .
```

### Finding rendered videos:
Videos are saved in:
```
user-data/{scene_name}/{quality}/[SceneName].mp4
```

For example:
- `user-data/CompleteAlchemyStory/1080p60/CompleteAlchemyStory.mp4`
- `user-data/SimpleDemo/480p15/SimpleDemo.mp4`

**IMPORTANT FOR CONTRIBUTORS**: Do NOT change the output directory back to `media/videos`. The output paths have been intentionally moved to `user-data/` to organize user-generated content separately from the codebase. The media directory configuration is set in:
- `/src/cli.py:145` - Main CLI media_dir configuration
- Shell scripts in `/scripts/` and `/examples/` directories

## Creating Your Own Scenes

See `scenes/README.md` for detailed documentation on creating YAML scenes.

## Important Notes

- Long scenes (over 1 minute) can take 10-15 minutes to render even at low quality
- Manim renders each frame individually, so patience is required
- The first render is always slowest; subsequent renders use cached data
- Close other applications to free up CPU for faster rendering