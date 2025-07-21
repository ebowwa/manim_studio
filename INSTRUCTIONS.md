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
manim-studio scenes/your_scene.yaml -q l -p
```

## Command Options

### Basic Rendering
```bash
# Render with preview (opens video after rendering)
manim-studio scenes/complete_alchemy_story.yaml -q l -p

# Render without preview (faster)
manim-studio scenes/complete_alchemy_story.yaml -q l
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

# Save with custom filename
manim-studio scenes/complete_alchemy_story.yaml -q l -o my_video.mp4
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
media/videos/{quality}/[SceneName].mp4
```

For example:
- `media/videos/1080p60/CompleteAlchemyStory.mp4`
- `media/videos/480p15/SimpleDemo.mp4`

## Creating Your Own Scenes

See `scenes/README.md` for detailed documentation on creating YAML scenes.

## Important Notes

- Long scenes (over 1 minute) can take 10-15 minutes to render even at low quality
- Manim renders each frame individually, so patience is required
- The first render is always slowest; subsequent renders use cached data
- Close other applications to free up CPU for faster rendering