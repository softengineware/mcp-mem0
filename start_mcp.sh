#!/bin/bash

# MCP-Mem0 Server Start Script
# Starts the MCP server with proper error handling

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Function to display errors
error_exit() {
    echo "ERROR: $1" >&2
    exit 1
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Creating from .env.example if available..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Created .env from .env.example. Please update it with your settings."
        exit 1
    else
        error_exit ".env file not found. Please create one with required settings."
    fi
fi

# Load environment variables safely
set -a
source .env
set +a

# Get port with validation
PORT=${PORT:-8050}

# Validate required environment variables
if [ -z "${LLM_PROVIDER:-}" ]; then
    error_exit "LLM_PROVIDER not set in .env file"
fi

if [ -z "${DATABASE_URL:-}" ]; then
    error_exit "DATABASE_URL not set in .env file"
fi

if [ "${LLM_PROVIDER}" != "ollama" ] && [ -z "${LLM_API_KEY:-}" ]; then
    error_exit "LLM_API_KEY not set in .env file (required for $LLM_PROVIDER)"
fi

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Warning: Port $PORT is already in use."
    echo "To find what's using it: lsof -i :$PORT"
    echo "To kill it: kill -9 \$(lsof -t -i:$PORT)"
    error_exit "Port $PORT is not available"
fi

echo "=========================================="
echo "Starting MCP-Mem0 Server"
echo "=========================================="
echo "Configuration:"
echo "  - LLM Provider: ${LLM_PROVIDER}"
echo "  - LLM Model: ${LLM_CHOICE:-default}"
echo "  - Port: $PORT"
echo "  - Transport: ${TRANSPORT:-sse}"
echo "=========================================="
echo ""
echo "The server will start on http://localhost:$PORT/sse"
echo "Add to Claude Code with:"
echo "claude config set mcpServers.mem0.transport sse"
echo "claude config set mcpServers.mem0.url http://localhost:$PORT/sse"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="

# Check Python version
if ! command -v python3 &> /dev/null; then
    error_exit "Python 3 is not installed or not in PATH"
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)"; then
    error_exit "Python 3.12+ is required (found $PYTHON_VERSION)"
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if main.py exists
if [ ! -f "src/main.py" ]; then
    error_exit "src/main.py not found"
fi

# Handle cleanup on exit
trap 'echo "\nShutting down MCP-Mem0 server..."; exit 0' INT TERM

# Run the MCP server
exec python3 src/main.py