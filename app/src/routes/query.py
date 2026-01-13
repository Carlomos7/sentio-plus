"""Query routes."""

from fastapi import APIRouter, Depends, HTTPException

from src.config.logging import get_logger
from src.dependencies import get_llm, get_rag_service
from src.schemas.api import ModelInfoResponse, QueryRequest, QueryResponse
from src.services.llm import LLMClient
from src.services.rag import RAGService

logger = get_logger(__name__)

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def query(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> QueryResponse:
    """Query the RAG system with a question."""
    logger.info(f"Query: {request.question[:50]}...")

    try:
        result = rag_service.query(
            question=request.question,
            filter_by_source=request.filter_by_source,
        )
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model", response_model=ModelInfoResponse)
def get_model_info(
    llm: LLMClient = Depends(get_llm),
) -> ModelInfoResponse:
    """Get current LLM model information."""
    return ModelInfoResponse(**llm.get_model_info())