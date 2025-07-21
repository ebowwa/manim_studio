# Manim Studio - Professional Animation Framework for Python

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![Manim Version](https://img.shields.io/badge/manim-0.17.3%2B-green)](https://www.manim.community/)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Create stunning mathematical animations and visualizations with code** - Manim Studio is a powerful, configuration-driven framework built on top of Manim that makes creating professional animated videos accessible to everyone.

🎬 **Perfect for**: Educational content, data visualization, mathematical animations, video production, motion graphics, and creative coding.

## 🌟 Key Features

- **📝 Configuration-Driven**: Create complex animations using simple YAML/JSON files - no programming required
- **⏱️ Advanced Timeline System**: Choreograph animations with millisecond precision
- **🎨 70+ Built-in Effects**: Particles, transitions, morphing, and more
- **🔌 Plugin Architecture**: Extend with custom effects and components
- **📦 Asset Management**: Automatic loading, caching, and placeholder generation
- **🚀 CLI Tool**: Render videos directly from command line
- **🎯 Production-Ready**: Used for educational videos, presentations, and content creation

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (coming soon)
pip install manim-studio

# Or install from source
git clone https://github.com/ebowwa/manim_studio.git
cd manim_studio
pip install -e .
```

### Create Your First Animation

1. **Create a configuration file** (`hello_world.yaml`):

```yaml
name: "HelloWorld"
duration: 5.0

objects:
  message:
    type: text
    text: "Welcome to Manim Studio!"
    params:
      gradient: ["#FF6B6B", "#4ECDC4"]
      scale: 1.5

animations:
  - target: message
    animation_type: write
    start_time: 0.0
    duration: 2.0
```

```

2. **Render your animation**:

```bash
manim-studio render hello_world.yaml --preview
```

3. **Watch your creation come to life!** 🎉

## 📚 Examples

### Mathematical Visualization

```yaml
name: "MathDemo"
duration: 8.0

objects:
  equation:
    type: text
    text: "$e^{i\pi} + 1 = 0$"
    params:
      tex: true
      scale: 2.0
      
  graph:
    type: function_graph
    function: "lambda x: np.sin(x)"
    params:
      x_range: [-3, 3]
      color: "#4ECDC4"

animations:
  - target: equation
    animation_type: write
    start_time: 0.0
    duration: 2.0
  - target: graph
    animation_type: create
    start_time: 2.5
    duration: 3.0
```

### Data Visualization

```yaml
name: "DataViz"
duration: 10.0

objects:
  chart:
    type: bar_chart
    data: [10, 25, 15, 30, 45]
    params:
      labels: ["A", "B", "C", "D", "E"]
      colors: ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]

effects:
  - type: particle_burst
    start_time: 5.0
    params:
      position: [0, 0, 0]
      count: 100

animations:
  - target: chart
    animation_type: grow_from_bottom
    start_time: 1.0
    duration: 3.0
```

## 🛠️ Advanced Features

### Timeline System

Create complex, synchronized animations with the Timeline API:

```python
from manim_studio import Timeline, Scene

timeline = Timeline()
timeline.add_event(0.0, lambda: show_title())
timeline.add_animation(2.0, FadeIn(subtitle))
timeline.add_parallel([
    (3.0, animation1),
    (3.0, animation2),
    (3.5, animation3)
])
timeline.play(scene)
```

### Custom Effects

Extend Manim Studio with your own effects:

```python
from manim_studio import register_effect, BaseEffect

@register_effect("glitch")
class GlitchEffect(BaseEffect):
    def create(self):
        # Create glitch visual elements
        return self.elements
    
    def animate(self, scene, duration=1.0):
        # Define glitch animation
        scene.play(self.glitch_animation, run_time=duration)
```

### Asset Management

```python
from manim_studio import AssetManager

# Initialize asset manager
assets = AssetManager("./project_assets")

# Load with automatic caching
logo = assets.load_image("logo.png")
data = assets.load_data("animation_config.json")
audio = assets.load_audio("background_music.mp3")

# Automatic placeholder generation if asset missing
texture = assets.load_image("missing.jpg", placeholder=True)
```

## 📖 Documentation

### Core Concepts
- [Configuration Schema](docs/configuration.md) - Complete YAML/JSON reference
- [Timeline System](docs/timeline.md) - Advanced choreography techniques
- [Effect Development](docs/effects.md) - Create custom visual effects
- [Asset Pipeline](docs/assets.md) - Media management best practices
- [API Reference](docs/api.md) - Full Python API documentation

### Tutorials
- [Getting Started Guide](docs/tutorials/getting-started.md)
- [Creating Educational Content](docs/tutorials/educational.md)
- [Data Visualization](docs/tutorials/data-viz.md)
- [Advanced Techniques](docs/tutorials/advanced.md)

## 🤝 Community & Support

- **Discord**: [Join our community](https://discord.gg/manim-studio)
- **GitHub Discussions**: [Ask questions](https://github.com/ebowwa/manim_studio/discussions)
- **Stack Overflow**: Tag your questions with `manim-studio`
- **Twitter**: [@ManimStudio](https://twitter.com/ManimStudio)

## 🚧 Roadmap

- [ ] Web-based configuration editor
- [ ] Real-time preview system
- [ ] GPU acceleration support
- [ ] Export to various formats (GIF, WebM, etc.)
- [ ] Integration with popular video editors
- [ ] AI-powered animation suggestions

## 🤲 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/manim_studio.git
cd manim_studio

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built on top of the amazing [Manim Community](https://www.manim.community/) project
- Inspired by [3Blue1Brown](https://www.3blue1brown.com/)'s mathematical animations
- Special thanks to all our [contributors](https://github.com/ebowwa/manim_studio/graphs/contributors)

---

**Made with ❤️ by the Manim Studio community**

*Keywords: manim, animation, python, video, visualization, mathematical animation, educational content, motion graphics, data visualization, creative coding, animation framework, video production*