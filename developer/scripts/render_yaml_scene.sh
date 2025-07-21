#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to render a YAML scene
render_yaml_scene() {
    local config_file=$1
    local scene_name=$2
    local quality=$3
    
    echo -e "${BLUE}Rendering $scene_name from $config_file with quality: $quality${NC}"
    
    # Build the command
    cmd="manim-studio $config_file"
    
    # Add scene name if provided
    if [ ! -z "$scene_name" ]; then
        cmd="$cmd -s $scene_name"
    fi
    
    # Add quality setting
    case $quality in
        "low"|"480p")
            cmd="$cmd -q l"
            ;;
        "medium"|"720p")
            cmd="$cmd -q m"
            ;;
        "high"|"1080p")
            cmd="$cmd -q h"
            ;;
        "production"|"1440p")
            cmd="$cmd -q p"
            ;;
        "4k")
            cmd="$cmd -q k"
            ;;
        *)
            echo "Invalid quality setting. Use: low, medium, high, production, or 4k"
            return 1
            ;;
    esac
    
    # Add preview flag
    cmd="$cmd -p"
    
    # Execute the command
    echo -e "${YELLOW}Running: $cmd${NC}"
    $cmd
}

# Ensure we're in the virtual environment
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo -e "${YELLOW}Warning: Virtual environment not found${NC}"
    fi
fi

# Check if manim-studio is installed
if ! command -v manim-studio &> /dev/null; then
    echo -e "${YELLOW}manim-studio command not found. Installing...${NC}"
    pip install -e .
fi

# Example usage
echo -e "${GREEN}=== Manim Studio YAML Scene Renderer ===${NC}"
echo ""

# Check if a config file was provided as argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <config_file.yaml> [scene_name] [quality]"
    echo ""
    echo "Examples:"
    echo "  $0 configs/example_scene.yaml"
    echo "  $0 scenes/lyras_alchemy.yaml LyrasAlchemy high"
    echo "  $0 configs/content_types/youtube_short.yaml MyScene 4k"
    echo ""
    echo "Available YAML scenes:"
    find . -name "*.yaml" -path "*/scenes/*" -o -path "*/configs/*" -name "*.yaml" | grep -v venv | sort
    exit 0
fi

# Parse arguments
CONFIG_FILE=$1
SCENE_NAME=${2:-""}
QUALITY=${3:-"high"}

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}Error: Config file not found: $CONFIG_FILE${NC}"
    exit 1
fi

# Render the scene
render_yaml_scene "$CONFIG_FILE" "$SCENE_NAME" "$QUALITY"

echo -e "${BLUE}Rendered videos can be found in the user-data directory${NC}"