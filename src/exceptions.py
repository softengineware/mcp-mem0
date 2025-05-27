"""
Custom exceptions for MCP-Mem0 server.

This module defines all custom exceptions used throughout the application
for better error handling and debugging.
"""

class MCPMem0Error(Exception):
    """Base exception for all MCP-Mem0 errors."""
    pass


class ConfigurationError(MCPMem0Error):
    """Raised when there's an error in configuration."""
    pass


class MemoryOperationError(MCPMem0Error):
    """Base exception for memory operation errors."""
    pass


class MemorySaveError(MemoryOperationError):
    """Raised when saving memory fails."""
    pass


class MemoryRetrievalError(MemoryOperationError):
    """Raised when retrieving memory fails."""
    pass


class MemorySearchError(MemoryOperationError):
    """Raised when searching memory fails."""
    pass


class ValidationError(MCPMem0Error):
    """Raised when input validation fails."""
    pass


class ConnectionError(MCPMem0Error):
    """Raised when connection to external services fails."""
    pass


class DatabaseConnectionError(ConnectionError):
    """Raised when database connection fails."""
    pass


class LLMProviderError(ConnectionError):
    """Raised when LLM provider connection fails."""
    pass


class AuthenticationError(MCPMem0Error):
    """Raised when authentication fails."""
    pass


class RateLimitError(MCPMem0Error):
    """Raised when rate limit is exceeded."""
    pass


class ServerError(MCPMem0Error):
    """Raised for general server errors."""
    pass


class TransportError(ServerError):
    """Raised when transport protocol errors occur."""
    pass