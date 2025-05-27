"""
MCP-Mem0: Long-term memory MCP server for AI agents.

This package provides MCP server implementations integrated with Mem0
for persistent memory capabilities.
"""

__version__ = "0.1.0"
__author__ = "MCP-Mem0 Contributors"

# Export main components
from .utils import get_mem0_client

__all__ = ["get_mem0_client"]