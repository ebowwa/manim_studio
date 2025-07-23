#!/usr/bin/env python3
"""Launch script for MCP server with proper path configuration."""

import sys
import os

# Add the src directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

# Now import and run the MCP interface
from interfaces.mcp_interface import main
import asyncio

if __name__ == "__main__":
    # Run the MCP server
    asyncio.run(main())