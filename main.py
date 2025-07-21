#!/usr/bin/env python3
"""Main entry point for Manim Studio.

This file allows running Manim Studio directly with:
    python main.py config.yaml
    
It's equivalent to using the installed command:
    manim-studio config.yaml
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli import main

if __name__ == "__main__":
    main()