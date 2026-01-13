"""RAG orchestration service."""

from typing import TYPE_CHECKING, Any

from langchain_core.prompts import PromptTemplate

from src.config.logging import get_logger
from src.prompts.templates import RAG_PROMPT, SOURCE_SELECTION_PROMPT
from src.services.llm import LLMClient

if TYPE_CHECKING:
    from src.services.vector_store import VectorStore

logger = get_logger(__name__)


class RAGService:
    """Orchestrates retrieval and generation."""

    def __init__(
        self,
        llm: LLMClient,
        vector_store: "VectorStore",
        top_k: int = 5,
        threshold: float = 1.2,
    ):
        """Initialize RAG service.

        Args:
            llm: LLM client instance.
            vector_store: ChromaDB vector store.
            top_k: Number of documents to retrieve.
            threshold: Distance threshold for filtering.
        """
        self.llm = llm
        self.vector_store = vector_store
        self.top_k = top_k
        self.threshold = threshold

    def query(
        self,
        question: str,
        filter_by_source: bool = True,
    ) -> dict[str, Any]:
        """Answer a question using RAG.

        Args:
            question: User question.
            filter_by_source: Whether to use LLM to pre-filter sources.

        Returns:
            Dict with answer, sources, number of sources, and metadata.
        """
        # Step 1: Optionally filter sources using LLM
        metadata_filter = None
        selected_sources = []

        if filter_by_source:
            selected_sources = self._select_sources(question)
            if selected_sources:
                metadata_filter = {"app_name": {"$in": selected_sources}}
                logger.debug(f"Filtering by sources: {selected_sources}")

        # Step 2: Retrieve relevant documents
        docs = self.vector_store.query(
            query_text=question,
            n_results=self.top_k,
            threshold=self.threshold,
            where=metadata_filter,
        )

        # Step 3: Handle no results
        if not docs:
            logger.info("No relevant documents found")
            return {
                "answer": "I couldn't find any relevant reviews to answer your question.",
                "sources": [],
                "num_docs": 0,
            }

        # Step 4: Format context
        context = self._format_context(docs)

        # Step 5: Generate answer
        answer = self._generate_answer(question, context)

        # Step 6: Extract unique sources
        sources = list({doc["metadata"].get("app_name", "unknown") for doc in docs})

        return {
            "answer": answer,
            "sources": sources,
            "num_docs": len(docs),
            "selected_sources": selected_sources,
        }

    def _select_sources(self, question: str) -> list[str]:
        """Use LLM to select relevant sources."""
        app_names = self.vector_store.get_all_metadata_values("app_name")

        if not app_names:
            return []

        prompt = PromptTemplate(
            template=SOURCE_SELECTION_PROMPT,
            input_variables=["sources", "query"],
        )

        formatted = prompt.format(
            sources=", ".join(sorted(app_names)),
            query=question,
        )

        response = self.llm.invoke_structured(formatted)
        
        # invoke_structured returns a list
        if not response or (isinstance(response, list) and len(response) == 1 and response[0].lower() == "none"):
            return []

        logger.debug(f"LLM selected sources: {response}")

        return response

    def _format_context(self, docs: list[dict[str, Any]]) -> str:
        """Format retrieved documents into context string."""
        formatted_docs = []
        for doc in docs:
            meta = doc["metadata"]
            app = meta.get("app_name", "Unknown")
            rating = meta.get("rating", "?")
            text = doc["text"]
            formatted_docs.append(f"[{app} - {rating}★]\n{text}")

        return "\n\n".join(formatted_docs)

    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer using LLM."""
        prompt = PromptTemplate(
            template=RAG_PROMPT,
            input_variables=["context", "question"],
        )

        formatted = prompt.format(context=context, question=question)
        return self.llm.invoke(formatted)
    