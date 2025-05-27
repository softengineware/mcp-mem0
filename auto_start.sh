#!/bin/bash

# MCP-Mem0 Auto Memory Start Script
# Starts the auto memory server and configures Claude Code

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Function to display errors
error_exit() {
    echo "ERROR: $1" >&2
    exit 1
}

# Function to check if process is running
is_running() {
    pgrep -f "python.*$1" > /dev/null 2>&1
}

# Check Python
if ! command -v python3 &> /dev/null; then
    error_exit "Python 3 is not installed or not in PATH"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    error_exit ".env file not found. Run ./setup_claude.sh first."
fi

# Load environment
set -a
source .env
set +a

# Validate environment
if [ -z "${LLM_PROVIDER:-}" ] || [ -z "${DATABASE_URL:-}" ]; then
    error_exit "Required environment variables not set. Check .env file."
fi

# Check if the auto_memory MCP server is running
if ! is_running "auto_memory.py"; then
    echo "Starting MCP-Mem0 auto memory server..."
    
    # Create log directory if needed
    mkdir -p logs
    
    # Start the server with proper logging
    nohup python3 "src/auto_memory.py" > "logs/auto_memory.log" 2>&1 &
    SERVER_PID=$!
    
    # Wait for the server to start
    echo -n "Waiting for server to start"
    for i in {1..10}; do
        sleep 1
        echo -n "."
        if is_running "auto_memory.py"; then
            echo " Started!"
            echo "Server PID: $SERVER_PID"
            echo "Log file: $DIR/logs/auto_memory.log"
            break
        fi
    done
    
    if ! is_running "auto_memory.py"; then
        echo " Failed!"
        echo "Check logs/auto_memory.log for details:"
        tail -20 logs/auto_memory.log
        exit 1
    fi
else
    echo "MCP-Mem0 auto memory server is already running."
    echo "To restart: pkill -f 'python.*auto_memory.py' && $0"
fi

# Check if claude command exists
if ! command -v claude &> /dev/null; then
    echo "Warning: 'claude' command not found."
    echo "Please install Claude Code or add it to your PATH."
    echo ""
    echo "The MCP server is running. Configure your MCP client with:"
    echo "  Transport: sse"
    echo "  URL: http://localhost:${PORT:-8050}/sse"
    exit 0
fi

# Configure Claude Code to use the MCP server if not already configured
echo "Checking Claude Code configuration..."
if ! claude config get mcpServers.auto_mem0 > /dev/null 2>&1; then
    echo "Configuring Claude Code to use MCP-Mem0 auto memory..."
    
    # Use proper error handling for config commands
    if claude config set mcpServers.auto_mem0.transport sse 2>/dev/null && \
       claude config set mcpServers.auto_mem0.url "http://localhost:${PORT:-8050}/sse" 2>/dev/null; then
        echo "Configuration complete!"
    else
        echo "Warning: Failed to configure Claude Code automatically."
        echo "Please configure manually with:"
        echo "  claude config set mcpServers.auto_mem0.transport sse"
        echo "  claude config set mcpServers.auto_mem0.url http://localhost:${PORT:-8050}/sse"
    fi
else
    echo "Claude Code is already configured to use MCP-Mem0."
fi

# Start Claude Code
echo ""
echo "========================================="
echo "MCP-Mem0 Auto Memory is ready!"
echo "========================================="
echo "Server running at: http://localhost:${PORT:-8050}/sse"
echo "Logs available at: $DIR/logs/auto_memory.log"
echo ""
echo "Starting Claude Code..."
echo "========================================="

# Launch Claude Code
exec claude