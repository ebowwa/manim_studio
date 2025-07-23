#!/usr/bin/env python3
"""Simple test to verify rendering works."""

import os
import sys
import tempfile
import subprocess

# Create a simple Manim script
script_content = '''
from src.config.manim_config import config
from manim import *

class SimpleTestScene(Scene):
    def construct(self):
        # Create simple text
        text = Text("GUI Render Test", font_size=48)
        text.set_color(WHITE)
        
        # Add animations
        self.play(FadeIn(text))
        self.wait(1)
        self.play(text.animate.scale(1.5).set_color(YELLOW))
        self.wait(1)
        self.play(FadeOut(text))
'''

# Write script to temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(script_content)
    script_path = f.name

print(f"Created test script at: {script_path}")

# Run manim command
cmd = f"python -m manim --media_dir user-data -ql {script_path} SimpleTestScene"
print(f"Running: {cmd}")

try:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("\nSTDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
    
    # Check if output was created
    expected_output = "user-data/videos/SimpleTestScene/480p15/SimpleTestScene.mp4"
    if os.path.exists(expected_output):
        print(f"\n✅ Success! Video created at: {expected_output}")
        print(f"File size: {os.path.getsize(expected_output)} bytes")
    else:
        print("\n❌ No video file found at expected location")
        # List contents of user-data
        if os.path.exists("user-data"):
            print("\nContents of user-data:")
            for root, dirs, files in os.walk("user-data"):
                level = root.replace("user-data", "").count(os.sep)
                indent = " " * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                sub_indent = " " * 2 * (level + 1)
                for file in files:
                    print(f"{sub_indent}{file}")
                    
finally:
    # Clean up temp file
    os.unlink(script_path)