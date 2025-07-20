# Manim Studio v2.0 - Scalable Animation Framework

A configuration-driven framework for creating animated videos using Manim. Now with improved scalability, modularity, and ease of use.

## What's New in v2.0

### 🚀 Configuration-Driven Scenes
Create complex animations using YAML or JSON configuration files instead of hardcoding everything:

```yaml
name: "MyAnimation"
duration: 10.0
background_color: "#000000"

objects:
  title:
    type: text
    text: "Hello World"
    params:
      gradient: ["#FF6B6B", "#4ECDC4"]
      scale: 1.5

effects:
  - type: particle_system
    start_time: 2.0
    params:
      n_emitters: 3
      particle_color: "#FFD700"

animations:
  - target: title
    animation_type: write
    start_time: 0.0
    duration: 2.0
```

### 🎬 Timeline System
Choreograph complex animation sequences with precise timing control:

```python
timeline = Timeline()
timeline.add_event(0.0, show_title)
timeline.add_animation(2.0, FadeIn(subtitle))
timeline.add_sequence(5.0, effect_sequence)
timeline.play(scene)
```

### 📦 Asset Management
Centralized asset loading with automatic caching and placeholders:

```python
assets = AssetManager("./project")
logo = assets.load_image("logo.png")
data = assets.load_data("config.json")
```

### 🎨 Effect Registry
Extensible effect system with plugin architecture:

```python
@register_effect("custom_effect")
class CustomEffect(BaseEffect):
    def create(self):
        # Your effect logic
        pass
```

### 🔧 CLI Tool
Render scenes directly from configuration files:

```bash
manim-studio render config.yaml --quality high --preview
```

## Installation

```bash
pip install -e .
```

## Quick Start

1. **Create a configuration file** (`my_scene.yaml`):
```yaml
name: "QuickDemo"
duration: 5.0

objects:
  message:
    type: text
    text: "Welcome to Manim Studio!"
    params:
      color: "#FFFFFF"
      scale: 1.2

animations:
  - target: message
    animation_type: write
    start_time: 0.0
    duration: 2.0
```

2. **Render the scene**:
```bash
python -m manim_studio.cli my_scene.yaml --preview
```

## Architecture Improvements

### Before (v1.0)
- Hardcoded scene definitions
- Fixed effect parameters
- Limited reusability
- Difficult to scale

### After (v2.0)
- Configuration-driven
- Dynamic effect system
- Modular components
- Easy to extend and maintain

## Features

- **Configuration Files**: Define scenes in YAML/JSON
- **Timeline System**: Precise animation choreography
- **Asset Pipeline**: Automatic asset loading and caching
- **Effect Registry**: Plugin-based effect system
- **Scene Builder**: Dynamic scene generation from configs
- **CLI Interface**: Command-line rendering tool

## Example: Book Trailer

Create a book trailer with multiple effects:

```json
{
  "name": "BookTrailer",
  "duration": 30.0,
  "objects": {
    "title": {
      "type": "text",
      "text": "The Chronicles of Shadow"
    }
  },
  "effects": [
    {
      "type": "magical_circle",
      "params": {
        "radius": 3.0,
        "rotation_speed": 0.2,
        "symbols": ["📖", "✨", "🌙", "⚔️"]
      }
    }
  ]
}
```

## Extending the Framework

### Custom Effects
```python
from manim_studio import register_effect, BaseEffect

@register_effect("lightning")
class LightningEffect(BaseEffect):
    def create(self):
        # Create lightning visuals
        pass
    
    def animate(self, scene):
        # Animate the effect
        pass
```

### Custom Object Types
Add new object types to the scene builder for specialized content.

## Documentation

- [Configuration Guide](docs/configuration.md)
- [Timeline System](docs/timeline.md)
- [Creating Effects](docs/effects.md)
- [Asset Management](docs/assets.md)

## License

MIT License