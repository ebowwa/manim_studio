# Manim Studio - The Future of Interactive Mathematical Content

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![Manim Version](https://img.shields.io/badge/manim-0.17.3%2B-green)](https://www.manim.community/)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**The least friction way to create stunning mathematical animations** - Manim Studio is building the foundation for the Netflix of mathematical content: an interactive, AI-powered platform where creators and viewers merge into one experience.

🚀 **Current Focus**: Zero-friction animation generation through configuration files and AI
🎮 **Future Vision**: Interactive mathematical experiences, real-time exploration, and community-driven content platform

## 🌟 What Makes Manim Studio Different

### Today: The Least Friction Animation Generator
- **📝 Zero-Code Creation**: YAML/JSON configs - anyone can animate
- **🤖 AI-Powered**: MCP interface lets AI create animations for you
- **🎓 Educational Focus**: Pre-built templates from top math YouTubers
- **⚡ Instant Results**: No setup, no learning curve, just create

### Tomorrow: Interactive Mathematical Universe
- **🎮 Real-Time Interaction**: Explore math like a video game
- **🌐 Content Platform**: Share, remix, and collaborate on animations
- **🧠 AI Co-Creator**: Generate custom educational content on demand
- **♾️ Infinite Content**: User-generated mathematical experiences

## 💡 Current Capabilities

- **Advanced Timeline System**: Professional choreography with easing library
- **100+ Visual Effects**: Particles, magical circles, morphing, transitions
- **Algorithm Visualizers**: Sorting, graph traversal, data structures
- **Educational Templates**: Code reveal, mathematical proofs, step-by-step
- **3D Math Utilities**: Vector3D, Matrix4x4, spatial transformations
- **Smart Boundaries**: Animations that respect video frame limits
- **Asset Management**: Automatic caching and optimization

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

**Quick Start without Installation**: You can also run Manim Studio directly without installing by using `python main.py` instead of `manim-studio` in all examples.

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

2. **Render your animation**:

```bash
# Using the installed CLI command
manim-studio hello_world.yaml --preview

# Or run directly with Python (no installation needed)
python main.py hello_world.yaml --preview
```

3. **Watch your creation come to life!** 🎉

## 🧪 Multiple Interface Options

**Choose your preferred workflow:**

### 🤖 AI-Powered Creation (MCP Interface)
Let AI create animations for you:
```bash
# Use with Claude Desktop, Cline, or other MCP clients
# Install the MCP server and get full Manim Studio capabilities
```

### 💻 Developer Experience (Neovim Interface)
Full IDE integration for YAML editing:
```bash
# Generate Neovim plugin
manim-studio --interface nvim-plugin

# Start LSP server
manim-studio --interface nvim-lsp
```

**Features:**
- Auto-completion for object types, animations, and properties
- Real-time validation with error highlighting
- Hover documentation for all configuration options
- Live preview with `<leader>mp`, render with `<leader>mr`
- Template insertion for objects and animations

### 🖥️ Command Line Interface
Direct rendering from terminal:
```bash
manim-studio scene.yaml --preview
```

## 📚 Examples

### Algorithm Visualization (New!)

```yaml
name: "BubbleSort"
duration: 10.0

objects:
  array:
    type: algorithm_visualizer
    algorithm: bubble_sort
    data: [5, 2, 8, 1, 9, 3]
    params:
      show_code: true
      highlight_comparisons: true

animations:
  - target: array
    animation_type: run_algorithm
    start_time: 1.0
    duration: 8.0
```

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

## 🛠️ Why Creators Choose Manim Studio

### 🎯 Zero Learning Curve
```yaml
# This is all you need to create professional animations
name: "MyFirstAnimation"
objects:
  title:
    type: text
    text: "E = mc²"
animations:
  - target: title
    animation_type: write
```

### 🧩 Pre-Built Excellence
- **xiaoxiae Integration**: Production techniques from 100k+ subscriber math channels
- **Algorithm Library**: Sorting, graphs, data structures - all animated
- **Effect Collection**: 100+ effects that just work
- **Smart Defaults**: Professional output without configuration

### 🤖 AI-First Design
```python
# Let AI create entire educational videos
from manim_studio import AICreator

creator = AICreator()
video = creator.generate("Explain quicksort with beautiful animations")
video.render()
```

### ⚡ Instant Gratification
- **Live Preview**: See changes in real-time
- **Hot Reload**: Edit configs while rendering
- **Smart Caching**: Re-render only what changed

## 📖 Documentation

### Core Concepts
- [Configuration Schema](docs/configuration.md) - Complete YAML/JSON reference
- [Timeline System](docs/timeline.md) - Advanced choreography techniques
- [Effect Development](docs/effects.md) - Create custom visual effects
- [Asset Pipeline](docs/assets.md) - Media management best practices
- [API Reference](docs/api.md) - Full Python API documentation

### Interface Documentation
- [Neovim Integration](src/interfaces/nvim/README.md) - LSP server, plugin setup, and development workflow
- [MCP Interface](src/interfaces/mcp/) - AI-powered animation creation
- [GUI Interface](src/interfaces/gradio/) - Web-based visual editor
- [API Interface](src/interfaces/api_interface.py) - REST API for external integrations

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

## 🚧 Roadmap: Building the Future

### Phase 1: Frictionless Creation (Current)
- [x] Configuration-driven animations
- [x] Educational templates from top creators
- [x] AI integration via MCP
- [ ] Web-based configuration editor
- [ ] One-click deploy to social media

### Phase 2: Interactive Platform (Q2 2025)
- [ ] Real-time preview and editing
- [ ] GPU acceleration for instant rendering
- [ ] Community marketplace for effects
- [ ] Collaborative animation projects
- [ ] Version control for animations

### Phase 3: Mathematical Metaverse (Q4 2025)
- [ ] Real-time interactive math exploration
- [ ] Multiplayer mathematical experiences
- [ ] AI tutors using custom animations
- [ ] VR/AR mathematical visualization
- [ ] Blockchain-based content ownership

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

## 🎬 Join the Revolution

Manim Studio isn't just another animation tool - it's the beginning of a new era where:
- **Every student** can visualize their learning
- **Every teacher** can create engaging content
- **Every idea** can become an interactive experience

Start creating today. The future of mathematical content is in your hands.

**Made with ❤️ by dreamers who believe math should be beautiful**

*Keywords: manim, animation, python, ai animation, mathematical visualization, educational platform, interactive content, zero-code animation, algorithm visualization, future of education*