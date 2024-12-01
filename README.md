# Manim Studio

A reusable framework for creating animated videos using Manim, perfect for book trailers and promotional content.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place your images in the `manim_studio/assets` directory.

## Project Structure

```
manim_studio/
├── assets/           # Store images and other media files here
├── components/       # Reusable animation components
├── scenes/          # Scene definitions
└── utils/           # Utility functions
```

## Usage

To render the Lyra's Alchemy video:

```bash
cd manim_studio
manim scenes/lyras_alchemy.py LyrasAlchemy -pql
```

## Customization

1. Create new scenes by inheriting from `StudioScene`
2. Use the provided components in `base_components.py`
3. Add your own transitions and effects in `components/`

## Required Images

Place the following images in the `assets` directory:
- umbra_forest.png
- lunar_lily.png
- ashborne_academy.png
- vampire.png
- battle_scene.png
