#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directory setup
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEDIA_DIR="$PROJECT_ROOT/media/videos"
EXAMPLES_DIR="$PROJECT_ROOT/examples"

# Function to render a demo scene
render_demo() {
    local scene_file="$1"
    local scene_name="$2"
    local quality="$3"

    echo -e "${BLUE}Rendering $scene_name from $scene_file${NC}"
    source "$PROJECT_ROOT/venv/bin/activate" && \
    PYTHONPATH=$PROJECT_ROOT/src python3 -m manim "$scene_file" "$scene_name" -p"$quality"
}

# Render magical effects demo
render_demo "$EXAMPLES_DIR/magical_effects_demo.py" "MagicalEffectsDemo" "ql"

# Output location of rendered video
echo -e "${GREEN}Demo videos have been rendered to: $MEDIA_DIR${NC}"
