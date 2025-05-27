"""
Centralized configuration constants for MCP-Mem0.

This module contains all configuration defaults and constants used
throughout the application to ensure consistency.
"""

import os
from pathlib import Path

# Server Configuration
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8050
DEFAULT_TRANSPORT = "sse"

# Memory Configuration
DEFAULT_USER_ID = "user"
DEFAULT_COLLECTION_NAME = "mem0_memories"
DEFAULT_SEARCH_LIMIT = 5
MAX_SEARCH_LIMIT = 100
DEFAULT_GET_ALL_LIMIT = 100

# Content Limits
MAX_MEMORY_SIZE = 10000  # 10KB in characters
MIN_MEMORY_SIZE = 1
MAX_QUERY_LENGTH = 500

# Model Configuration Defaults
DEFAULT_LLM_TEMPERATURE = 0.2
DEFAULT_LLM_MAX_TOKENS = 2000

# OpenAI Defaults
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_OPENAI_EMBEDDING_DIMS = 1536

# Ollama Defaults
DEFAULT_OLLAMA_MODEL = "llama2"
DEFAULT_OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_OLLAMA_EMBEDDING_DIMS = 768

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
CACHE_DIR = Path.home() / ".mcp-mem0"
CONVERSATION_CACHE_FILE = CACHE_DIR / "conversation_cache.json"

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# API Configuration
API_TIMEOUT = 30  # seconds
API_RETRY_COUNT = 3
API_RETRY_DELAY = 1  # seconds

# Auto Memory Configuration
AUTO_MEMORY_POLL_INTERVAL = 2  # seconds
AUTO_MEMORY_HOST = "localhost"

# Environment Variable Names
ENV_TRANSPORT = "TRANSPORT"
ENV_HOST = "HOST"
ENV_PORT = "PORT"
ENV_LLM_PROVIDER = "LLM_PROVIDER"
ENV_LLM_API_KEY = "LLM_API_KEY"
ENV_LLM_BASE_URL = "LLM_BASE_URL"
ENV_LLM_CHOICE = "LLM_CHOICE"
ENV_EMBEDDING_MODEL_CHOICE = "EMBEDDING_MODEL_CHOICE"
ENV_DATABASE_URL = "DATABASE_URL"
ENV_LOG_LEVEL = "LOG_LEVEL"

# Supported Providers
SUPPORTED_LLM_PROVIDERS = ["openai", "openrouter", "ollama"]
SUPPORTED_VECTOR_PROVIDERS = ["supabase", "chroma", "qdrant"]

# Error Messages
ERROR_EMPTY_MEMORY = "Cannot save empty memory"
ERROR_MEMORY_TOO_LARGE = f"Memory content too large (max {MAX_MEMORY_SIZE} characters)"
ERROR_EMPTY_QUERY = "Search query cannot be empty"
ERROR_INVALID_LIMIT = f"Limit must be between 1 and {MAX_SEARCH_LIMIT}"
ERROR_MISSING_CONFIG = "Required configuration missing: {}"
ERROR_INVALID_PROVIDER = "Invalid provider: {}"
ERROR_CONNECTION_FAILED = "Failed to connect to {}: {}"