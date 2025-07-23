#!/bin/bash
# Start the Manim Studio MCP server

cd /Users/ebowwa/apps/manim_studio

echo "Starting Manim Studio MCP server..."

# Kill any existing MCP server process
pkill -f "run_mcp_server.py" 2>/dev/null

# Start the server in the background
nohup python3 run_mcp_server.py > mcp_server.log 2>&1 &

# Get the PID
MCP_PID=$!

echo "MCP server started with PID: $MCP_PID"
echo "Logs are being written to: mcp_server.log"
echo ""
echo "To stop the server, run: kill $MCP_PID"
echo "To view logs, run: tail -f mcp_server.log"

# Save PID to file for easy stopping later
echo $MCP_PID > mcp_server.pid

echo ""
echo "Server is ready! You can now start Claude Desktop."