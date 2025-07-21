# Frame Extraction Feature

The frame extraction feature in Manim Studio allows you to automatically extract frames from your animations during or after rendering. This is useful for:

- Creating thumbnail previews
- Analyzing animation quality
- Debugging timing issues
- Creating storyboards
- Generating documentation

## Features

- **Automatic Frame Extraction**: Extract frames at regular intervals during rendering
- **Keyframe Detection**: Automatically detect and extract frames with significant changes
- **Visual Analysis**: Analyze extracted frames for quality metrics (brightness, contrast, sharpness)
- **Report Generation**: Generate PDF reports with analysis results and visualizations
- **Flexible Configuration**: Configure via YAML/JSON or programmatically

## Usage Methods

### Method 1: Configuration File (Recommended)

Add a `frame_extraction` section to your scene configuration:

```yaml
scenes:
  MyScene:
    name: "MyScene"
    duration: 10.0
    
    # Frame extraction configuration
    frame_extraction:
      enabled: true
      frame_interval: 30  # Extract every 30 frames
      analyze: true  # Run visual analysis
      generate_report: true  # Generate PDF report
      output_dir: "extracted_frames/my_scene"
      keyframe_extraction: false
      keyframe_threshold: 30.0
      max_frames: 100
    
    # ... rest of scene configuration
```

### Method 2: Using FrameExtractionMixin

```python
from manim import *
from manim_studio.core import FrameExtractionMixin

class MyScene(FrameExtractionMixin, Scene):
    def construct(self):
        # Enable frame extraction
        self.enable_frame_extraction(
            frame_interval=15,
            analyze=True,
            output_dir="extracted_frames/manual"
        )
        
        # Your animation code
        text = Text("Hello World")
        self.play(Write(text))
```

### Method 3: Using Render Hooks

```python
from manim import *
from manim_studio.core import auto_extract_frames

# Apply to existing scene class
MySceneWithExtraction = auto_extract_frames(
    MyScene,
    frame_interval=20,
    analyze=True
)

# Render the scene
scene = MySceneWithExtraction()
scene.render()
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | false | Enable frame extraction |
| `frame_interval` | int | 30 | Extract every N frames |
| `analyze` | bool | true | Run visual analysis on frames |
| `generate_report` | bool | true | Generate PDF analysis report |
| `output_dir` | str | None | Directory for extracted frames |
| `keyframe_extraction` | bool | false | Enable keyframe detection |
| `keyframe_threshold` | float | 30.0 | Threshold for keyframe detection |
| `max_frames` | int | None | Maximum frames to extract |

## Output Structure

When frame extraction is enabled, the following files are generated:

```
extracted_frames/
└── my_scene/
    ├── scene_frame_0000_at_0.00s.jpg
    ├── scene_frame_0001_at_0.50s.jpg
    ├── scene_frame_0002_at_1.00s.jpg
    ├── ...
    ├── scene_analysis.pdf  # Analysis report
    └── scene_grid.jpg      # Grid visualization
```

## Analysis Metrics

The frame analyzer evaluates:

- **Brightness**: Average luminance of the frame
- **Contrast**: Standard deviation of pixel values
- **Sharpness**: Edge detection using Laplacian variance
- **Motion Score**: Change detection between frames
- **Quality Score**: Overall quality metric (0-100)
- **Issues**: Detection of common problems (too dark, blurry, etc.)

## Examples

### Basic Example

```python
# examples/frame_extraction_demo.py
from manim_studio.core import SceneConfig, SceneBuilder

config = SceneConfig(
    name="Demo",
    frame_extraction={
        "enabled": True,
        "frame_interval": 15
    }
)

# Add objects and animations...

builder = SceneBuilder()
Scene = builder.build_scene(config)
scene = Scene()
scene.render()
```

### Advanced Example with Analysis

See `examples/frame_extraction_demo.py` for a complete example demonstrating:
- Configuration-based extraction
- Manual extraction with custom settings
- Analysis report generation
- Multiple extraction methods

## Tips

1. **Frame Interval**: For a 30fps video, `frame_interval=30` extracts 1 frame per second
2. **Keyframes**: Enable `keyframe_extraction` for scenes with distinct segments
3. **Performance**: Extraction happens after rendering, so it doesn't slow down animation generation
4. **Storage**: Each frame is ~50-200KB depending on resolution. Plan accordingly for long animations
5. **Analysis**: The PDF report provides valuable insights into animation quality

## Troubleshooting

### No frames extracted
- Check that `enabled: true` is set in configuration
- Verify the output directory exists and is writable
- Check console output for error messages

### Analysis fails
- Ensure OpenCV is installed: `pip install opencv-python`
- For PDF reports, matplotlib is required: `pip install matplotlib`

### Large file sizes
- Reduce `frame_interval` to extract fewer frames
- Set `max_frames` to limit total extracted frames
- Use JPEG format (default) instead of PNG