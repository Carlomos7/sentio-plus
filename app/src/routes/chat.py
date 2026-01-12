"""Chat routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.config.logging import get_logger
from src.dependencies import get_chat_service
from src.services.chat import ChatService

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    citations: list[dict]


@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Handle chat query with RAG."""
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")
    
    try:
        result = chat_service.chat(request.message.strip())
        return ChatResponse(**result)
    except ValueError as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Chat service unavailable. Check AWS credentials configuration.",
        )
    except Exception as e:
        logger.error(f"Unexpected chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat request")
