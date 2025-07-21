#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to render a scene with different quality settings
render_scene() {
    local scene_file=$1
    local scene_class=$2
    local quality=$3

    echo -e "${BLUE}Rendering $scene_class with quality: $quality${NC}"
    
    case $quality in
        "low")
            PYTHONPATH=$PWD/src manim $scene_file $scene_class -pql --media_dir user-data  # 480p
            ;;
        "medium")
            PYTHONPATH=$PWD/src manim $scene_file $scene_class -pqm --media_dir user-data  # 720p
            ;;
        "high")
            PYTHONPATH=$PWD/src manim $scene_file $scene_class -pqh --media_dir user-data  # 1080p
            ;;
        "4k")
            PYTHONPATH=$PWD/src manim $scene_file $scene_class -pqk --media_dir user-data  # 4K
            ;;
        *)
            echo "Invalid quality setting. Use: low, medium, high, or 4k"
            exit 1
            ;;
    esac
}

# Ensure we're in the virtual environment
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Example usage:
echo -e "${GREEN}Example 1: Render in low quality (480p)${NC}"
render_scene "src/manim_studio/scenes/lyras_alchemy.py" "LyrasAlchemyScene" "low"

echo -e "${GREEN}Example 2: Render specific animations (use -n flag)${NC}"
PYTHONPATH=$PWD/src manim src/manim_studio/scenes/lyras_alchemy.py LyrasAlchemyScene -pql -n 0,5 --media_dir user-data

echo -e "${GREEN}Example 3: Skip to last frame (use -s flag)${NC}"
PYTHONPATH=$PWD/src manim src/manim_studio/scenes/lyras_alchemy.py LyrasAlchemyScene -pql -s --media_dir user-data

echo -e "${GREEN}Example 4: Save as GIF${NC}"
PYTHONPATH=$PWD/src manim src/manim_studio/scenes/lyras_alchemy.py LyrasAlchemyScene -pql --format=gif --media_dir user-data

echo -e "${GREEN}Example 5: Custom resolution${NC}"
PYTHONPATH=$PWD/src manim src/manim_studio/scenes/lyras_alchemy.py LyrasAlchemyScene -pql --resolution=1920,1080 --media_dir user-data

echo -e "${BLUE}All rendered videos can be found in the user-data directory${NC}"
echo -e "${BLUE}Usage: ./render_scene.sh${NC}"
