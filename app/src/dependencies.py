"""Dependency injection for FastAPI routes."""

from functools import lru_cache

from src.config.logging import get_logger
from src.config.settings import Settings, get_settings
from src.services.ingest import IngestionService
from src.services.vector_store import VectorStore
from src.services.chat import ChatService

logger = get_logger(__name__)

def get_config() -> Settings:
    """Get cached settings instance for dependency injection."""
    return get_settings()

# TODO: Implement actual dependencies below

@lru_cache
def get_vector_store() -> VectorStore:
    '''Provide ChromaDB vector store instance'''
    settings = get_settings()
    settings = get_settings()
    return VectorStore(
        client_type=settings.chroma_client_type,
        collection_name=settings.chroma_collection_name,
        persist_path=settings.chroma_persist_path,
        host=settings.chroma_host,
        port=settings.chroma_port,
    )

def get_ingest_service() -> IngestionService:
    """Provide ingest service instance."""
    settings = get_settings()
    return IngestionService(
        vector_store=get_vector_store(),
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

def get_chat_service() -> ChatService:
    """Provide chat service instance."""
    settings = get_settings()
    return ChatService(
        vector_store=get_vector_store(),
        settings=settings,
    )