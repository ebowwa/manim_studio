#!/bin/bash
# Stop the Manim Studio MCP server

if [ -f mcp_server.pid ]; then
    PID=$(cat mcp_server.pid)
    if ps -p $PID > /dev/null; then
        echo "Stopping MCP server (PID: $PID)..."
        kill $PID
        rm mcp_server.pid
        echo "MCP server stopped."
    else
        echo "MCP server is not running (PID $PID not found)."
        rm mcp_server.pid
    fi
else
    echo "No PID file found. Trying to find and stop any running MCP server..."
    pkill -f "run_mcp_server.py"
    echo "Done."
fi