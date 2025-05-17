#!/bin/bash

# Make script exit on error
set -e

echo "=========================================="
echo "Setting up MCP-Mem0 for Claude Code"
echo "=========================================="

# Check if claude command exists
if ! command -v claude &> /dev/null; then
    echo "Error: Claude Code CLI not found."
    echo "Please make sure Claude Code is installed and the 'claude' command is available."
    exit 1
fi

echo "Configuring Claude Code to use MCP-Mem0..."
claude config set mcpServers.mem0.transport sse
claude config set mcpServers.mem0.url "http://localhost:8050/sse"

echo "=========================================="
echo "Configuration Complete!"
echo "=========================================="
echo ""
echo "To use MCP-Mem0 with Claude Code:"
echo ""
echo "1. Start the MCP server in a terminal:"
echo "   ./start_mcp.sh"
echo ""
echo "2. In another terminal, restart Claude Code:"
echo "   claude"
echo ""
echo "3. You can now use the following memory tools:"
echo "   - mcp__save_memory: Store information in long-term memory"
echo "   - mcp__get_all_memories: Retrieve all stored memories"
echo "   - mcp__search_memories: Find relevant memories with semantic search"
echo ""
echo "Example usage in Claude Code:"
echo "  'Save this information to my long-term memory: [content]'"
echo "  'What memories do I have stored?'"
echo "  'Search my memories for information about [topic]'"
echo "=========================================="