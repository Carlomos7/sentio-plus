"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config.logging import get_logger
from src.config.settings import get_settings
from src.dependencies import get_vector_store
from src.routes import ingest_router


logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup and cleanup on shutdown."""
    logger.info("Starting Sentio+ API")
    logger.info(f"Chroma path: {settings.chroma_persist_path.resolve()}")
    logger.info(f"Chroma client type: {settings.chroma_client_type.value}")
    logger.info(f"Bedrock model: {settings.llm_model}")

    # ChromaDB client
    vector_store = get_vector_store()
    app.state.vector_store = vector_store
    # TODO: LLM client (bedrock)

    yield

    logger.info("Shutting down Sentio+ API")


app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.version,
    lifespan=lifespan,
)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Sentio+ RAG API",
        "docs": "/docs",
        "health": "/health",
    }

# Register routers
app.include_router(ingest_router)

@app.get("/health")
def health_check():
    """Health check endpoint."""
    vector_store = get_vector_store()
    return {
        "status": "healthy",
        "service": settings.app_name,
        "documents": vector_store.count(),
        "data_dir": settings.data_dir,
    }
