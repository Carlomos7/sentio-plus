"""Routes package."""

from src.routes.agent import router as agent_router
from src.routes.ingest import router as ingest_router
from src.routes.query import router as query_router

__all__ = ["agent_router", "ingest_router", "query_router"]