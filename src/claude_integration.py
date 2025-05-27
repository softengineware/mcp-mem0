#!/usr/bin/env python3
"""
Claude Code Integration for MCP-Mem0 Auto Memory

This script provides integration instructions and utilities for using
MCP-Mem0's automatic memory features with Claude Code.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_step(number, text):
    """Print a numbered step."""
    print(f"{BOLD}{GREEN}Step {number}:{RESET} {text}")

def print_command(command):
    """Print a command to run."""
    print(f"{YELLOW}  $ {command}{RESET}")

def print_info(text):
    """Print info text."""
    print(f"{BLUE}ℹ️  {text}{RESET}")

def print_success(text):
    """Print success message."""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    """Print error message."""
    print(f"{RED}❌ {text}{RESET}")

def check_mcp_server():
    """Check if the MCP server is running."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "python.*auto_memory.py"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def get_claude_config():
    """Get the Claude Code configuration for auto memory."""
    config = {
        "mcpServers": {
            "auto_mem0": {
                "command": "python",
                "args": [str(Path.home() / "mcp-mem0" / "src" / "auto_memory.py")],
                "env": {
                    "TRANSPORT": "stdio"
                }
            }
        }
    }
    return config

def create_custom_instructions():
    """Create custom instructions for Claude Code."""
    return """
# Auto Memory Instructions

You have access to MCP-Mem0's automatic memory features through these tools:

1. **save_conversation_turn** - Save important Q&A exchanges
2. **save_memory** - Save specific information to remember
3. **search_memories** - Search through saved memories
4. **get_all_memories** - View all saved memories
5. **get_conversation_summary** - Get a summary of recent conversations

## Automatic Memory Behavior

After each significant conversation:
1. Suggest saving important exchanges using: "Would you like me to save this conversation to your long-term memory?"
2. If the user agrees, use the `save_conversation_turn` tool
3. For technical discussions, automatically save key decisions and solutions

## Memory Best Practices

- Save conversations about project decisions, technical solutions, and user preferences
- Before answering complex questions, search memories for relevant context
- Periodically remind users they can view their saved memories
"""

def setup_auto_memory():
    """Interactive setup for auto memory."""
    print_header("MCP-Mem0 Auto Memory Setup")
    
    # Step 1: Check if MCP server is running
    print_step(1, "Checking MCP server status...")
    if check_mcp_server():
        print_success("MCP server is running")
    else:
        print_info("MCP server is not running")
        print_command("cd ~/mcp-mem0 && ./start_mcp.sh")
        print()
    
    # Step 2: Show Claude Code configuration
    print_step(2, "Claude Code Configuration")
    print_info("Add this to your Claude Code settings:")
    print()
    config = get_claude_config()
    print(json.dumps(config, indent=2))
    print()
    
    # Step 3: Show custom instructions
    print_step(3, "Custom Instructions (Optional)")
    print_info("Add these instructions to Claude Code for better auto-memory behavior:")
    print()
    print(create_custom_instructions())
    print()
    
    # Step 4: Usage examples
    print_step(4, "Usage Examples")
    print_info("Try these commands in Claude Code:\n")
    
    examples = [
        ("Save this conversation", "Uses save_conversation_turn to save the current exchange"),
        ("What do you remember about Python?", "Searches memories for Python-related content"),
        ("Show me all my memories", "Displays all saved memories"),
        ("Summarize today's conversations", "Gets a summary of recent activity")
    ]
    
    for example, description in examples:
        print(f"  {BOLD}You:{RESET} {example}")
        print(f"  {BLUE}→ {description}{RESET}\n")
    
    # Step 5: Advanced features
    print_step(5, "Advanced Features")
    print_info("For developers who want more control:\n")
    
    print("  • Direct tool access:")
    print("    - save_memory(text='Important info')")
    print("    - search_memories(query='project setup')")
    print("    - save_conversation_turn(user_message='...', assistant_message='...')")
    print()
    
    print("  • Programmatic usage:")
    print_command("python ~/mcp-mem0/src/auto_memory_plugin.py")
    print()
    
    print_success("Setup complete! Start using Claude Code with automatic memory.")

def show_troubleshooting():
    """Show troubleshooting tips."""
    print_header("Troubleshooting")
    
    issues = [
        {
            "problem": "MCP server won't start",
            "solutions": [
                "Check if port 8050 is already in use: lsof -i :8050",
                "Verify environment variables are set correctly",
                "Check logs: cat ~/mcp-mem0/mcp_server.log"
            ]
        },
        {
            "problem": "Claude Code can't connect to MCP server",
            "solutions": [
                "Ensure the server is running: pgrep -f auto_memory.py",
                "Verify Claude Code configuration is correct",
                "Try restarting Claude Code after configuration"
            ]
        },
        {
            "problem": "Memories aren't being saved",
            "solutions": [
                "Check if Mem0 is properly configured with API keys",
                "Verify database connection (PostgreSQL or SQLite)",
                "Look for errors in the MCP server logs"
            ]
        }
    ]
    
    for issue in issues:
        print(f"{BOLD}{issue['problem']}{RESET}")
        for solution in issue['solutions']:
            print(f"  • {solution}")
        print()

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--troubleshoot":
        show_troubleshooting()
    else:
        setup_auto_memory()

if __name__ == "__main__":
    main()