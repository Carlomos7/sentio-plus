"""
LangChain Agent Service for Review Search
"""
from typing import Any

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from src.config.logging import get_logger
from src.config.settings import LLMProvider
from src.services.tools import ALL_TOOLS, set_vector_store
from src.services.vector_store import VectorStore

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a helpful assistant that searches and analyzes product/app reviews.

You have access to a database of user reviews for various apps across categories like Finance, Shopping, Entertainment, Social, etc.

Available tools:
- search_reviews: Semantic search across all reviews by topic
- search_by_app: Search reviews for a specific app
- search_by_category: Search reviews within a category
- search_by_rating: Filter reviews by rating (1-5 stars)
- list_available_apps: See all apps in the database
- list_categories: See all categories in the database

Guidelines:
1. Use the appropriate tool based on what the user asks
2. If the user mentions a specific app, use search_by_app
3. For general topics (e.g., "security issues", "crashes"), use search_reviews
4. For negative sentiment, filter by low ratings (1-2)
5. Be concise and highlight key insights from the reviews
6. Mention specific apps when relevant to the answer"""


class AgentService:
    """LangChain agent for review search."""

    def __init__(
        self,
        vector_store: VectorStore,
        provider: LLMProvider,
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 1000,
        base_url: str | None = None,
        api_key: str | None = None,
        aws_region: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
    ):
        set_vector_store(vector_store)
        
        self.model = self._create_model(
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            base_url=base_url,
            api_key=api_key,
            aws_region=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        
        self.agent = create_react_agent(
            model=self.model,
            tools=ALL_TOOLS,
            prompt=SYSTEM_PROMPT,
        )
        
        logger.info(f"✅ AgentService initialized with {len(ALL_TOOLS)} tools")

    def _create_model(
        self,
        provider: LLMProvider,
        model: str,
        temperature: float,
        max_tokens: int,
        base_url: str | None,
        api_key: str | None,
        aws_region: str | None,
        aws_access_key_id: str | None,
        aws_secret_access_key: str | None,
    ):
        """Create LangChain chat model."""
        if provider == LLMProvider.BEDROCK:
            model_id = f"bedrock:{model}"
            return init_chat_model(
                model_id,
                temperature=temperature,
                max_tokens=max_tokens,
                region_name=aws_region or "us-west-2",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )
        else:
            return init_chat_model(
                model,
                model_provider="openai",
                temperature=temperature,
                max_tokens=max_tokens,
                base_url=base_url,
                api_key=api_key or "not-needed",
            )

    def invoke(self, question: str) -> dict[str, Any]:
        """Run the agent with a user question."""
        logger.info(f"Agent query: {question[:50]}...")
        print(f"\n🤖 AGENT: Processing '{question}'")
        
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": question}]
        })
        
        # Extract tool calls for logging
        tool_calls = []
        for msg in result.get("messages", []):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_calls.append({"name": tc["name"], "args": tc["args"]})
        
        # Get final response
        final_message = result["messages"][-1]
        answer = final_message.content if hasattr(final_message, "content") else str(final_message)
        
        return {
            "answer": answer,
            "tool_calls": tool_calls,
            "num_messages": len(result.get("messages", [])),
        }
