"""LangChain agent service with tools for RAG queries."""

from typing import Any

from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from src.config.logging import get_logger
from src.services.ingest import IngestionService
from src.services.rag import RAGService
from src.services.vector_store import VectorStore
from src.prompts.templates import AGENT_SYSTEM_PROMPT

logger = get_logger(__name__)

# Global references to services (set by AgentService)
_rag_service: RAGService | None = None
_ingest_service: IngestionService | None = None
_vector_store: VectorStore | None = None


@tool
def search_reviews(question: str) -> str:
    """Search product reviews to answer questions about user feedback, app features, 
    ratings, complaints, or comparisons between apps.
    
    Use this tool when the user asks about:
    - What users think about an app or feature
    - Common complaints or praise in reviews
    - Comparisons between different apps
    - Specific features mentioned in reviews
    - User sentiment or satisfaction
    - App ratings or feedback patterns
    
    Args:
        question: The question to search reviews for.
        
    Returns:
        An answer synthesized from relevant product reviews.
    """
    if _rag_service is None:
        return "Error: RAG service not initialized."
    
    try:
        result = _rag_service.query(question=question, filter_by_source=True)
        
        answer = result["answer"]
        sources = result.get("sources", [])
        num_docs = result.get("num_docs", 0)
        
        if sources:
            return f"{answer}\n\n[Based on {num_docs} reviews from: {', '.join(sources)}]"
        return answer
    except Exception as e:
        logger.error(f"search_reviews failed: {e}")
        return f"Error searching reviews: {str(e)}"


@tool
def get_collection_stats() -> str:
    """Get statistics about the review collection including total documents, 
    unique apps, and categories.
    
    Use this tool when the user asks about:
    - How many reviews are in the system
    - What apps are available to query
    - What categories of apps exist
    - The scope or coverage of the review data
    
    Returns:
        Statistics about the document collection.
    """
    if _ingest_service is None:
        return "Error: Ingestion service not initialized."
    
    try:
        stats = _ingest_service.get_stats()
        
        total = stats.get("total_documents", 0)
        apps = stats.get("unique_apps", 0)
        categories = stats.get("unique_categories", 0)
        category_list = stats.get("categories", [])
        
        response = f"Collection Statistics:\n"
        response += f"- Total documents: {total:,}\n"
        response += f"- Unique apps: {apps}\n"
        response += f"- Unique categories: {categories}\n"
        
        if isinstance(category_list, list) and category_list:
            response += f"- Categories: {', '.join(category_list)}"
        
        return response
    except Exception as e:
        logger.error(f"get_collection_stats failed: {e}")
        return f"Error getting stats: {str(e)}"


@tool
def list_available_apps() -> str:
    """List all apps that have reviews in the collection.
    
    Use this tool when the user asks about:
    - What apps can be queried
    - Which apps have reviews
    - Available apps in the system
    - Before searching for a specific app to confirm it exists
    
    Returns:
        A list of app names with reviews in the collection.
    """
    if _vector_store is None:
        return "Error: Vector store not initialized."
    
    try:
        app_names = _vector_store.get_all_metadata_values("app_name")
        
        if not app_names:
            return "No apps found in the collection."
        
        sorted_apps = sorted(app_names)
        return f"Available apps ({len(sorted_apps)}):\n" + "\n".join(f"- {app}" for app in sorted_apps)
    except Exception as e:
        logger.error(f"list_available_apps failed: {e}")
        return f"Error listing apps: {str(e)}"


class AgentService:
    """Service for managing the LangChain agent with tools and memory."""
    
    def __init__(
        self,
        llm: Any,
        rag_service: RAGService,
        ingest_service: IngestionService,
        vector_store: VectorStore,
    ):
        """Initialize the agent service.
        
        Args:
            llm: LangChain-compatible LLM instance.
            rag_service: RAG service for search_reviews tool.
            ingest_service: Ingestion service for stats tool.
            vector_store: Vector store for list_apps tool.
        """
        global _rag_service, _ingest_service, _vector_store
        
        # Set global references for tools
        _rag_service = rag_service
        _ingest_service = ingest_service
        _vector_store = vector_store
        
        # Create memory checkpointer
        self.checkpointer = InMemorySaver()
        
        # Create agent with tools
        self.tools = [search_reviews, get_collection_stats, list_available_apps]
        
        self.agent = create_agent(
            llm,
            tools=self.tools,
            checkpointer=self.checkpointer,
            system_prompt=AGENT_SYSTEM_PROMPT,
        )
        
        logger.info(f"AgentService initialized with {len(self.tools)} tools")
    
    def invoke(self, message: str, thread_id: str) -> dict[str, Any]:
        """Invoke the agent with a user message.
        
        Args:
            message: User's message/question.
            thread_id: Unique thread ID for conversation memory.
            
        Returns:
            Dict with response and thread_id.
        """
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": message}]},
                {"configurable": {"thread_id": thread_id}},
            )
            
            # Extract the last assistant message
            messages = result.get("messages", [])
            response_content = ""
            
            for msg in reversed(messages):
                if hasattr(msg, "content") and hasattr(msg, "type"):
                    if msg.type == "ai":
                        response_content = msg.content
                        break
                elif isinstance(msg, dict) and msg.get("role") == "assistant":
                    response_content = msg.get("content", "")
                    break
            
            if not response_content and messages:
                # Fallback: get last message content
                last_msg = messages[-1]
                if hasattr(last_msg, "content"):
                    response_content = last_msg.content
                elif isinstance(last_msg, dict):
                    response_content = last_msg.get("content", "")
            
            return {
                "response": response_content,
                "thread_id": thread_id,
            }
        except Exception as e:
            logger.error(f"Agent invoke failed: {e}")
            raise
    
    def get_conversation_history(self, thread_id: str) -> list[dict[str, str]]:
        """Get conversation history for a thread.
        
        Args:
            thread_id: Thread ID to retrieve history for.
            
        Returns:
            List of message dicts with role and content.
        """
        try:
            config = {"configurable": {"thread_id": thread_id}}
            state = self.checkpointer.get(config)
            
            if state is None:
                return []
            
            messages = state.get("messages", [])
            history = []
            
            for msg in messages:
                if hasattr(msg, "type") and hasattr(msg, "content"):
                    role = "assistant" if msg.type == "ai" else "user"
                    history.append({"role": role, "content": msg.content})
                elif isinstance(msg, dict):
                    history.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", ""),
                    })
            
            return history
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []

