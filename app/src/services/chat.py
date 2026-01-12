"""Chat service for RAG-based responses."""

from typing import Any
from collections import defaultdict

from langchain_aws import ChatBedrock
import boto3

from src.services.vector_store import VectorStore
from src.config.logging import get_logger
from src.config.settings import Settings

logger = get_logger(__name__)


class ChatService:
    """Handles RAG-based chat responses."""

    def __init__(
        self,
        vector_store: VectorStore,
        settings: Settings,
    ):
        self.vector_store = vector_store
        self.settings = settings
        self.llm = self._init_llm()

    def _init_llm(self) -> ChatBedrock:
        """Initialize Bedrock LLM client."""
        if not self.settings.aws_access_key_id or not self.settings.aws_secret_access_key:
            logger.warning("AWS credentials not configured. Chat will fail.")
            raise ValueError("AWS credentials required for chat")

        session = boto3.Session(
            aws_access_key_id=self.settings.aws_access_key_id,
            aws_secret_access_key=self.settings.aws_secret_access_key,
            region_name=self.settings.aws_region,
        )
        bedrock_client = session.client("bedrock-runtime")

        return ChatBedrock(
            model_id=self.settings.bedrock_model_id,
            client=bedrock_client,
            model_kwargs={"max_tokens": 1000, "temperature": 0.1},
        )

    def _group_chunks_by_review(self, results: list[dict[str, Any]]) -> dict[str, list[dict]]:
        """Group chunks by review_id to reconstruct full reviews."""
        grouped = defaultdict(list)
        for result in results:
            review_id = result["metadata"].get("review_id")
            if review_id:
                grouped[str(review_id)].append(result)
        
        for review_id in grouped:
            grouped[review_id].sort(
                key=lambda x: x["metadata"].get("chunk_index", 0)
            )
        
        return dict(grouped)

    def _summarize_context(self, grouped_reviews: dict[str, list[dict]]) -> str:
        """Summarize retrieved reviews into context string."""
        context_parts = []
        
        for review_id, chunks in grouped_reviews.items():
            full_text = " ".join(chunk["text"] for chunk in chunks)
            
            meta = chunks[0]["metadata"]
            app_name = meta.get("app_name", "Unknown")
            category = meta.get("category", "Unknown")
            rating = meta.get("rating", "?")
            date = meta.get("date", "Unknown")
            
            context_parts.append(
                f"Review {review_id} ({app_name}, {category}, Rating: {rating}/5, Date: {date}):\n"
                f"{full_text}\n"
            )
        
        return "\n".join(context_parts)

    def chat(self, query: str) -> dict[str, Any]:
        """Generate RAG-based chat response."""
        logger.info(f"Chat query: {query[:100]}...")
        
        results = self.vector_store.query(
            query_text=query,
            n_results=self.settings.retrieval_top_k,
            threshold=self.settings.retrieval_threshold,
        )
        
        if not results:
            return {
                "response": "I couldn't find any relevant reviews for your question. Try rephrasing or asking about different aspects.",
                "citations": [],
            }
        
        grouped_reviews = self._group_chunks_by_review(results)
        context = self._summarize_context(grouped_reviews)
        
        citations = []
        for review_id, chunks in grouped_reviews.items():
            meta = chunks[0]["metadata"]
            citations.append({
                "review_id": review_id,
                "app_name": meta.get("app_name"),
                "category": meta.get("category"),
                "rating": meta.get("rating"),
                "date": meta.get("date"),
            })
        
        system_prompt = """You are Sentio AI, a helpful customer review analysis assistant. 
You analyze customer feedback to provide insights and answer questions.

When responding:
- Be concise and data-driven
- Use specific numbers and percentages when possible
- Cite specific reviews when referencing them (e.g., "Based on Review 123...")
- Highlight actionable insights
- If the context doesn't fully answer the question, say so honestly"""

        user_prompt = f"""Context from customer reviews:

{context}

User Question: {query}

Provide a helpful response based on the context above. Cite specific reviews when relevant."""

        try:
            response = self.llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ])
            
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"Generated response: {len(response_text)} chars")
            
            return {
                "response": response_text,
                "citations": citations,
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": f"I encountered an error processing your question: {str(e)}",
                "citations": citations,
            }
