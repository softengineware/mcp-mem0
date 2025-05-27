# Automatic Memory for Claude Code

This extension to MCP-Mem0 provides automatic conversation memory, enabling Claude Code to remember important conversations and information across sessions.

## How It Works

The automatic memory system provides:

1. **Manual Conversation Saving**: Save important Q&A exchanges on demand
2. **Semantic Memory Search**: Find relevant information from past conversations
3. **Conversation Summaries**: Get overviews of your interaction history
4. **Persistent Knowledge Base**: Build a personal knowledge repository over time

## Quick Start

### 1. Automated Setup

```bash
cd ~/mcp-mem0
./auto_start.sh
```

This will:
- Start the enhanced memory server
- Configure Claude Code automatically
- Launch Claude Code with memory capabilities

### 2. Interactive Setup

For a guided setup with troubleshooting:

```bash
python ~/mcp-mem0/src/claude_integration.py
```

## Usage in Claude Code

### Saving Conversations

After any important exchange, simply ask:
- "Save this conversation"
- "Remember this discussion"
- "Add this to my memory"

Claude will use the `save_conversation_turn` tool to save the Q&A pair.

### Searching Memories

Access your saved knowledge:
- "What do you remember about Python decorators?"
- "Search my memories for Docker setup"
- "Find our previous discussion about API design"

### Viewing All Memories

- "Show me all my memories"
- "What have we discussed before?"
- "Display my saved conversations"

### Getting Summaries

- "Summarize today's conversations"
- "What topics have we covered?"
- "Show memory statistics"

## Available Tools

The auto memory server provides these MCP tools:

1. **save_conversation_turn(user_message, assistant_message)**
   - Saves a complete Q&A exchange
   - Perfect for important discussions

2. **save_memory(text)**
   - Saves specific information
   - Good for notes, reminders, facts

3. **search_memories(query, limit)**
   - Semantic search through memories
   - Returns most relevant results

4. **get_all_memories()**
   - Retrieves all saved memories
   - Limited to 100 most recent

5. **get_conversation_summary(time_range)**
   - Provides conversation statistics
   - Shows common topics and activity

6. **auto_save_message(role, content)**
   - Used internally for automatic saving
   - Supports individual messages or full turns

## Configuration

### Claude Code Settings

Add to your Claude Code configuration:

```json
{
  "mcpServers": {
    "auto_mem0": {
      "command": "python",
      "args": ["~/mcp-mem0/src/auto_memory.py"],
      "env": {
        "TRANSPORT": "stdio"
      }
    }
  }
}
```

### Custom Instructions (Optional)

For better auto-memory behavior, add custom instructions to Claude Code that remind it to:
1. Suggest saving important conversations
2. Search memories before answering complex questions
3. Proactively use memory features

## Advanced Features

### Programmatic Access

Developers can use the auto memory client:

```python
from auto_memory_plugin import AutoMemoryClient

client = AutoMemoryClient()
await client.save_conversation_turn(user_msg, assistant_msg)
memories = await client.get_recent_memories(limit=10)
```

### Conversation Cache

The system maintains a local cache at `~/.mcp-mem0/conversation_cache.json` for quick access to recent conversations.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Claude Code    │────▶│  MCP Auto Memory │────▶│    Mem0     │
│   (Client)      │◀────│    (Server)      │◀────│  (Storage)  │
└─────────────────┘     └──────────────────┘     └─────────────┘
        │                                                  │
        └──────────── User Interactions ───────────────────┘
```

## Troubleshooting

### Server Won't Start
- Check port 8050: `lsof -i :8050`
- Verify environment variables
- Check logs: `cat ~/mcp-mem0/mcp_server.log`

### Connection Issues
- Ensure server is running: `pgrep -f auto_memory.py`
- Restart Claude Code after configuration
- Verify MCP configuration

### Memory Not Saving
- Check Mem0 API keys
- Verify database connection
- Look for errors in server logs

For detailed troubleshooting:
```bash
python ~/mcp-mem0/src/claude_integration.py --troubleshoot
```

## Limitations

1. **Manual Trigger**: Conversations must be explicitly saved (no automatic interception)
2. **Context Window**: Very long conversations may be truncated
3. **No Threading**: Memories are individual entries, not conversation threads
4. **Search Accuracy**: Depends on Mem0's embedding quality

## Future Enhancements

- [ ] Automatic conversation detection and saving
- [ ] Conversation threading and context preservation  
- [ ] Memory export/import functionality
- [ ] Scheduled memory summaries
- [ ] Memory categories and tags
- [ ] Privacy controls and encryption