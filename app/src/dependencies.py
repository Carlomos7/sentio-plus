"""Dependency injection for fastapi routes."""

from functools import lru_cache
from src.config.settings import Settings, get_settings

def get_config() -> Settings:
    """Get cached settings instance for dependency injection."""
    return get_settings()

# TODO: Implement actual dependencies below

@lru_cache
def get_vector_store():
    '''Provide ChromaDB vector store instance'''
    raise NotIImplementedError("VectorStore dependency not implemented yet.")

@lru_cache
def get_llm():
    '''Provide LLM instance'''
    raise NotIImplementedError("LLM dependency not implemented yet.")