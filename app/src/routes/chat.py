"""Chat routes for LangChain agent."""

from fastapi import APIRouter, Depends, HTTPException

from src.config.logging import get_logger
from src.dependencies import get_agent_service
from src.schemas.api import ChatRequest, ChatResponse
from src.services.agent import AgentService

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    agent_service: AgentService = Depends(get_agent_service),
) -> ChatResponse:
    """Chat with the agent.
    
    The agent uses tools to search reviews, get stats, and list apps.
    Conversation history is maintained per thread_id.
    """
    logger.info(f"Chat request [thread={request.thread_id}]: {request.message[:50]}...")

    try:
        result = agent_service.invoke(
            message=request.message,
            thread_id=request.thread_id,
        )
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{thread_id}")
def get_history(
    thread_id: str,
    agent_service: AgentService = Depends(get_agent_service),
) -> dict:
    """Get conversation history for a thread."""
    logger.info(f"History request for thread: {thread_id}")
    
    history = agent_service.get_conversation_history(thread_id)
    return {
        "thread_id": thread_id,
        "messages": history,
        "count": len(history),
    }

