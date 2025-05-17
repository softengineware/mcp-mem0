#!/bin/bash

# Make script exit on error
set -e

# Get the port from the .env file
PORT=$(grep "PORT=" .env | cut -d'=' -f2)
PORT=${PORT:-8051}  # Default to 8051 if not found

echo "=========================================="
echo "Starting MCP-Mem0 Server"
echo "=========================================="
echo "Make sure you've set up your .env file with:"
echo "- OpenAI API key"
echo "- Supabase connection string"
echo "=========================================="
echo ""
echo "The server will start on http://localhost:$PORT/sse"
echo "Add to Claude Code with:"
echo "claude config set mcpServers.mem0.transport sse"
echo "claude config set mcpServers.mem0.url http://localhost:$PORT/sse"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the MCP server
python3 src/main.py