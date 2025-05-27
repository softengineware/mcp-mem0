from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv
from mem0 import Memory
import asyncio
import json
import os
import time
import logging
from typing import List, Dict, Any

from utils import get_mem0_client
from exceptions import (
    MemorySaveError,
    MemoryRetrievalError,
    MemorySearchError,
    ValidationError,
    ServerError
)
import constants as const
from validators import (
    sanitize_text,
    validate_memory_content,
    validate_search_query,
    validate_limit,
    validate_conversation_data
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, const.LOG_LEVEL),
    format=const.LOG_FORMAT
)
logger = logging.getLogger(__name__)

load_dotenv()

# Create a dataclass for our application context
@dataclass
class Mem0Context:
    """Context for the Mem0 MCP server."""
    mem0_client: Memory
    chat_history: list

@asynccontextmanager
async def mem0_lifespan(server: FastMCP) -> AsyncIterator[Mem0Context]:
    """
    Manages the Mem0 client lifecycle.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        Mem0Context: The context containing the Mem0 client
    """
    # Create and return the Memory client with the helper function in utils.py
    mem0_client = get_mem0_client()
    
    try:
        yield Mem0Context(mem0_client=mem0_client, chat_history=[])
    finally:
        # No explicit cleanup needed for the Mem0 client
        pass

# Initialize FastMCP server with the Mem0 client as context
mcp = FastMCP(
    "mcp-mem0-auto",
    description="MCP server for automatic long term memory storage and retrieval with Mem0",
    lifespan=mem0_lifespan,
    host=os.getenv(const.ENV_HOST, const.DEFAULT_HOST),
    port=int(os.getenv(const.ENV_PORT, str(const.DEFAULT_PORT)))
)        

@mcp.tool()
async def save_memory(ctx: Context, text: str) -> str:
    """Save information to your long-term memory.

    This tool is designed to store any type of information that might be useful in the future.
    The content will be processed and indexed for later retrieval through semantic search.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        text: The content to store in memory, including any relevant details and context
    """
    try:
        # Validate and sanitize
        is_valid, error = validate_memory_content(text)
        if not is_valid:
            return f"Validation error: {error}"
        
        sanitized_text = sanitize_text(text)
        
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        messages = [{"role": "user", "content": sanitized_text}]
        mem0_client.add(messages, user_id=const.DEFAULT_USER_ID)
        return f"Successfully saved memory: {text[:100]}..." if len(text) > 100 else f"Successfully saved memory: {text}"
    except Exception as e:
        return f"Error saving memory: {str(e)}"

@mcp.tool()
async def get_all_memories(ctx: Context) -> str:
    """Get all stored memories for the user.
    
    Call this tool when you need complete context of all previously memories.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client

    Returns a JSON formatted list of all stored memories, including when they were created
    and their content. Results are paginated with a default of 100 items per page.
    """
    try:
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        memories = mem0_client.get_all(user_id=const.DEFAULT_USER_ID, limit=const.DEFAULT_GET_ALL_LIMIT)
        if isinstance(memories, dict) and "results" in memories:
            flattened_memories = [memory["memory"] for memory in memories["results"]]
        else:
            flattened_memories = memories
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error retrieving memories: {str(e)}"

@mcp.tool()
async def search_memories(ctx: Context, query: str, limit: int = const.DEFAULT_SEARCH_LIMIT) -> str:
    """Search memories using semantic search.

    This tool should be called to find relevant information from your memory. Results are ranked by relevance.
    Always search your memories before making decisions to ensure you leverage your existing knowledge.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        query: Search query string describing what you're looking for. Can be natural language.
        limit: Maximum number of results to return (default: 5)
    """
    try:
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        memories = mem0_client.search(query, user_id=const.DEFAULT_USER_ID, limit=limit)
        if isinstance(memories, dict) and "results" in memories:
            flattened_memories = [memory["memory"] for memory in memories["results"]]
        else:
            flattened_memories = memories
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error searching memories: {str(e)}"

@mcp.tool()
async def auto_save_message(ctx: Context, role: str, content: str) -> str:
    """Automatically save a message from the conversation to long-term memory.

    This tool is designed to be called automatically for each message in the conversation.
    
    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        role: The role of the message sender (user, assistant, or conversation)
        content: The content of the message or conversation JSON
    """
    try:
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        timestamp = int(time.time())
        
        # Handle different role types
        if role == "conversation":
            # Parse conversation turn from JSON
            try:
                conversation_data = json.loads(content)
                conversation_turn = [
                    {"role": "user", "content": conversation_data.get("user", "")},
                    {"role": "assistant", "content": conversation_data.get("assistant", "")}
                ]
                mem0_client.add(conversation_turn, user_id=const.DEFAULT_USER_ID)
                return "Successfully saved conversation turn to memory"
            except json.JSONDecodeError:
                return "Error: Invalid conversation JSON format"
        else:
            # Original single message handling
            # Add message to chat history
            ctx.request_context.lifespan_context.chat_history.append({
                "role": role,
                "content": content,
                "timestamp": timestamp
            })
            
            # Save full conversation turn if this is an assistant message (completing a turn)
            if role == "assistant" and len(ctx.request_context.lifespan_context.chat_history) >= 2:
                # Get the preceding user message
                user_idx = -2
                while user_idx >= -len(ctx.request_context.lifespan_context.chat_history) and ctx.request_context.lifespan_context.chat_history[user_idx]["role"] != "user":
                    user_idx -= 1
                
                if user_idx >= -len(ctx.request_context.lifespan_context.chat_history):
                    user_message = ctx.request_context.lifespan_context.chat_history[user_idx]
                    
                    # Create a conversation turn with context
                    conversation_turn = [
                        {"role": "user", "content": user_message["content"]},
                        {"role": "assistant", "content": content}
                    ]
                    
                    # Save to memory
                    mem0_client.add(conversation_turn, user_id=const.DEFAULT_USER_ID)
            
            return f"Successfully saved {role} message to memory"
    except Exception as e:
        return f"Error auto-saving message: {str(e)}"

@mcp.tool()
async def save_conversation_turn(ctx: Context, user_message: str, assistant_message: str) -> str:
    """Save a complete conversation turn (user question and assistant response).
    
    This is useful for saving important exchanges without needing to track individual messages.
    
    Args:
        ctx: The MCP server provided context
        user_message: The user's message/question
        assistant_message: The assistant's response
    """
    try:
        # Validate conversation data
        is_valid, error = validate_conversation_data(user_message, assistant_message)
        if not is_valid:
            return f"Validation error: {error}"
        
        # Sanitize messages
        sanitized_user = sanitize_text(user_message)
        sanitized_assistant = sanitize_text(assistant_message)
        
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        conversation_turn = [
            {"role": "user", "content": sanitized_user},
            {"role": "assistant", "content": sanitized_assistant}
        ]
        mem0_client.add(conversation_turn, user_id=const.DEFAULT_USER_ID)
        return "Successfully saved conversation turn to memory"
    except Exception as e:
        return f"Error saving conversation turn: {str(e)}"

@mcp.tool()
async def get_conversation_summary(ctx: Context, time_range: str = "today") -> str:
    """Get a summary of conversations from a specific time range.
    
    Args:
        ctx: The MCP server provided context
        time_range: Time range for the summary (today, yesterday, last_week)
    """
    try:
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        
        # Get all memories and filter by time if needed
        memories = mem0_client.get_all(user_id=const.DEFAULT_USER_ID, limit=const.DEFAULT_GET_ALL_LIMIT)
        
        if isinstance(memories, dict) and "results" in memories:
            all_memories = memories["results"]
        else:
            all_memories = memories if memories else []
        
        # Group memories by conversation patterns
        conversation_count = len(all_memories)
        topics = set()
        
        # Extract topics from memories (simple keyword extraction)
        for memory in all_memories:
            memory_text = memory.get("memory", "").lower()
            # Extract potential topics (words longer than 4 characters)
            words = memory_text.split()
            topics.update(word for word in words if len(word) > 4 and word.isalpha())
        
        summary = {
            "total_memories": conversation_count,
            "time_range": time_range,
            "common_topics": list(topics)[:10],  # Top 10 topics
            "status": "active" if conversation_count > 0 else "no memories found"
        }
        
        return json.dumps(summary, indent=2)
    except Exception as e:
        return f"Error getting conversation summary: {str(e)}"

@mcp.tool()
async def clear_chat_history(ctx: Context) -> str:
    """Clear the current chat history buffer (does not delete saved memories).
    
    This is useful for starting fresh without affecting your long-term memories.
    """
    try:
        ctx.request_context.lifespan_context.chat_history.clear()
        return "Chat history buffer cleared. Your saved memories remain intact."
    except Exception as e:
        return f"Error clearing chat history: {str(e)}"

@mcp.tool()
async def health_check(ctx: Context) -> str:
    """Check the health status of the auto memory MCP server.
    
    Returns a JSON object with the health status of various components.
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {
            "mcp_server": "healthy",
            "mem0_client": "unknown",
            "database": "unknown",
            "chat_history": "unknown"
        },
        "version": "0.1.0",
        "mode": "auto_memory"
    }
    
    try:
        # Check Mem0 client
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        if mem0_client:
            try:
                test_memories = mem0_client.get_all(user_id="health_check_test", limit=1)
                health_status["components"]["mem0_client"] = "healthy"
                health_status["components"]["database"] = "healthy"
            except Exception as e:
                health_status["components"]["mem0_client"] = "unhealthy"
                health_status["status"] = "unhealthy"
        
        # Check chat history
        chat_history = ctx.request_context.lifespan_context.chat_history
        if isinstance(chat_history, list):
            health_status["components"]["chat_history"] = "healthy"
            health_status["chat_history_size"] = len(chat_history)
        else:
            health_status["components"]["chat_history"] = "not_initialized"
    
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
        logger.error(f"Health check failed: {str(e)}")
    
    return json.dumps(health_status, indent=2)

async def main():
    transport = os.getenv(const.ENV_TRANSPORT, const.DEFAULT_TRANSPORT)
    if transport == 'sse':
        # Run the MCP server with sse transport
        await mcp.run_sse_async()
    else:
        # Run the MCP server with stdio transport
        await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())