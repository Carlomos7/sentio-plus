"""ChromaDB vector store service."""

import uuid
from pathlib import Path
from typing import Any

import chromadb
from chromadb.api import ClientAPI
from chromadb.config import Settings as ChromaSettings

from src.config.logging import get_logger
from src.config.settings import ChromaClientType

logger = get_logger(__name__)


class VectorStore:
    """Wrapper for ChromaDB operations."""

    def __init__(
        self,
        client_type: ChromaClientType,
        collection_name: str,
        persist_path: Path | None = None,
        host: str | None = None,
        port: int | None = None,
    ):
        """Initialize ChromaDB client and collection.

        Args:
            client_type: PERSISTENT for local, HTTP for remote.
            collection_name: Name of the collection.
            persist_path: Directory for persistent storage (persistent only).
            host: ChromaDB server host (HTTP only).
            port: ChromaDB server port (HTTP only).
        """
        self.client = self._create_client(client_type, persist_path, host, port)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"✅ ChromaDB initialized ({client_type.value}): {collection_name} ({self.collection.count()} documents)"
        )

    def _create_client(
        self,
        client_type: ChromaClientType,
        persist_path: Path | None,
        host: str | None,
        port: int | None,
    ) -> ClientAPI:
        """Create the appropriate ChromaDB client."""
        if client_type == ChromaClientType.PERSISTENT:
            if not persist_path:
                raise ValueError("persist_path required for persistent client")
            persist_path.mkdir(parents=True, exist_ok=True)
            return chromadb.PersistentClient(
                path=str(persist_path),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        elif client_type == ChromaClientType.HTTP:
            if not host or not port:
                raise ValueError("host and port required for HTTP client")
            return chromadb.HttpClient(
                host=host,
                port=port,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        else:
            raise ValueError(f"Unknown client type: {client_type}")

    def add_documents(
        self,
        documents: list[str],  # variable type
        metadatas: list[dict[str, Any]] | None = None,  # Can be None, default None
        ids: list[str] | None = None,
        batch_size: int = 500,  # TODO: Subject to change
    ) -> int:
        """Add documents to the collection in batches.

        Args:
            documents: List of text documents.
            metadatas: Optional metadata for each document.
            ids: Optional IDs (generated if not provided).
            batch_size: Documents per batch.

        Returns:
            Number of documents added.
        """
        if ids is None:
            ids = [
                str(uuid.uuid4()) for _ in documents
            ]  # bad avoid using (may cause duplicate ids in some circumstances)
        if metadatas is None:
            metadatas = [{} for _ in documents]

        total = len(documents)
        for i in range(0, total, batch_size):  # Each batch
            end = min(i + batch_size, total)
            self.collection.add(
                documents=documents[i:end],
                metadatas=metadatas[i:end],
                ids=ids[i:end],
            )
            logger.info(f"   ✅ Batch {i}:{end} added")

        logger.info(f"Added {total} documents. Collection count: {self.collection.count()}")
        return total

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        threshold: float = 0.8,  # TODO:Subject to change, normal default is 0.7
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Query the collection with distance threshold filtering.

        Args:
            query_text: Search query.
            n_results: Max results to return.
            threshold: Max distance (lower = stricter). Cosine: 0=identical, 2=opposite.
            where: Optional metadata filter.

        Returns:
            List of dicts with 'text', 'metadata', 'distance'.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        docs = []
        if results["documents"] and results["documents"][0]:
            for text, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                if dist <= threshold:
                    docs.append(
                        {
                            "text": text,
                            "metadata": meta,
                            "distance": dist,
                        }
                    )

        logger.debug(f"Retrieved {len(docs)} documents (threshold: {threshold})")
        return docs

    def get_all_metadata_values(self, field: str) -> set[str]:
        """Get unique values for a metadata field.

        Args:
            field: Metadata field name.

        Returns:
            Set of unique values for the given field.
        """
        results = self.collection.get(include=["metadatas"])
        return {
            meta.get(field)
            for meta in results["metadatas"]
            if meta.get(field) is not None
        }

    def count(self) -> int:
        """Return document count in collection."""
        return self.collection.count()

    def clear(self) -> None:
        """Delete all documents in collection."""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("🗑️ Collection cleared")


# TODO: Figure out metadata and ids
