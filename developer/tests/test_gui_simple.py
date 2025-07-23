#!/usr/bin/env python3
"""Simple test of GUI rendering by running the GUI directly."""

import subprocess
import time
import requests
import json

def test_gui_api():
    """Test GUI rendering through its API."""
    print("Starting GUI test...\n")
    
    # Start the GUI in the background
    print("1. Starting GUI server...")
    gui_process = subprocess.Popen(
        ["python", "main.py", "gui"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    print("   Waiting for server to start...")
    time.sleep(5)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:7860")
        if response.status_code == 200:
            print("   ✅ GUI server is running!\n")
        else:
            print(f"   ❌ Server returned status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Could not connect to GUI server: {e}")
        gui_process.terminate()
        return
    
    print("2. GUI is accessible at: http://localhost:7860")
    print("   You can now:")
    print("   - Create a scene in the 'Scene Management' tab")
    print("   - Add objects in the 'Add Objects' tab")
    print("   - Add animations in the 'Add Animations' tab")
    print("   - Render the video in the 'Rendering' tab")
    
    print("\n3. To render a video:")
    print("   a) Go to the 'Rendering' tab")
    print("   b) Enter an output path (e.g., 'test_output.mp4')")
    print("   c) Select quality (Low for quick test)")
    print("   d) Click 'Render Scene'")
    
    print("\n4. The video will be saved in the user-data directory")
    
    print("\nPress Ctrl+C to stop the GUI server...")
    
    try:
        # Keep the server running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down GUI server...")
        gui_process.terminate()
        gui_process.wait()
        print("GUI server stopped.")

if __name__ == "__main__":
    test_gui_api()