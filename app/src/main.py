"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.logging import get_logger
from src.config.settings import get_settings
from src.dependencies import get_vector_store
from src.routes import ingest_router
from src.routes import query_router


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

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(query_router)

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
