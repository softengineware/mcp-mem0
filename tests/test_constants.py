"""
Unit tests for constants and configuration.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import constants as const


class TestServerConfiguration:
    """Test server configuration constants."""
    
    def test_default_values(self):
        assert const.DEFAULT_HOST == "0.0.0.0"
        assert const.DEFAULT_PORT == 8050
        assert const.DEFAULT_TRANSPORT == "sse"
    
    def test_port_consistency(self):
        # Ensure port is consistent across all usages
        assert const.DEFAULT_PORT == 8050
        assert isinstance(const.DEFAULT_PORT, int)


class TestMemoryConfiguration:
    """Test memory-related constants."""
    
    def test_user_defaults(self):
        assert const.DEFAULT_USER_ID == "user"
        assert const.DEFAULT_COLLECTION_NAME == "mem0_memories"
    
    def test_search_limits(self):
        assert const.DEFAULT_SEARCH_LIMIT == 5
        assert const.MAX_SEARCH_LIMIT == 100
        assert const.DEFAULT_GET_ALL_LIMIT == 100
        
        # Ensure defaults don't exceed max
        assert const.DEFAULT_SEARCH_LIMIT <= const.MAX_SEARCH_LIMIT
        assert const.DEFAULT_GET_ALL_LIMIT <= const.MAX_SEARCH_LIMIT
    
    def test_content_limits(self):
        assert const.MAX_MEMORY_SIZE == 10000
        assert const.MIN_MEMORY_SIZE == 1
        assert const.MAX_QUERY_LENGTH == 500
        
        # Ensure min is less than max
        assert const.MIN_MEMORY_SIZE < const.MAX_MEMORY_SIZE


class TestModelConfiguration:
    """Test model configuration defaults."""
    
    def test_model_defaults(self):
        assert const.DEFAULT_LLM_TEMPERATURE == 0.2
        assert const.DEFAULT_LLM_MAX_TOKENS == 2000
    
    def test_openai_defaults(self):
        assert const.DEFAULT_OPENAI_MODEL == "gpt-4o-mini"
        assert const.DEFAULT_OPENAI_EMBEDDING_MODEL == "text-embedding-3-small"
        assert const.DEFAULT_OPENAI_EMBEDDING_DIMS == 1536
    
    def test_ollama_defaults(self):
        assert const.DEFAULT_OLLAMA_MODEL == "llama2"
        assert const.DEFAULT_OLLAMA_EMBEDDING_MODEL == "nomic-embed-text"
        assert const.DEFAULT_OLLAMA_EMBEDDING_DIMS == 768


class TestPaths:
    """Test path constants."""
    
    def test_project_paths(self):
        assert const.PROJECT_ROOT.exists()
        assert const.PROJECT_ROOT.is_dir()
        
        # Check if we're in the right directory structure
        assert (const.PROJECT_ROOT / "src").exists()
    
    def test_cache_paths(self):
        assert const.CACHE_DIR == Path.home() / ".mcp-mem0"
        assert const.CONVERSATION_CACHE_FILE == const.CACHE_DIR / "conversation_cache.json"


class TestEnvironmentVariables:
    """Test environment variable names."""
    
    def test_env_var_names(self):
        expected_vars = [
            "TRANSPORT", "HOST", "PORT", "LLM_PROVIDER",
            "LLM_API_KEY", "LLM_BASE_URL", "LLM_CHOICE",
            "EMBEDDING_MODEL_CHOICE", "DATABASE_URL", "LOG_LEVEL"
        ]
        
        actual_vars = [
            const.ENV_TRANSPORT, const.ENV_HOST, const.ENV_PORT,
            const.ENV_LLM_PROVIDER, const.ENV_LLM_API_KEY,
            const.ENV_LLM_BASE_URL, const.ENV_LLM_CHOICE,
            const.ENV_EMBEDDING_MODEL_CHOICE, const.ENV_DATABASE_URL,
            const.ENV_LOG_LEVEL
        ]
        
        assert actual_vars == expected_vars


class TestSupportedProviders:
    """Test supported provider lists."""
    
    def test_llm_providers(self):
        assert "openai" in const.SUPPORTED_LLM_PROVIDERS
        assert "openrouter" in const.SUPPORTED_LLM_PROVIDERS
        assert "ollama" in const.SUPPORTED_LLM_PROVIDERS
        assert len(const.SUPPORTED_LLM_PROVIDERS) == 3
    
    def test_vector_providers(self):
        assert "supabase" in const.SUPPORTED_VECTOR_PROVIDERS
        assert "chroma" in const.SUPPORTED_VECTOR_PROVIDERS
        assert "qdrant" in const.SUPPORTED_VECTOR_PROVIDERS
        assert len(const.SUPPORTED_VECTOR_PROVIDERS) == 3


class TestErrorMessages:
    """Test error message constants."""
    
    def test_error_messages_exist(self):
        assert const.ERROR_EMPTY_MEMORY
        assert const.ERROR_MEMORY_TOO_LARGE
        assert const.ERROR_EMPTY_QUERY
        assert const.ERROR_INVALID_LIMIT
        assert const.ERROR_MISSING_CONFIG
        assert const.ERROR_INVALID_PROVIDER
        assert const.ERROR_CONNECTION_FAILED
    
    def test_error_message_formatting(self):
        # Messages with placeholders
        assert "{}" in const.ERROR_MISSING_CONFIG
        assert "{}" in const.ERROR_INVALID_PROVIDER
        assert "{}" in const.ERROR_CONNECTION_FAILED
        
        # Messages with values
        assert str(const.MAX_MEMORY_SIZE) in const.ERROR_MEMORY_TOO_LARGE
        assert str(const.MAX_SEARCH_LIMIT) in const.ERROR_INVALID_LIMIT


class TestAPIConfiguration:
    """Test API-related constants."""
    
    def test_api_settings(self):
        assert const.API_TIMEOUT == 30
        assert const.API_RETRY_COUNT == 3
        assert const.API_RETRY_DELAY == 1
        
        # Ensure reasonable values
        assert 10 <= const.API_TIMEOUT <= 120
        assert 1 <= const.API_RETRY_COUNT <= 5
        assert 0.5 <= const.API_RETRY_DELAY <= 5


class TestAutoMemoryConfiguration:
    """Test auto memory specific constants."""
    
    def test_auto_memory_settings(self):
        assert const.AUTO_MEMORY_POLL_INTERVAL == 2
        assert const.AUTO_MEMORY_HOST == "localhost"
        
        # Ensure reasonable poll interval
        assert 1 <= const.AUTO_MEMORY_POLL_INTERVAL <= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])