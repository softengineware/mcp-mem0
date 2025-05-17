#!/bin/bash

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if the auto_memory MCP server is running
if ! pgrep -f "python $DIR/src/auto_memory.py" > /dev/null; then
    echo "Starting MCP-Mem0 auto memory server..."
    # Start the server in the background
    nohup python "$DIR/src/auto_memory.py" > "$DIR/mcp_server.log" 2>&1 &
    
    # Wait for the server to start (give it 3 seconds)
    sleep 3
    
    if pgrep -f "python $DIR/src/auto_memory.py" > /dev/null; then
        echo "MCP-Mem0 server started successfully!"
    else
        echo "Failed to start MCP-Mem0 server. Check $DIR/mcp_server.log for details."
        exit 1
    fi
else
    echo "MCP-Mem0 server is already running."
fi

# Configure Claude Code to use the MCP server if not already configured
if ! claude config get mcpServers.auto_mem0 > /dev/null 2>&1; then
    echo "Configuring Claude Code to use MCP-Mem0 auto memory..."
    claude config set mcpServers.auto_mem0.transport sse
    claude config set mcpServers.auto_mem0.url "http://localhost:8050/sse"
    echo "Configuration complete!"
else
    echo "Claude Code is already configured to use MCP-Mem0."
fi

# Start Claude Code
echo "Starting Claude Code..."
claude