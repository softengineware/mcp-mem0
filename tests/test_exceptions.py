"""
Unit tests for custom exceptions.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from exceptions import (
    MCPMem0Error,
    ConfigurationError,
    MemoryOperationError,
    MemorySaveError,
    MemoryRetrievalError,
    MemorySearchError,
    ValidationError,
    ConnectionError,
    DatabaseConnectionError,
    LLMProviderError,
    AuthenticationError,
    RateLimitError,
    ServerError,
    TransportError
)


class TestExceptionHierarchy:
    """Test exception inheritance hierarchy."""
    
    def test_base_exception(self):
        with pytest.raises(MCPMem0Error):
            raise MCPMem0Error("Base error")
    
    def test_configuration_error(self):
        with pytest.raises(MCPMem0Error):
            raise ConfigurationError("Config error")
        
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Config error")
    
    def test_memory_operation_errors(self):
        # Base memory operation error
        with pytest.raises(MemoryOperationError):
            raise MemoryOperationError("Memory op error")
        
        # Specific memory errors should be caught by base class
        with pytest.raises(MemoryOperationError):
            raise MemorySaveError("Save error")
        
        with pytest.raises(MemoryOperationError):
            raise MemoryRetrievalError("Retrieval error")
        
        with pytest.raises(MemoryOperationError):
            raise MemorySearchError("Search error")
    
    def test_connection_errors(self):
        # Base connection error
        with pytest.raises(ConnectionError):
            raise ConnectionError("Connection error")
        
        # Specific connection errors
        with pytest.raises(ConnectionError):
            raise DatabaseConnectionError("DB error")
        
        with pytest.raises(ConnectionError):
            raise LLMProviderError("LLM error")
    
    def test_server_errors(self):
        # Base server error
        with pytest.raises(ServerError):
            raise ServerError("Server error")
        
        # Specific server errors
        with pytest.raises(ServerError):
            raise TransportError("Transport error")


class TestExceptionMessages:
    """Test exception message handling."""
    
    def test_error_messages(self):
        error_msg = "Test error message"
        
        exceptions_to_test = [
            MCPMem0Error,
            ConfigurationError,
            MemorySaveError,
            ValidationError,
            DatabaseConnectionError,
            RateLimitError
        ]
        
        for exc_class in exceptions_to_test:
            try:
                raise exc_class(error_msg)
            except exc_class as e:
                assert str(e) == error_msg
    
    def test_empty_message(self):
        try:
            raise ValidationError("")
        except ValidationError as e:
            assert str(e) == ""
    
    def test_no_message(self):
        try:
            raise AuthenticationError()
        except AuthenticationError as e:
            assert str(e) == ""


class TestExceptionUsage:
    """Test practical usage of exceptions."""
    
    def test_configuration_validation(self):
        def validate_config(config):
            if not config.get("api_key"):
                raise ConfigurationError("API key is required")
            if not config.get("database_url"):
                raise ConfigurationError("Database URL is required")
            return True
        
        # Valid config
        assert validate_config({"api_key": "key", "database_url": "url"})
        
        # Invalid config
        with pytest.raises(ConfigurationError, match="API key is required"):
            validate_config({"database_url": "url"})
    
    def test_memory_operations(self):
        def save_memory(content):
            if not content:
                raise ValidationError("Content cannot be empty")
            if len(content) > 1000:
                raise MemorySaveError("Content too large")
            return True
        
        # Valid save
        assert save_memory("Valid content")
        
        # Validation error
        with pytest.raises(ValidationError):
            save_memory("")
        
        # Save error
        with pytest.raises(MemorySaveError):
            save_memory("x" * 1001)
    
    def test_connection_handling(self):
        def connect_to_database(url):
            if not url:
                raise ConfigurationError("Database URL not provided")
            if "invalid" in url:
                raise DatabaseConnectionError(f"Failed to connect to {url}")
            return True
        
        # Valid connection
        assert connect_to_database("postgresql://localhost/db")
        
        # Configuration error
        with pytest.raises(ConfigurationError):
            connect_to_database("")
        
        # Connection error
        with pytest.raises(DatabaseConnectionError):
            connect_to_database("invalid://url")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])