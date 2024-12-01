#!/bin/bash
set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Manim Studio test environment...${NC}"

# Install LaTeX if not installed
if ! command -v latex &> /dev/null; then
    echo -e "${GREEN}Installing MacTeX...${NC}"
    curl -O https://mirror.ctan.org/systems/mac/mactex/mactex-basictex-2022.pkg
    sudo installer -pkg mactex-basictex-2022.pkg -target /
    rm mactex-basictex-2022.pkg
fi

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${GREEN}Upgrading pip...${NC}"
python -m pip install --upgrade pip

# Install requirements
echo -e "${GREEN}Installing requirements...${NC}"
pip install -r requirements.txt

# Install package in development mode
echo -e "${GREEN}Installing manim_studio package...${NC}"
pip install -e .

# Create test assets directory if it doesn't exist
if [ ! -d "manim_studio/assets" ]; then
    echo -e "${GREEN}Creating assets directory...${NC}"
    mkdir -p manim_studio/assets
fi

# Create a simple test image if none exist
if [ ! -f "manim_studio/assets/test_image.png" ]; then
    echo -e "${GREEN}Creating test image...${NC}"
    python3 -c "
from PIL import Image, ImageDraw
img = Image.new('RGB', (800, 600), color='blue')
draw = ImageDraw.Draw(img)
draw.rectangle([300, 200, 500, 400], fill='white')
img.save('manim_studio/assets/test_image.png')
"
fi

# Create symbolic links for test images
echo -e "${GREEN}Setting up test images...${NC}"
cd manim_studio/assets
for img in "umbra_forest.png" "lunar_lily.png" "ashborne_academy.png" "vampire.png" "battle_scene.png"; do
    if [ ! -f "$img" ]; then
        ln -sf test_image.png "$img"
    fi
done
cd ../..

# Run the test
echo -e "${GREEN}Running Manim test render...${NC}"
PYTHONPATH=$PWD manim manim_studio/scenes/lyras_alchemy.py LyrasAlchemy -pql

echo -e "${GREEN}Test completed! Check the media directory for the output video.${NC}"
