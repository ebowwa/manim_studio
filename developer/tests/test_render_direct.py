#!/usr/bin/env python3
"""Direct test of rendering without imports."""

import os
import tempfile
import subprocess

# Create a simple Manim script with no external dependencies
script_content = '''
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
    # Change to manim studio directory
    os.chdir("/Users/ebowwa/apps/manim_studio")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("\nSTDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
    
    if result.returncode == 0:
        print("\n✅ Rendering succeeded!")
        # Check for output file
        possible_paths = [
            "user-data/videos/SimpleTestScene/480p15/SimpleTestScene.mp4",
            "user-data/SimpleTestScene/480p15/SimpleTestScene.mp4",
            f"user-data/videos/{os.path.basename(script_path).replace('.py', '')}/480p15/SimpleTestScene.mp4"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Video created at: {path}")
                print(f"File size: {os.path.getsize(path)} bytes")
                break
        else:
            print("⚠️ Video file not found at expected locations")
            print("\nSearching for .mp4 files in user-data:")
            for root, dirs, files in os.walk("user-data"):
                for file in files:
                    if file.endswith(".mp4") and "SimpleTestScene" in file:
                        print(f"Found: {os.path.join(root, file)}")
    else:
        print("\n❌ Rendering failed!")
        
finally:
    # Clean up temp file
    os.unlink(script_path)
    print(f"\nCleaned up temp file: {script_path}")