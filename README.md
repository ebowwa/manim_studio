# Manim Studio

A reusable framework for creating animated videos using Manim, perfect for book trailers and promotional content.

## System Requirements

### Required System Dependencies

1. **LaTeX** (required for text rendering)
   ```bash
   # Install BasicTeX (recommended, smaller size)
   brew install --cask basictex
   
   # Add LaTeX binaries to PATH
   export PATH="/Library/TeX/texbin:$PATH"
   
   # Install required LaTeX packages
   sudo tlmgr update --self
   sudo tlmgr install standalone preview doublestroke mathtools amsmath babel-english
   sudo tlmgr install dvisvgm dvipng xetex
   sudo tlmgr install type1cm tex-gyre latex-bin dvips geometry graphics graphics-def hyperref
   sudo texhash
   
   # OR install full MacTeX (larger, includes more features)
   # brew install --cask mactex
   ```

2. **Python 3.7+**
   - macOS comes with Python, but you can install the latest version:
   ```bash
   brew install python
   ```

### Optional Dependencies

- **FFmpeg** (for video encoding, usually installed automatically with Manim)
  ```bash
  brew install ffmpeg
  ```

## Project Structure

```
manim_studio/
├── src/
│   └── manim_studio/
│       ├── resources/        # Input resources for animations
│       │   ├── images/      # Source images
│       │   ├── textures/    # Effect textures
│       │   └── fonts/       # Custom fonts
│       ├── components/      # Animation components
│       ├── scenes/         # Scene definitions
│       └── utils/          # Utility functions
├── tests/                  # Test files
├── docs/                   # Documentation
├── examples/               # Example scenes
└── output/                # Generated content (formerly media/)
    ├── videos/           # Rendered animations
    ├── images/           # Generated images
    └── tex/              # Generated LaTeX files
```

## Directory Purposes

- `resources/`: Source files used to create animations (images, textures, fonts)
- `output/`: Generated files from Manim (videos, images, LaTeX)

## Setup

1. Install system dependencies (if not already installed):
   ```bash
   # Install Homebrew if you haven't already
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install BasicTeX
   brew install --cask basictex
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install in development mode:
   ```bash
   pip install -e .
   ```

## Quick Start

Run the test animation:
```bash
./test_and_run.sh
```

## Creating Your Own Animations

1. Place your source images in `src/manim_studio/resources/images/`
2. Create a new scene in `src/manim_studio/scenes/`
3. Run your scene:
```bash
PYTHONPATH=$PWD/src manim src/manim_studio/scenes/your_scene.py YourScene -pql
```

## Required Resources

The following images should be placed in `src/manim_studio/resources/images/`:
- umbra_forest.png
- lunar_lily.png
- ashborne_academy.png
- vampire.png
- battle_scene.png

## Output Files

- All generated content will be in the `output/` directory
- Do not commit the `output/` directory to version control

## Troubleshooting

### Common Issues

1. **LaTeX Not Found**
   ```
   LaTeX is not installed...
   ```
   Solution: Install BasicTeX using the command in the System Requirements section.

2. **FFmpeg Missing**
   Solution: Install FFmpeg using `brew install ffmpeg`

3. **Python Dependencies**
   Solution: Make sure you're in the virtual environment and run:
   ```bash
   pip install -r requirements.txt
   ```
