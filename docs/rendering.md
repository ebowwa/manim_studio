# Rendering Manim Studio Demos

This guide explains how to render the demo animations in Manim Studio.

## Prerequisites

- Python 3.9+
- Virtual environment with Manim installed
- Manim Studio package installed in development mode

## Available Demos

### 1. Magical Effects Demo
Located at `examples/magical_effects_demo.py`

This demo showcases various magical effects including:
- Particle systems
- Magic circles with sparkle reveals
- Gradient text animations
- Combined particle and geometric effects

## Rendering Scripts

### Using render_demos.sh

The `scripts/render_demos.sh` script provides an easy way to render demos. It will:
1. Activate the virtual environment
2. Set the correct Python path
3. Render the demo using manim

```bash
# Make the script executable
chmod +x scripts/render_demos.sh

# Run the script
./scripts/render_demos.sh
```

### Manual Rendering

If you prefer to render manually:

```bash
# Activate virtual environment
source venv/bin/activate

# Set Python path and render
PYTHONPATH=/path/to/manim_studio/src python3 -m manim examples/magical_effects_demo.py MagicalEffectsDemo -pql
```

### Output Location

Rendered videos will be saved to:
```
media/videos/magical_effects_demo/480p15/MagicalEffectsDemo.mp4
```

### Quality Options

The script supports different quality settings:
- `-ql`: Low quality (480p15)
- `-qm`: Medium quality (720p30)
- `-qh`: High quality (1080p60)
- `-qk`: 4K quality (2160p60)

To modify the quality, edit the quality parameter in `render_demos.sh`.

## Example Output

When you run the render script, you'll see output similar to:

```
Rendering MagicalEffectsDemo from examples/magical_effects_demo.py
[mm/dd/yy hh:mm:ss] INFO     Animation 0 : Write(Text)
[mm/dd/yy hh:mm:ss] INFO     Animation 1 : FadeIn(Dot)
...
[mm/dd/yy hh:mm:ss] INFO     Rendered MagicalEffectsDemo
                             Played XX animations
INFO     Previewed File at: '/path/to/manim_studio/media/videos/magical_effects_demo/480p15/MagicalEffectsDemo.mp4'
```

## Troubleshooting

If you encounter any issues:

1. Ensure your virtual environment is activated
2. Verify manim is installed in your virtual environment:
   ```bash
   pip list | grep manim
   ```
3. Check PYTHONPATH is set correctly
4. Verify the demo file exists in the examples directory

For more detailed debugging, add the `-v` flag to the manim command in the render script.
