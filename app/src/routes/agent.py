"""Agent routes."""

from fastapi import APIRouter, Depends, HTTPException

from src.config.logging import get_logger
from src.dependencies import get_agent_service
from src.schemas.api import QueryRequest, AgentResponse
from src.services.agent import AgentService

logger = get_logger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("", response_model=AgentResponse)
def agent_query(
    request: QueryRequest,
    agent_service: AgentService = Depends(get_agent_service),
) -> AgentResponse:
    """Query using the LangChain agent with tools."""
    logger.info(f"Agent query: {request.question[:50]}...")

    try:
        result = agent_service.invoke(question=request.question)
        return AgentResponse(**result)
    except Exception as e:
        logger.error(f"Agent query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
