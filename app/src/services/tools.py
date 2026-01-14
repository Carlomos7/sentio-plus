"""
Review Search Tools for LangChain Agent
"""
from typing import Any

from langchain_core.tools import tool

from src.config.logging import get_logger
from src.services.vector_store import VectorStore

logger = get_logger(__name__)

# Module-level store reference (set by agent service)
_vector_store: VectorStore | None = None


def set_vector_store(store: VectorStore) -> None:
    """Set the vector store instance for tools to use."""
    global _vector_store
    _vector_store = store


def _get_store() -> VectorStore:
    """Get the vector store, raising if not set."""
    if _vector_store is None:
        raise RuntimeError("VectorStore not initialized. Call set_vector_store first.")
    return _vector_store


def _format_results(results: list[dict[str, Any]], query: str = "") -> str:
    """Format query results for the agent."""
    if not results:
        return "No reviews found matching your criteria."
    
    output = f"Found {len(results)} relevant reviews"
    if query:
        output += f" for '{query}'"
    output += ":\n\n"
    
    for i, doc in enumerate(results, 1):
        meta = doc.get("metadata", {})
        app = meta.get("app_name", "Unknown")
        rating = meta.get("rating", "?")
        category = meta.get("category", "Unknown")
        distance = doc.get("distance", 0)
        similarity = (1 - distance) * 100 if distance else 0
        text = doc.get("text", "")[:300]
        
        output += f"{i}. [{app}] {category} | Rating: {rating}/5 | Match: {similarity:.0f}%\n"
        output += f"   {text}...\n\n"
    
    return output


@tool
def search_reviews(query: str, n_results: int = 5) -> str:
    """Search reviews by topic or meaning. Use for questions like 'find reviews about crashes' or 'reviews mentioning security issues'."""
    logger.info(f"🔧 TOOL CALLED: search_reviews(query='{query}', n_results={n_results})")
    print(f"🔧 TOOL: search_reviews | query='{query}' | n_results={n_results}")
    
    store = _get_store()
    results = store.query(query_text=query, n_results=n_results, threshold=1.5)
    
    return _format_results(results, query)


@tool
def search_by_app(app_name: str, query: str = "", n_results: int = 5) -> str:
    """Search reviews for a specific app. Optionally add a topic query to filter further."""
    logger.info(f"🔧 TOOL CALLED: search_by_app(app_name='{app_name}', query='{query}')")
    print(f"🔧 TOOL: search_by_app | app='{app_name}' | query='{query}'")
    
    store = _get_store()
    where_filter = {"app_name": app_name}
    
    search_query = query if query else f"reviews for {app_name}"
    results = store.query(
        query_text=search_query,
        n_results=n_results,
        threshold=1.5,
        where=where_filter,
    )
    
    return _format_results(results, query or app_name)


@tool
def search_by_category(category: str, query: str = "", n_results: int = 5) -> str:
    """Search reviews within a category. Categories include: Finance, Shopping, Entertainment, Social, Productivity, etc."""
    logger.info(f"🔧 TOOL CALLED: search_by_category(category='{category}', query='{query}')")
    print(f"🔧 TOOL: search_by_category | category='{category}' | query='{query}'")
    
    store = _get_store()
    where_filter = {"category": category}
    
    search_query = query if query else f"reviews in {category} category"
    results = store.query(
        query_text=search_query,
        n_results=n_results,
        threshold=1.5,
        where=where_filter,
    )
    
    return _format_results(results, query or category)


@tool
def search_by_rating(min_rating: int, max_rating: int = 5, query: str = "", n_results: int = 5) -> str:
    """Search reviews filtered by rating range (1-5). Use min_rating=1, max_rating=2 for negative reviews, min_rating=4 for positive."""
    logger.info(f"🔧 TOOL CALLED: search_by_rating(min={min_rating}, max={max_rating}, query='{query}')")
    print(f"🔧 TOOL: search_by_rating | range={min_rating}-{max_rating} | query='{query}'")
    
    store = _get_store()
    where_filter = {"$and": [{"rating": {"$gte": min_rating}}, {"rating": {"$lte": max_rating}}]}
    
    search_query = query if query else f"reviews with rating {min_rating}-{max_rating}"
    results = store.query(
        query_text=search_query,
        n_results=n_results,
        threshold=1.5,
        where=where_filter,
    )
    
    return _format_results(results, query or f"rating {min_rating}-{max_rating}")


@tool
def list_available_apps() -> str:
    """List all app names available in the review database."""
    logger.info("🔧 TOOL CALLED: list_available_apps()")
    print("🔧 TOOL: list_available_apps")
    
    store = _get_store()
    apps = store.get_all_metadata_values("app_name")
    
    if not apps:
        return "No apps found in the database."
    
    return f"Available apps ({len(apps)}): {', '.join(sorted(apps))}"


@tool
def list_categories() -> str:
    """List all categories available in the review database."""
    logger.info("🔧 TOOL CALLED: list_categories()")
    print("🔧 TOOL: list_categories")
    
    store = _get_store()
    categories = store.get_all_metadata_values("category")
    
    if not categories:
        return "No categories found in the database."
    
    return f"Available categories ({len(categories)}): {', '.join(sorted(categories))}"


# Export all tools as a list for easy agent binding
ALL_TOOLS = [
    search_reviews,
    search_by_app,
    search_by_category,
    search_by_rating,
    list_available_apps,
    list_categories,
]
