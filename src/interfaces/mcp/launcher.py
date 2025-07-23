#!/usr/bin/env python3
"""Launch script for MCP server with proper path configuration."""

import sys
import os
import asyncio

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Now import and run the MCP server
from src.interfaces.mcp.server import main

if __name__ == "__main__":
    # Run the MCP server
    asyncio.run(main())