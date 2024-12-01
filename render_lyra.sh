#!/bin/bash

# Activate virtual environment and run the magical effects demo
source venv/bin/activate && PYTHONPATH=$PWD/src manim examples/magical_effects_demo.py MagicalEffectsDemo -pql
