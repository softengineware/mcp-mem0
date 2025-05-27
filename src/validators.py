"""
Input validation and sanitization utilities for MCP-Mem0.

This module provides validation functions to ensure data integrity
and security throughout the application.
"""

import re
import html
from typing import Any, Dict, List, Optional, Tuple
import constants as const
from exceptions import ValidationError


def sanitize_text(text: str) -> str:
    """
    Sanitize text input by removing potentially harmful content.
    
    Args:
        text: Raw text input
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove any null bytes
    text = text.replace('\x00', '')
    
    # Escape HTML entities to prevent injection
    text = html.escape(text)
    
    # Remove excessive whitespace while preserving single spaces
    text = ' '.join(text.split())
    
    # Limit consecutive newlines to 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def validate_memory_content(content: str) -> Tuple[bool, Optional[str]]:
    """
    Validate memory content before saving.
    
    Args:
        content: Memory content to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not content or not content.strip():
        return False, const.ERROR_EMPTY_MEMORY
    
    if len(content) < const.MIN_MEMORY_SIZE:
        return False, f"Memory content too short (minimum {const.MIN_MEMORY_SIZE} character)"
    
    if len(content) > const.MAX_MEMORY_SIZE:
        return False, const.ERROR_MEMORY_TOO_LARGE
    
    # Check for potential security issues
    if contains_suspicious_patterns(content):
        return False, "Memory content contains suspicious patterns"
    
    return True, None


def validate_search_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Validate search query input.
    
    Args:
        query: Search query to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, const.ERROR_EMPTY_QUERY
    
    if len(query) > const.MAX_QUERY_LENGTH:
        return False, f"Query too long (maximum {const.MAX_QUERY_LENGTH} characters)"
    
    # Check for SQL injection patterns
    if contains_sql_patterns(query):
        return False, "Query contains invalid characters"
    
    return True, None


def validate_limit(limit: int) -> Tuple[bool, Optional[str]]:
    """
    Validate pagination limit.
    
    Args:
        limit: Number of results to return
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(limit, int):
        return False, "Limit must be an integer"
    
    if limit < 1:
        return False, "Limit must be at least 1"
    
    if limit > const.MAX_SEARCH_LIMIT:
        return False, f"Limit cannot exceed {const.MAX_SEARCH_LIMIT}"
    
    return True, None


def contains_suspicious_patterns(text: str) -> bool:
    """
    Check if text contains suspicious patterns that might indicate
    malicious content.
    
    Args:
        text: Text to check
        
    Returns:
        True if suspicious patterns found
    """
    # Check for script tags (even escaped)
    script_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',  # Event handlers like onclick=
        r'eval\s*\(',
        r'expression\s*\(',
    ]
    
    for pattern in script_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def contains_sql_patterns(text: str) -> bool:
    """
    Check for potential SQL injection patterns.
    
    Args:
        text: Text to check
        
    Returns:
        True if SQL patterns found
    """
    sql_patterns = [
        r';\s*(DROP|DELETE|TRUNCATE|ALTER|CREATE)\s+',
        r'--\s*$',  # SQL comment at end
        r"'\s*OR\s*'?\d*'\s*=\s*'?\d*",  # OR '1'='1'
        r'UNION\s+SELECT',
        r'INSERT\s+INTO',
        r'UPDATE\s+\w+\s+SET',
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def validate_conversation_data(user_message: str, assistant_message: str) -> Tuple[bool, Optional[str]]:
    """
    Validate conversation turn data.
    
    Args:
        user_message: User's message
        assistant_message: Assistant's response
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate user message
    is_valid, error = validate_memory_content(user_message)
    if not is_valid:
        return False, f"User message: {error}"
    
    # Validate assistant message
    is_valid, error = validate_memory_content(assistant_message)
    if not is_valid:
        return False, f"Assistant message: {error}"
    
    # Check combined size
    total_size = len(user_message) + len(assistant_message)
    if total_size > const.MAX_MEMORY_SIZE * 2:
        return False, "Conversation too large to save"
    
    return True, None


def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    required_fields = ["llm", "embedder", "vector_store"]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required configuration: {field}")
    
    # Validate LLM configuration
    if "llm" in config:
        llm_config = config["llm"]
        if "provider" not in llm_config:
            errors.append("LLM configuration missing provider")
        elif llm_config["provider"] not in const.SUPPORTED_LLM_PROVIDERS:
            errors.append(f"Unsupported LLM provider: {llm_config['provider']}")
    
    # Validate vector store configuration
    if "vector_store" in config:
        vector_config = config["vector_store"]
        if "provider" not in vector_config:
            errors.append("Vector store configuration missing provider")
        elif vector_config["provider"] not in const.SUPPORTED_VECTOR_PROVIDERS:
            errors.append(f"Unsupported vector provider: {vector_config['provider']}")
    
    return len(errors) == 0, errors