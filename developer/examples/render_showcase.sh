#!/bin/bash

# Ensure we're in the right directory
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Render the showcase scene in high quality
manim -qh examples/effects_showcase.py EffectsShowcase --media_dir user-data

# Open the rendered video (macOS specific)
open user-data/effects_showcase/1080p60/EffectsShowcase.mp4
