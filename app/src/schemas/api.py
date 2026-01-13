"""API request/response schemas."""

from pydantic import BaseModel, Field


# --- Query Schemas ---

class QueryRequest(BaseModel):
    """Request to query the RAG system."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Question to ask about product reviews",
        examples=["What do users think about Google Wallet?"],
    )
    filter_by_source: bool = Field(
        default=True,
        description="Use LLM to pre-filter relevant apps",
    )


class QueryResponse(BaseModel):
    """Response from RAG query."""

    answer: str
    sources: list[str]
    num_docs: int
    selected_sources: list[str] = []


# --- Ingest Schemas ---

class IngestResponse(BaseModel):
    """Response from ingestion."""

    success: bool
    file: str
    rows_loaded: int
    chunks_added: int
    collection_count: int


class IngestStatsResponse(BaseModel):
    """Response with ingestion statistics."""

    total_documents: int
    unique_categories: int
    unique_apps: int
    categories: list[str] | str


# --- Health Schemas ---

class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    documents: int


# --- Model Info ---

class ModelInfoResponse(BaseModel):
    """LLM model information."""

    provider: str
    model: str
    temperature: float
    max_tokens: int