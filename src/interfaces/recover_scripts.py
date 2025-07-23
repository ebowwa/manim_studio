#!/usr/bin/env python3
"""Utility to list and recover saved MCP-generated scripts."""

import json
import sys
from pathlib import Path
from datetime import datetime

def list_saved_scripts():
    """List all saved MCP scripts with their metadata."""
    script_dir = Path("/Users/ebowwa/apps/manim_studio/user-data/mcp-scripts")
    
    if not script_dir.exists():
        print(f"Script directory does not exist: {script_dir}")
        return
    
    scripts = list(script_dir.glob("*.py"))
    
    if not scripts:
        print("No saved scripts found.")
        return
    
    print(f"\nFound {len(scripts)} saved script(s):\n")
    
    for i, script_path in enumerate(sorted(scripts, reverse=True), 1):
        print(f"{i}. {script_path.name}")
        
        # Try to load metadata
        metadata_path = script_path.with_suffix('.json')
        if metadata_path.exists():
            try:
                metadata = json.loads(metadata_path.read_text())
                print(f"   Scene: {metadata.get('scene_name', 'Unknown')}")
                print(f"   Created: {metadata.get('timestamp', 'Unknown')}")
                print(f"   Quality: {metadata.get('quality', 'Unknown')}")
                print(f"   Duration: {metadata.get('scene_config', {}).get('duration', 'Unknown')}s")
            except Exception as e:
                print(f"   (Could not read metadata: {e})")
        else:
            # Parse from filename
            parts = script_path.stem.split('_')
            if len(parts) >= 3:
                timestamp = f"{parts[0]}_{parts[1]}"
                scene_name = '_'.join(parts[2:-1])
                print(f"   Scene: {scene_name}")
                print(f"   Created: {timestamp}")
        print()

def render_script(script_number):
    """Render a specific saved script."""
    script_dir = Path("/Users/ebowwa/apps/manim_studio/user-data/mcp-scripts")
    scripts = sorted(list(script_dir.glob("*.py")), reverse=True)
    
    if script_number < 1 or script_number > len(scripts):
        print(f"Invalid script number. Please choose between 1 and {len(scripts)}")
        return
    
    script_path = scripts[script_number - 1]
    print(f"\nRendering script: {script_path.name}")
    
    # Load metadata if available
    metadata_path = script_path.with_suffix('.json')
    quality = "m"  # default
    
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text())
            quality_map = {"low": "l", "medium": "m", "high": "h", "4k": "k"}
            quality = quality_map.get(metadata.get('quality', 'medium'), 'm')
        except Exception:
            pass
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"recovered_{timestamp}.mp4"
    
    # Run manim
    import subprocess
    cmd = [
        "python", "-m", "manim",
        str(script_path),
        "Scene",
        f"-q{quality}",
        "-p",
        "--media_dir", "user-data",
        "-o", output_path
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

def main():
    """Main entry point."""
    if len(sys.argv) == 1:
        list_saved_scripts()
        print("\nUsage:")
        print("  python recover_scripts.py          # List all saved scripts")
        print("  python recover_scripts.py <number> # Render specific script")
    elif len(sys.argv) == 2:
        try:
            script_number = int(sys.argv[1])
            render_script(script_number)
        except ValueError:
            print("Please provide a valid script number")
            list_saved_scripts()

if __name__ == "__main__":
    main()