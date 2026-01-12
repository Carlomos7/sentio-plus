"""Routes package."""

from src.routes.ingest import router as ingest_router
from src.routes.chat import router as chat_router

__all__ = ["ingest_router", "chat_router"]