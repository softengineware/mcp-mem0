"""
Unit tests for input validators.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validators import (
    sanitize_text,
    validate_memory_content,
    validate_search_query,
    validate_limit,
    contains_suspicious_patterns,
    contains_sql_patterns,
    validate_conversation_data,
    validate_config
)
import constants as const


class TestSanitizeText:
    """Test text sanitization."""
    
    def test_removes_null_bytes(self):
        text = "Hello\x00World"
        assert sanitize_text(text) == "Hello World"
    
    def test_escapes_html(self):
        text = "<script>alert('xss')</script>"
        assert "&lt;script&gt;" in sanitize_text(text)
    
    def test_normalizes_whitespace(self):
        text = "Hello    World\n\n\n\nTest"
        result = sanitize_text(text)
        assert "Hello World" in result
        assert result.count('\n') <= 2
    
    def test_empty_string(self):
        assert sanitize_text("") == ""
        assert sanitize_text(None) == ""


class TestValidateMemoryContent:
    """Test memory content validation."""
    
    def test_valid_content(self):
        is_valid, error = validate_memory_content("This is a valid memory")
        assert is_valid is True
        assert error is None
    
    def test_empty_content(self):
        is_valid, error = validate_memory_content("")
        assert is_valid is False
        assert error == const.ERROR_EMPTY_MEMORY
    
    def test_content_too_large(self):
        large_content = "x" * (const.MAX_MEMORY_SIZE + 1)
        is_valid, error = validate_memory_content(large_content)
        assert is_valid is False
        assert error == const.ERROR_MEMORY_TOO_LARGE
    
    def test_suspicious_content(self):
        is_valid, error = validate_memory_content("<script>alert('xss')</script>")
        assert is_valid is False
        assert "suspicious patterns" in error


class TestValidateSearchQuery:
    """Test search query validation."""
    
    def test_valid_query(self):
        is_valid, error = validate_search_query("find python tutorials")
        assert is_valid is True
        assert error is None
    
    def test_empty_query(self):
        is_valid, error = validate_search_query("")
        assert is_valid is False
        assert error == const.ERROR_EMPTY_QUERY
    
    def test_query_too_long(self):
        long_query = "x" * (const.MAX_QUERY_LENGTH + 1)
        is_valid, error = validate_search_query(long_query)
        assert is_valid is False
        assert "too long" in error
    
    def test_sql_injection(self):
        is_valid, error = validate_search_query("'; DROP TABLE users; --")
        assert is_valid is False
        assert "invalid characters" in error


class TestValidateLimit:
    """Test limit validation."""
    
    def test_valid_limits(self):
        for limit in [1, 5, 10, 50, 100]:
            is_valid, error = validate_limit(limit)
            assert is_valid is True
            assert error is None
    
    def test_invalid_type(self):
        is_valid, error = validate_limit("10")
        assert is_valid is False
        assert "must be an integer" in error
    
    def test_too_small(self):
        is_valid, error = validate_limit(0)
        assert is_valid is False
        assert "at least 1" in error
    
    def test_too_large(self):
        is_valid, error = validate_limit(const.MAX_SEARCH_LIMIT + 1)
        assert is_valid is False
        assert f"cannot exceed {const.MAX_SEARCH_LIMIT}" in error


class TestPatternDetection:
    """Test suspicious pattern detection."""
    
    def test_script_patterns(self):
        patterns = [
            "<script>alert('test')</script>",
            "javascript:void(0)",
            "<div onclick='malicious()'>",
            "eval(something)",
        ]
        for pattern in patterns:
            assert contains_suspicious_patterns(pattern) is True
    
    def test_safe_patterns(self):
        patterns = [
            "This is a normal text",
            "Learning JavaScript programming",
            "onclick is an event handler",
        ]
        for pattern in patterns:
            assert contains_suspicious_patterns(pattern) is False
    
    def test_sql_injection_patterns(self):
        patterns = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "UNION SELECT * FROM passwords",
            "'; DELETE FROM accounts; --"
        ]
        for pattern in patterns:
            assert contains_sql_patterns(pattern) is True
    
    def test_safe_sql_keywords(self):
        patterns = [
            "I want to select the best option",
            "Let's create something new",
            "Update me on the progress",
        ]
        for pattern in patterns:
            assert contains_sql_patterns(pattern) is False


class TestValidateConversationData:
    """Test conversation validation."""
    
    def test_valid_conversation(self):
        is_valid, error = validate_conversation_data(
            "What is Python?",
            "Python is a programming language."
        )
        assert is_valid is True
        assert error is None
    
    def test_empty_user_message(self):
        is_valid, error = validate_conversation_data(
            "",
            "This is a response"
        )
        assert is_valid is False
        assert "User message:" in error
    
    def test_conversation_too_large(self):
        large_message = "x" * const.MAX_MEMORY_SIZE
        is_valid, error = validate_conversation_data(
            large_message,
            large_message
        )
        assert is_valid is False
        assert "too large" in error


class TestValidateConfig:
    """Test configuration validation."""
    
    def test_valid_config(self):
        config = {
            "llm": {"provider": "openai"},
            "embedder": {"provider": "openai"},
            "vector_store": {"provider": "supabase"}
        }
        is_valid, errors = validate_config(config)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_missing_fields(self):
        config = {"llm": {"provider": "openai"}}
        is_valid, errors = validate_config(config)
        assert is_valid is False
        assert any("embedder" in e for e in errors)
        assert any("vector_store" in e for e in errors)
    
    def test_invalid_provider(self):
        config = {
            "llm": {"provider": "invalid_provider"},
            "embedder": {"provider": "openai"},
            "vector_store": {"provider": "supabase"}
        }
        is_valid, errors = validate_config(config)
        assert is_valid is False
        assert any("Unsupported LLM provider" in e for e in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])