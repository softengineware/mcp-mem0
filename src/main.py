from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv
from mem0 import Memory
import asyncio
import json
import os
import logging
import time
from typing import Optional

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
    validate_limit
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
        yield Mem0Context(mem0_client=mem0_client)
    finally:
        # No explicit cleanup needed for the Mem0 client
        pass

# Initialize FastMCP server with the Mem0 client as context
mcp = FastMCP(
    "mcp-mem0",
    description="MCP server for long term memory storage and retrieval with Mem0",
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
        # Validate and sanitize input
        is_valid, error = validate_memory_content(text)
        if not is_valid:
            raise ValidationError(error)
        
        # Sanitize the text
        sanitized_text = sanitize_text(text)
        
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        messages = [{"role": "user", "content": sanitized_text}]
        
        try:
            mem0_client.add(messages, user_id=const.DEFAULT_USER_ID)
            logger.info(f"Successfully saved memory for user {const.DEFAULT_USER_ID}")
            return f"Successfully saved memory: {text[:100]}..." if len(text) > 100 else f"Successfully saved memory: {text}"
        except Exception as e:
            logger.error(f"Failed to save memory: {str(e)}")
            raise MemorySaveError(f"Failed to save memory: {str(e)}")
            
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        return f"Validation error: {str(e)}"
    except MemorySaveError as e:
        return f"Error saving memory: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in save_memory: {str(e)}")
        return f"Unexpected error: {str(e)}"

@mcp.tool()
async def get_all_memories(ctx: Context) -> str:
    """Get all stored memories for the user.
    
    Call this tool when you need complete context of all previously memories.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client

    Returns a JSON formatted list of all stored memories, including when they were created
    and their content. Results are paginated with a default of 50 items per page.
    """
    try:
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        
        try:
            memories = mem0_client.get_all(user_id=const.DEFAULT_USER_ID)
            
            if isinstance(memories, dict) and "results" in memories:
                flattened_memories = [memory["memory"] for memory in memories["results"]]
            else:
                flattened_memories = memories if memories else []
            
            logger.info(f"Retrieved {len(flattened_memories)} memories for user {const.DEFAULT_USER_ID}")
            return json.dumps(flattened_memories, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {str(e)}")
            raise MemoryRetrievalError(f"Failed to retrieve memories: {str(e)}")
            
    except MemoryRetrievalError as e:
        return f"Error retrieving memories: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in get_all_memories: {str(e)}")
        return f"Unexpected error: {str(e)}"

@mcp.tool()
async def search_memories(ctx: Context, query: str, limit: int = const.DEFAULT_SEARCH_LIMIT) -> str:
    """Search memories using semantic search.

    This tool should be called to find relevant information from your memory. Results are ranked by relevance.
    Always search your memories before making decisions to ensure you leverage your existing knowledge.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        query: Search query string describing what you're looking for. Can be natural language.
        limit: Maximum number of results to return (default: 3)
    """
    try:
        # Validate query
        is_valid, error = validate_search_query(query)
        if not is_valid:
            raise ValidationError(error)
        
        # Validate limit
        is_valid, error = validate_limit(limit)
        if not is_valid:
            raise ValidationError(error)
        
        # Sanitize query
        sanitized_query = sanitize_text(query)
        
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        
        try:
            memories = mem0_client.search(sanitized_query, user_id=const.DEFAULT_USER_ID, limit=limit)
            
            if isinstance(memories, dict) and "results" in memories:
                flattened_memories = [memory["memory"] for memory in memories["results"]]
            else:
                flattened_memories = memories if memories else []
            
            logger.info(f"Search returned {len(flattened_memories)} results for query: {query}")
            return json.dumps(flattened_memories, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to search memories: {str(e)}")
            raise MemorySearchError(f"Failed to search memories: {str(e)}")
            
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        return f"Validation error: {str(e)}"
    except MemorySearchError as e:
        return f"Error searching memories: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in search_memories: {str(e)}")
        return f"Unexpected error: {str(e)}"

@mcp.tool()
async def health_check(ctx: Context) -> str:
    """Check the health status of the MCP server and its dependencies.
    
    Returns a JSON object with the health status of various components.
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {
            "mcp_server": "healthy",
            "mem0_client": "unknown",
            "database": "unknown",
            "llm_provider": "unknown"
        },
        "version": "0.1.0"
    }
    
    try:
        # Check Mem0 client
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        if mem0_client:
            # Try a simple operation to verify it's working
            try:
                # This is a lightweight operation
                test_memories = mem0_client.get_all(user_id="health_check_test", limit=1)
                health_status["components"]["mem0_client"] = "healthy"
                health_status["components"]["database"] = "healthy"  # If get_all works, DB is healthy
            except Exception as e:
                health_status["components"]["mem0_client"] = "unhealthy"
                health_status["components"]["database"] = "unhealthy"
                health_status["status"] = "unhealthy"
                health_status["error"] = str(e)
        else:
            health_status["components"]["mem0_client"] = "not_initialized"
            health_status["status"] = "unhealthy"
    
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
        logger.error(f"Health check failed: {str(e)}")
    
    return json.dumps(health_status, indent=2)

@mcp.tool()
async def get_server_info(ctx: Context) -> str:
    """Get information about the MCP server.
    
    Returns server configuration and runtime information.
    """
    try:
        server_info = {
            "name": "mcp-mem0",
            "version": "0.1.0",
            "description": "MCP server for long term memory storage and retrieval with Mem0",
            "configuration": {
                "transport": os.getenv(const.ENV_TRANSPORT, const.DEFAULT_TRANSPORT),
                "host": os.getenv(const.ENV_HOST, const.DEFAULT_HOST),
                "port": int(os.getenv(const.ENV_PORT, str(const.DEFAULT_PORT))),
                "llm_provider": os.getenv(const.ENV_LLM_PROVIDER, "not_set"),
                "default_user_id": const.DEFAULT_USER_ID,
                "max_memory_size": const.MAX_MEMORY_SIZE,
                "max_search_limit": const.MAX_SEARCH_LIMIT
            },
            "available_tools": [
                "save_memory",
                "get_all_memories",
                "search_memories",
                "health_check",
                "get_server_info"
            ]
        }
        return json.dumps(server_info, indent=2)
    except Exception as e:
        logger.error(f"Error getting server info: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

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
