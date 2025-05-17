# Automatic Memory for Claude Code

This extension to MCP-Mem0 provides automatic conversation memory similar to ChatGPT, saving all messages without requiring explicit commands.

## How It Works

The automatic memory system:

1. Stores all user and assistant messages automatically
2. Maintains conversation context across sessions
3. Uses semantic search to retrieve relevant past conversations
4. Runs as a background service

## Setup Instructions

### 1. One-Click Setup

The easiest way to set up automatic memory is using the auto_start script:

```bash
cd ~/mcp-mem0
./auto_start.sh
```

This will:
- Start the memory server if it's not running
- Configure Claude Code to use the memory server
- Launch Claude Code

### 2. Manual Setup

If you prefer manual setup:

1. Start the automatic memory server:
   ```bash
   cd ~/mcp-mem0
   python src/auto_memory.py
   ```

2. Configure Claude Code:
   ```bash
   claude config set mcpServers.auto_mem0.transport sse
   claude config set mcpServers.auto_mem0.url "http://localhost:8050/sse"
   ```

## Usage

### Automatic Memory (No Commands Needed)

The system automatically saves:
- All user messages
- All assistant responses
- Complete conversation turns

There's no need to explicitly ask Claude to remember anything.

### Retrieving Memories

You can still use commands to access memories:

- "What do you remember about [topic]?"
- "Do we have any previous conversations about [topic]?"
- "What did I tell you about [topic] before?"

## Technical Details

The automatic memory system uses:

1. **auto_memory.py**: Enhanced MCP server with automatic message saving
2. **auto_start.sh**: Helper script to start the server and Claude Code
3. **auto_memory_plugin.py**: Conceptual plugin for message interception

## Limitations

Current limitations include:

1. Messages are saved as individual entries, not threaded conversations
2. No automatic summarization of lengthy conversation history
3. The polling mechanism is conceptual and would require Claude Code API access to fully implement

## Maintenance

To check if the memory server is running:
```bash
pgrep -f "python.*auto_memory.py"
```

To stop the memory server:
```bash
pkill -f "python.*auto_memory.py"
```

To view logs:
```bash
cat ~/mcp-mem0/mcp_server.log
```