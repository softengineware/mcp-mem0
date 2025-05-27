#!/usr/bin/env python3
"""
Auto Memory Plugin for Claude Code

This plugin provides automatic memory saving functionality through slash commands.
Since Claude Code doesn't expose a direct API for message interception, this
implementation uses a client-side approach with slash commands.
"""

import asyncio
import aiohttp
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.expanduser('~/mcp-mem0/auto_memory.log'))
    ]
)
logger = logging.getLogger(__name__)

# Configuration
MCP_BASE_URL = "http://localhost:8050"
CONVERSATION_CACHE_FILE = os.path.expanduser("~/.mcp-mem0/conversation_cache.json")

class AutoMemoryClient:
    """Client for interacting with the MCP-Mem0 auto memory server."""
    
    def __init__(self):
        self.session = None
        self.conversation_cache = self._load_conversation_cache()
        
    def _load_conversation_cache(self) -> Dict:
        """Load conversation cache from file."""
        if os.path.exists(CONVERSATION_CACHE_FILE):
            try:
                with open(CONVERSATION_CACHE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading conversation cache: {e}")
        return {"conversations": [], "last_save": None}
    
    def _save_conversation_cache(self):
        """Save conversation cache to file."""
        os.makedirs(os.path.dirname(CONVERSATION_CACHE_FILE), exist_ok=True)
        try:
            with open(CONVERSATION_CACHE_FILE, 'w') as f:
                json.dump(self.conversation_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving conversation cache: {e}")
    
    async def save_conversation_turn(self, user_message: str, assistant_message: str) -> bool:
        """Save a complete conversation turn to memory."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Create the conversation turn
            conversation_turn = {
                "timestamp": datetime.now().isoformat(),
                "user": user_message,
                "assistant": assistant_message
            }
            
            # Add to cache
            self.conversation_cache["conversations"].append(conversation_turn)
            self.conversation_cache["last_save"] = datetime.now().isoformat()
            self._save_conversation_cache()
            
            # Call the MCP server to save the conversation
            async with self.session.post(
                f"{MCP_BASE_URL}/call-tool",
                json={
                    "name": "auto_save_message",
                    "arguments": {
                        "role": "conversation",
                        "content": json.dumps(conversation_turn)
                    }
                },
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    logger.info("Successfully saved conversation turn")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to save conversation: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error saving conversation turn: {e}")
            return False
    
    async def get_recent_memories(self, limit: int = 10) -> List[Dict]:
        """Get recent memories from the server."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.post(
                f"{MCP_BASE_URL}/call-tool",
                json={
                    "name": "get_all_memories",
                    "arguments": {}
                },
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    memories = json.loads(result.get("result", "[]"))
                    return memories[-limit:] if len(memories) > limit else memories
                else:
                    logger.error(f"Failed to get memories: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting memories: {e}")
            return []
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()


class ConversationMonitor:
    """Monitor for conversation patterns to enable automatic saving."""
    
    def __init__(self):
        self.client = AutoMemoryClient()
        self.pending_user_message = None
        
    def format_slash_command(self, user_input: str, assistant_response: str) -> str:
        """Format a slash command to save the conversation."""
        # Escape any quotes in the messages
        user_input = user_input.replace('"', '\\"')
        assistant_response = assistant_response.replace('"', '\\"')
        
        return f'/save_turn "{user_input}" "{assistant_response}"'
    
    def create_auto_save_instruction(self) -> str:
        """Create an instruction for automatic memory saving."""
        return (
            "\n\n---\n"
            "💡 **Auto Memory Tip**: To automatically save this conversation, "
            "copy and paste the following command:\n\n"
            "```\n/auto_save\n```\n\n"
            "This will save our entire conversation to your long-term memory."
        )


async def setup_slash_commands():
    """Set up slash commands for Claude Code."""
    commands = [
        {
            "name": "auto_save",
            "description": "Automatically save the current conversation to memory",
            "handler": "save_current_conversation"
        },
        {
            "name": "save_turn",
            "description": "Save a specific conversation turn",
            "parameters": ["user_message", "assistant_message"],
            "handler": "save_conversation_turn"
        },
        {
            "name": "toggle_auto_memory",
            "description": "Toggle automatic memory saving on/off",
            "handler": "toggle_auto_memory"
        },
        {
            "name": "memory_status",
            "description": "Check auto memory status and recent saves",
            "handler": "check_memory_status"
        }
    ]
    
    logger.info("Slash commands configured for Claude Code integration")
    return commands


def create_claude_config():
    """Create a Claude Code configuration snippet for auto memory."""
    config = {
        "mcpServers": {
            "auto_mem0": {
                "command": "python",
                "args": [os.path.expanduser("~/mcp-mem0/src/auto_memory.py")],
                "env": {
                    "TRANSPORT": "stdio"
                }
            }
        },
        "customInstructions": {
            "autoMemory": (
                "After each conversation turn, remind the user they can save it "
                "using the /auto_save command. For important conversations, "
                "suggest using auto memory to preserve the discussion."
            )
        }
    }
    
    return config


def main():
    """Main entry point for the auto memory plugin."""
    print("\n=== MCP-Mem0 Auto Memory Plugin ===")
    print("\nThis plugin enables automatic conversation saving in Claude Code.")
    print("\nSetup Instructions:")
    print("1. Ensure the MCP-Mem0 server is running (./start_mcp.sh)")
    print("2. Add the following to your Claude Code config:")
    print("\n" + json.dumps(create_claude_config(), indent=2))
    print("\n3. Use these commands in Claude Code:")
    print("   /auto_save - Save the current conversation")
    print("   /memory_status - Check memory status")
    print("   /toggle_auto_memory - Toggle auto-save on/off")
    print("\nThe plugin is now configured. Start using Claude Code with auto memory!\n")


if __name__ == "__main__":
    main()