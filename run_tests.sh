#!/bin/bash

# Run tests for MCP-Mem0

set -e  # Exit on error

echo "Running MCP-Mem0 Tests..."
echo "========================="

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to project directory
cd "$DIR"

# Check if pytest is installed
if ! python -m pytest --version >/dev/null 2>&1; then
    echo "Installing pytest..."
    pip install pytest pytest-asyncio
fi

# Run tests with coverage if available
if python -m pytest --version >/dev/null 2>&1; then
    echo "Running tests with pytest..."
    python -m pytest tests/ -v --tb=short
else
    echo "Running tests with unittest..."
    python -m unittest discover tests/ -v
fi

echo ""
echo "Tests completed!"