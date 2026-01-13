"""Tests for services."""

from pathlib import Path

from src.config.logging import get_logger, setup_logging
from src.config.settings import ChromaClientType, get_settings
from src.services.ingest import IngestionService
from src.services.vector_store import VectorStore

setup_logging()
logger = get_logger(__name__)
settings = get_settings()


def test_logger():
    """Test logging configuration."""
    logger.debug("This is a debug message for testing.")
    logger.info("This is an info message for testing.")
    logger.warning("This is a warning message for testing.")
    logger.error("This is an error message for testing.")
    logger.critical("This is a critical message for testing.")
    logger.info(settings.model_dump())  # Pydantic v2
    assert True


def test_vector_store_persistent():
    """Test VectorStore with persistent client."""
    vector_store = VectorStore(
        client_type=ChromaClientType.PERSISTENT,
        collection_name="test_persistent",
        persist_path=settings.chroma_persist_path / "test",
    )
    assert vector_store.count() >= 0
    logger.info(f"Persistent store initialized: {vector_store.count()} docs")


def test_vector_store_http():
    """Test VectorStore with HTTP client."""
    vector_store = VectorStore(
        client_type=ChromaClientType.HTTP,
        collection_name="test_http",
        host=settings.chroma_host,
        port=settings.chroma_port,
    )
    assert vector_store.count() >= 0
    logger.info(f"HTTP store initialized: {vector_store.count()} docs")


def test_ingestion():
    """Test CSV ingestion."""
    logger.info("Starting ingestion test")

    # Resolve data path
    root_dir = Path(__file__).parent.parent.parent
    data_path = root_dir / "notebooks" / "data" / "processed" / "THIS_ONE.csv"
    logger.info(f"Data path: {data_path}")

    # Use settings to determine client type
    if settings.chroma_client_type == ChromaClientType.HTTP:
        vector_store = VectorStore(
            client_type=ChromaClientType.HTTP,
            collection_name="test_ingest",
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
    else:
        vector_store = VectorStore(
            client_type=ChromaClientType.PERSISTENT,
            collection_name="test_ingest",
            persist_path=settings.chroma_persist_path / "test",
        )

    ingest_service = IngestionService(
        vector_store=vector_store,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    result = ingest_service.ingest_csv(
        file_path=data_path,
        clear_existing=True,
        limit=settings.ingest_limit,
    )

    logger.info(f"Ingestion complete: {result}")
    assert result["chunks_added"] > 0


if __name__ == "__main__":
    test_logger()
    # test_vector_store_persistent()  # Uncomment to test persistent
    # test_vector_store_http()        # Uncomment to test HTTP
    test_ingestion()