"""Routes package."""

from src.routes.ingest import router as ingest_router
from src.routes.query import router as query_router

__all__ = ["ingest_router", "query_router"]