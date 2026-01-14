"""Dependency injection for FastAPI routes."""

from functools import lru_cache

from src.config.logging import get_logger
from src.config.settings import Settings, get_settings
from src.services.agent import AgentService
from src.services.ingest import IngestionService
from src.services.llm import LLMClient
from src.services.rag import RAGService
from src.services.vector_store import VectorStore

logger = get_logger(__name__)

def get_config() -> Settings:
    """Get cached settings instance for dependency injection."""
    return get_settings()

# TODO: Implement actual dependencies below

@lru_cache
def get_vector_store() -> VectorStore:
    '''Provide ChromaDB vector store instance'''
    settings = get_settings()
    return VectorStore(
        client_type=settings.chroma_client_type,
        collection_name=settings.chroma_collection_name,
        persist_path=settings.chroma_persist_path,
        host=settings.chroma_host,
        port=settings.chroma_port,
        chroma_cloud_api_key=settings.chroma_cloud_api_key,
        chroma_tenant_id=settings.chroma_tenant_id,
        chroma_database=settings.chroma_database,
    )

def get_ingest_service() -> IngestionService:
    """Provide ingest service instance."""
    settings = get_settings()
    return IngestionService(
        vector_store=get_vector_store(),
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

@lru_cache
def get_llm() -> LLMClient:
    """Provide LLM client instance."""
    settings = get_settings()
    return LLMClient(
        provider=settings.llm_provider,
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        aws_region=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )

def get_rag_service() -> RAGService:
    """Provide RAG service instance."""
    settings = get_settings()
    return RAGService(
        llm=get_llm(),
        vector_store=get_vector_store(),
        top_k=settings.retrieval_top_k,
        threshold=settings.retrieval_threshold,
    )


@lru_cache
def get_agent_service() -> AgentService:
    """Provide LangChain agent service instance."""
    settings = get_settings()
    return AgentService(
        vector_store=get_vector_store(),
        provider=settings.llm_provider,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        aws_region=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )