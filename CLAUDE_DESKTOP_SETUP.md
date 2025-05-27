# Claude Desktop Configuration for MCP-Mem0

## Configuration File Location

The Claude Desktop configuration file should be placed in the Claude application folder. The exact location varies by system, but you can find it by looking for the Claude Desktop app configuration directory.

## Configuration Options

You have two options for configuring MCP-Mem0 with Claude Desktop:

### Option 1: Standard Memory Server

Add this to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "mcp-mem0": {
      "command": "python",
      "args": ["/Users/branchechols/mcp-mem0/src/main.py"],
      "env": {
        "TRANSPORT": "stdio",
        "LLM_PROVIDER": "openai",
        "LLM_BASE_URL": "https://api.openai.com/v1",
        "LLM_API_KEY": "YOUR_OPENAI_API_KEY",
        "LLM_CHOICE": "gpt-4o-mini",
        "EMBEDDING_MODEL_CHOICE": "text-embedding-3-small",
        "DATABASE_URL": "YOUR_SUPABASE_DATABASE_URL"
      }
    }
  }
}
```

### Option 2: Auto Memory Server

For automatic conversation memory, use this configuration:

```json
{
  "mcpServers": {
    "mcp-mem0-auto": {
      "command": "python",
      "args": ["/Users/branchechols/mcp-mem0/src/auto_memory.py"],
      "env": {
        "TRANSPORT": "stdio",
        "LLM_PROVIDER": "openai",
        "LLM_BASE_URL": "https://api.openai.com/v1",
        "LLM_API_KEY": "YOUR_OPENAI_API_KEY",
        "LLM_CHOICE": "gpt-4o-mini",
        "EMBEDDING_MODEL_CHOICE": "text-embedding-3-small",
        "DATABASE_URL": "YOUR_SUPABASE_DATABASE_URL"
      }
    }
  }
}
```

### Option 3: Both Servers

You can also run both servers simultaneously:

```json
{
  "mcpServers": {
    "mcp-mem0": {
      "command": "python",
      "args": ["/Users/branchechols/mcp-mem0/src/main.py"],
      "env": {
        "TRANSPORT": "stdio",
        "LLM_PROVIDER": "openai",
        "LLM_BASE_URL": "https://api.openai.com/v1",
        "LLM_API_KEY": "YOUR_OPENAI_API_KEY",
        "LLM_CHOICE": "gpt-4o-mini",
        "EMBEDDING_MODEL_CHOICE": "text-embedding-3-small",
        "DATABASE_URL": "YOUR_SUPABASE_DATABASE_URL"
      }
    },
    "mcp-mem0-auto": {
      "command": "python",
      "args": ["/Users/branchechols/mcp-mem0/src/auto_memory.py"],
      "env": {
        "TRANSPORT": "stdio",
        "LLM_PROVIDER": "openai",
        "LLM_BASE_URL": "https://api.openai.com/v1",
        "LLM_API_KEY": "YOUR_OPENAI_API_KEY",
        "LLM_CHOICE": "gpt-4o-mini",
        "EMBEDDING_MODEL_CHOICE": "text-embedding-3-small",
        "DATABASE_URL": "YOUR_SUPABASE_DATABASE_URL"
      }
    }
  }
}
```

## Configuration Steps

1. **Replace placeholder values**:
   - `YOUR_OPENAI_API_KEY`: Your actual OpenAI API key
   - `YOUR_SUPABASE_DATABASE_URL`: Your Supabase PostgreSQL connection string

2. **Update paths if needed**:
   - Replace `/Users/branchechols/mcp-mem0` with your actual project path

3. **Alternative LLM providers**:
   - For Ollama: Change `LLM_PROVIDER` to `"ollama"` and remove `LLM_API_KEY`
   - For OpenRouter: Keep `LLM_PROVIDER` as `"openrouter"` and use your OpenRouter API key

4. **Save and restart**:
   - Save the configuration file
   - Restart Claude Desktop to apply the changes

## Using with .env File

If you prefer to use the .env file instead of hardcoding values:

```json
{
  "mcpServers": {
    "mcp-mem0": {
      "command": "bash",
      "args": ["-c", "cd /Users/branchechols/mcp-mem0 && source .env && python src/main.py"],
      "env": {
        "TRANSPORT": "stdio"
      }
    }
  }
}
```

## Verification

After configuration, restart Claude Desktop and check if the MCP server is available:
- You should see memory-related tools in Claude's tool list
- Try commands like "Save this to memory" or "What do you remember?"

## Troubleshooting

If the server doesn't connect:
1. Check the logs in Claude Desktop's console
2. Verify Python path is correct
3. Ensure all environment variables are set
4. Check that the database connection is working
5. Try running the server manually first: `cd /Users/branchechols/mcp-mem0 && python src/main.py`