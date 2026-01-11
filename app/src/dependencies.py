"""Dependency injection for fastapi routes."""

from functools import lru_cache
from src.config.settings import Settings, get_settings
from src.services.vector_store import VectorStore

def get_config() -> Settings:
    """Get cached settings instance for dependency injection."""
    return get_settings()

# TODO: Implement actual dependencies below

@lru_cache
def get_vector_store():
    '''Provide ChromaDB vector store instance'''
    settings = get_settings()
    return VectorStore(
        #client_type=settings.chroma_client_type,
        collection_name=settings.chroma_collection_name,
        path=settings.chroma_persist_path,
        host=settings.chroma_host,
        port=settings.chroma_port,
    )

@lru_cache
def get_llm():
    '''Provide LLM instance'''
    raise NotImplementedError("LLM dependency not implemented yet.")