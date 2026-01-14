"""Routes package."""

from src.routes.chat import router as chat_router
from src.routes.ingest import router as ingest_router
from src.routes.query import router as query_router

__all__ = ["chat_router", "ingest_router", "query_router"]