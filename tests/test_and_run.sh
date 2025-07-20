#!/bin/bash
set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Manim Studio environment...${NC}"

# Ensure LaTeX binaries are in PATH
export PATH="/Library/TeX/texbin:$PATH"

# Install required LaTeX packages
echo -e "${GREEN}Installing LaTeX packages...${NC}"
sudo tlmgr update --self
sudo tlmgr install standalone preview doublestroke dvisvgm dvipng xetex
sudo tlmgr install amsmath babel-english type1cm tex-gyre latex-bin dvips
sudo tlmgr install geometry graphics graphics-def hyperref

# Set up Python environment
echo -e "${GREEN}Setting up Python environment...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Install Python dependencies
pip install -e .

echo -e "${GREEN}Setup complete! You can now run your Manim scenes.${NC}"
echo -e "Example: PYTHONPATH=\$PWD/src manim src/manim_studio/scenes/your_scene.py YourScene -pql"
