#!/usr/bin/env python3
"""Main entry point for Manim Studio.

This unified launcher can start any interface:
- CLI: python main.py cli scene.yaml -q l -p       
- API: python main.py api --port 8000              
- GUI: python main.py gui --port 7860              
- MCP: python main.py mcp                          

For backwards compatibility with CLI:
    python main.py config.yaml         # Auto-detects CLI mode
    
For new unified interface:
    python main.py --help              # Show all options
    python main.py --list-interfaces   # List available interfaces
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

def detect_cli_mode():
    """Detect if this is a CLI call for backwards compatibility."""
    # If first argument exists and doesn't start with interface names or flags
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        interface_names = ["cli", "api", "gui", "mcp"]
        flags = ["--help", "-h", "--list-interfaces"]
        
        # If it's not an interface name or flag, assume it's a CLI scene file
        if (not first_arg.startswith("-") and 
            first_arg not in interface_names and 
            first_arg not in flags):
            return True
    return False

if __name__ == "__main__":
    # Backwards compatibility: detect CLI usage
    if detect_cli_mode():
        print("🔄 Detected CLI mode (backwards compatibility)")
        print("💡 New syntax: python main.py cli scene.yaml -q l -p")
        print("   Use --help to see all interface options\n")
        
        from src.interfaces.cli.cli import main as cli_main
        cli_main()
    else:
        # Use new unified launcher
        from src.launcher import main as launcher_main
        launcher_main()