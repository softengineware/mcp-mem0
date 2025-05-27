from mem0 import Memory
import os
import logging
from typing import Optional

from exceptions import ConfigurationError, ConnectionError, LLMProviderError

# Configure logging
logger = logging.getLogger(__name__)

# Custom instructions for memory processing
# These aren't being used right now but Mem0 does support adding custom prompting
# for handling memory retrieval and processing.
CUSTOM_INSTRUCTIONS = """
Extract the Following Information:  

- Key Information: Identify and save the most important details.
- Context: Capture the surrounding context to understand the memory's relevance.
- Connections: Note any relationships to other topics or memories.
- Importance: Highlight why this information might be valuable in the future.
- Source: Record where this information came from when applicable.
"""

def get_mem0_client() -> Memory:
    """
    Initialize and return a configured Mem0 Memory client.
    
    Returns:
        Memory: Configured Memory client instance
        
    Raises:
        ConfigurationError: If required configuration is missing
        LLMProviderError: If LLM provider configuration is invalid
        ConnectionError: If connection to services fails
    """
    # Get LLM provider and configuration
    llm_provider = os.getenv('LLM_PROVIDER')
    llm_api_key = os.getenv('LLM_API_KEY')
    llm_model = os.getenv('LLM_CHOICE')
    embedding_model = os.getenv('EMBEDDING_MODEL_CHOICE')
    
    # Validate required configuration
    if not llm_provider:
        raise ConfigurationError("LLM_PROVIDER environment variable is required")
    
    if llm_provider in ['openai', 'openrouter'] and not llm_api_key:
        raise ConfigurationError(f"LLM_API_KEY is required for {llm_provider} provider")
    
    if not llm_model:
        raise ConfigurationError("LLM_CHOICE environment variable is required")
    
    # Initialize config dictionary
    config = {}
    
    # Configure LLM based on provider
    if llm_provider == 'openai' or llm_provider == 'openrouter':
        config["llm"] = {
            "provider": "openai",
            "config": {
                "model": llm_model,
                "temperature": 0.2,
                "max_tokens": 2000,
            }
        }
        
        # Set API key in environment if not already set
        if llm_api_key and not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = llm_api_key
            
        # For OpenRouter, set the specific API key
        if llm_provider == 'openrouter' and llm_api_key:
            os.environ["OPENROUTER_API_KEY"] = llm_api_key
    
    elif llm_provider == 'ollama':
        config["llm"] = {
            "provider": "ollama",
            "config": {
                "model": llm_model,
                "temperature": 0.2,
                "max_tokens": 2000,
            }
        }
        
        # Set base URL for Ollama if provided
        llm_base_url = os.getenv('LLM_BASE_URL')
        if llm_base_url:
            config["llm"]["config"]["ollama_base_url"] = llm_base_url
    
    # Configure embedder based on provider
    if llm_provider == 'openai':
        config["embedder"] = {
            "provider": "openai",
            "config": {
                "model": embedding_model or "text-embedding-3-small",
                "embedding_dims": 1536  # Default for text-embedding-3-small
            }
        }
        
        # Set API key in environment if not already set
        if llm_api_key and not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = llm_api_key
    
    elif llm_provider == 'ollama':
        config["embedder"] = {
            "provider": "ollama",
            "config": {
                "model": embedding_model or "nomic-embed-text",
                "embedding_dims": 768  # Default for nomic-embed-text
            }
        }
        
        # Set base URL for Ollama if provided
        embedding_base_url = os.getenv('LLM_BASE_URL')
        if embedding_base_url:
            config["embedder"]["config"]["ollama_base_url"] = embedding_base_url
    
    # Configure Supabase vector store
    database_url = os.environ.get('DATABASE_URL', '')
    if not database_url:
        raise ConfigurationError("DATABASE_URL environment variable is required")
    
    config["vector_store"] = {
        "provider": "supabase",
        "config": {
            "connection_string": database_url,
            "collection_name": "mem0_memories",
            "embedding_model_dims": 1536 if llm_provider == "openai" else 768
        }
    }

    # config["custom_fact_extraction_prompt"] = CUSTOM_INSTRUCTIONS
    
    # Create and return the Memory client
    try:
        logger.info(f"Initializing Mem0 client with {llm_provider} provider")
        client = Memory.from_config(config)
        logger.info("Successfully initialized Mem0 client")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Mem0 client: {str(e)}")
        raise ConnectionError(f"Failed to initialize Mem0 client: {str(e)}")