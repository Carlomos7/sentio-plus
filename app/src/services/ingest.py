"""Ingestion service for text data."""

from pathlib import Path
from typing import Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pandas as pd

from src.services.vector_store import VectorStore
from src.config.logging import get_logger

logger = get_logger(__name__)


class IngestionService:
    """Handles ingestion of raw text data into a vector store."""

    def __init__(
        self, vector_store: VectorStore, chunk_size: int = 500, chunk_overlap: int = 100
    ):
        """Initialize with vector store and chunking config."""
        self.vector_store = vector_store
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def ingest_text(
        self,
        raw_text: str,
        metadata: dict[str, Any],
    ) -> int:
        """Ingests a single text document.

        Args:
            raw_text: The raw text document to ingest.
            metadata: Metadata for the document.

        Returns:
            Number of chunks added.
        """
        chunks = self.splitter.split_text(raw_text)
        metadatas = [
            {**metadata, "chunk_index": i, "total_chunks": len(chunks)}
            for i in range(len(chunks))
        ]

        return self.vector_store.add_documents(
            documents=chunks,
            metadatas=metadatas,
        )

    def batch_ingest_texts(
        self,
        raw_texts: list[str],
        metadatas: list[dict],
        ids: list[str] = None,
        batch_size: int = 500,
    ) -> int:
        """
        Batch ingests the provided list of texts using the provided list of metadatas

        Args:
            raw_texts: List of texts to chunk and ingest.
            metadata: Metadata for each text.
            batch_size: Amount to process per batch.
        Returns:
            Number of chunks added.
        """

        if len(raw_texts) != len(metadatas):
            raise ValueError("Length of raw_texts and metadatas must be the same.")

        if ids is not None and len(raw_texts) != len(ids):
            raise ValueError(
                "Length of raw_texts and ids must be the same when ids are provided."
            )

        total = 0  # total number of added documents (chunks)

        for i in range(0, len(raw_texts), batch_size):
            batch_chunks = []
            batch_metadatas = []
            batch_ids = [] if ids else None

            for j in range(i, min(i + batch_size, len(raw_texts))):
                chunks = self.splitter.split_text(raw_texts[j])

                for k, chunk in enumerate(chunks):
                    batch_chunks.append(chunk)
                    batch_metadatas.append(
                        {
                            **metadatas[j],
                            "chunk_index": k,
                            "total_chunks": len(chunks),
                        }
                    )
                    # Generate chunk ID if ids are provided
                    if ids is not None:
                        batch_ids.append(f"{ids[j]}_chunk_{k}")

            total += self.vector_store.add_documents(
                documents=batch_chunks,
                metadatas=batch_metadatas,
                ids=batch_ids,
            )

        return total

    def ingest_csv(
        self,
        file_path: Path,
        text_column: str = "enriched_text",
        id_column: str = "review_id",
        batch_size: int = 500,
        clear_existing: bool = False,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Ingest a preprocessed CSV file.

        Args:
            file_path: Path to a preprocessed CSV file.
            text_column: column name for the documents.
            id_column: column name for the ids.
            batch_size: Amount to process per batch.
            clear_existing: Whether to clear any existing collection.
            limit: Maximum number of rows to ingest.
        Returns:
            Dict with ingestion stats.
        """

        if not file_path.exists():
            raise FileNotFoundError(f"CSV not found: {file_path}")

        logger.info(f"Loading CSV: {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df):,} rows")

        # Validate required columns
        required = [
            text_column,
            id_column,
            "app_name",
            "category",
            "rating",
            "review_date",
            "helpful_count",
        ]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        # Drop rows with missing text
        df = df.dropna(subset=[text_column])
        logger.info(f"After dropna: {len(df):,} rows")

        # Apply limit if specified
        if limit is not None:
            df = df.head(limit)
            logger.info(f"Limited to: {len(df):,} rows")

        # whether we want to clear the existing collection or not
        if clear_existing:
            self.vector_store.clear()

        documents = []
        ids = []
        metadatas = []

        for _, row in df.iterrows():
            # Extract review text after header
            enriched_review = row[text_column]
            review = enriched_review.split("USER REVIEW: ")[-1]

            review_id = int(row[id_column])
            doc_id = f"com.{row['app_name']}_{review_id}"

            metadata = {
                "review_id": review_id,
                "app_name": row["app_name"],
                "category": row["category"],
                "rating": int(row["rating"]),
                "date": str(row["review_date"]),
                "helpful_count": int(row["helpful_count"]),
            }

            documents.append(review)
            metadatas.append(metadata)
            ids.append(doc_id)

        # Ingest with chunking
        chunks_added = self.batch_ingest_texts(
            raw_texts=documents,
            metadatas=metadatas,
            ids=ids,
            batch_size=batch_size,
        )

        logger.info(f"Ingestion complete: {chunks_added} chunks from {len(df)} rows")

        return {
            "file": str(file_path),
            "rows_loaded": len(df),
            "chunks_added": chunks_added,
            "collection_count": self.vector_store.count(),
        }

    def get_stats(self) -> dict[str, Any]:
        """Get current ingestion stats.

        Returns:
            Dict with collection stats.
        """
        count = self.vector_store.count()
        categories = self.vector_store.get_all_metadata_values("category")
        apps = self.vector_store.get_all_metadata_values("app_name")

        return {
            "total_documents": count,
            "unique_categories": len(categories),
            "unique_apps": len(apps),
            "categories": (
                sorted(categories)
                if len(categories) <= 20
                else f"{len(categories)} categories"
            ),
        }
