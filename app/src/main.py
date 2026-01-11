'''FastAPI application entry point.'''
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config.settings import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    '''Initialize resources on startup and cleanup on shutdown.'''
    print("🚀 Starting Sentio Plus application...")
    print(f"Chroma Path: {settings.chroma_persist_path}")
    print(f"Bedrock Model ID: {settings.bedrock_model_id}")
    
    # TODO: ChromaDB client
    # TODO: LLM client (bedrock)
    
    yield
    
    print("🛑 Shutting down Sentio Plus application...")

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.version,
    lifespan=lifespan
)

@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Sentio+ RAG API",
        "docs": "/docs",
        "health": "/health",
    }

@app.get("/health")
def health_check():
    '''Health check endpoint.'''
    return {"status": "healthy", "service": "Sentio Plus RAG API"}