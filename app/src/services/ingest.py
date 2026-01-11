from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.services.vector_store import VectorStore
import pandas as pd
from pathlib import Path
from typing import Any
from src.config.logging import get_logger

logger = get_logger()

class IngestionService:
    '''Handles ingestion of raw text data into a vector store.'''
    
    def __init__(self,  vector_store: VectorStore, chunk_size: int = 500, chunk_overlap: int = 100):
        '''Initialize with vector store and chunking config.'''
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
        '''Ingests a single text document.'''
        
        chunks = self.splitter.split_text(raw_text)
        metadatas = [metadata for _ in chunks]
        ''' TODO: see if this isn't overkill
        metadatas = [{**metadata, "chunk_index":i, "total_chunks": len(chunks)}
        for i in range(len(chunks))]
        '''

        return self.vector_store.add_documents(
            documents=chunks,
            metadatas=metadatas,
        )
    

    def batch_ingest_texts(
        self,
        raw_texts: list[str],
        metadatas: list[dict],
        ids: list[str] = None,
        batch_size: int = 500
    ) -> int:
        '''
        Batch ingests the provided list of texts using the provided list of metadatas
        
        Args:
            raw_texts: List of texts to chunk and ingest.
            metadata: Metadata for each text.
            batch_size: Amount to process per batch.
        Returns:
            Number of chunks added.
        '''
        
        if len(raw_texts) != len(metadatas):
            raise ValueError("Length of raw_texts and metadatas must be the same.")

        if ids is not None and len(raw_texts) != len(ids):
            raise ValueError("Length of raw_texts and ids must be the same when ids are provided.")

        total=0 #total number of added documents (chunks)

        for i in range(0, len(raw_texts), batch_size):
            batch_chunks = []
            batch_metadata = []
            batch_ids = [] #TODO: Implement batch ids
            for j in range(i, min(i+batch_size, len(raw_texts))):
                chunks = self.splitter.split_text(raw_texts[j])
                batch_chunks.extend(chunks)
                batch_metadata.extend([metadatas[j] for _ in chunks]) #use text metadata for every chunk #TODO: Add chunk number
                if ids is not None:
                    batch_ids.extend([f'{ids[j]}_chunk_{c}' for c in range(len(chunks))])
                ''' TODO: see if this isn't overkill
                metadatas = [{**metadata, "chunk_index": k, "total_chunks": len(chunks)}
                for k in range(len(chunks))]
                '''

            if ids is None:
                total += self.vector_store.add_documents(
                    documents=batch_chunks,
                    metadatas=batch_metadata,
                )
            else:
                total += self.vector_store.add_documents(
                    documents=batch_chunks,
                    metadatas=batch_metadata,
                    ids=batch_ids
                )
        return total

    #injests the preprocessed csv in path
    def ingest_csv(self, path: Path, text_column: str = 'enriched_text', id_column: str = 'review_id', batch_size: int = 500, clear_existing: bool = False, stop_num: int = None):
        '''
        Injests the preprocessed .csv file in path.

        Args:
            path: Path to a preprocessed .csv file to injest.
            text_column: column name for the documents.
            id_column: column name for the ids.
            batch_size: Amount to process per batch.
            clear_existing: Whether to clear any existing collection.
        Returns:
            Number of chunks added.
        '''

        if not path.exists():
            raise FileNotFoundError(f'CSV not found at file location: {path}')
        try:
            data = pd.read_csv(path)
        except Exception as e:
            logger.error(f"There was a problem reading CSV {path}: {e}")
            return
        
        # Validate required columns
        if text_column not in data.columns or id_column not in data.columns:
            raise ValueError(f"CSV must contain '{text_column}' and '{id_column}' columns.")
        if id_column not in data.columns:
            raise ValueError(f"CSV must contain '{id_column}' column.")
        
        # Drop rows with missing text
        data = data.dropna(subset=[text_column])
        
        
        # whether we want to clear the existing collection or not
        if clear_existing:
            self.vector_store.clear()
        
        documents = []
        ids = []
        metadatas = []

        for index, row in data.iterrows(): #For row in data
            enriched_review = row[text_column] #May be more useful for LLM
            review = enriched_review.split("USER REVIEW: ")[-1] #Simpler, more cost effective for LLM
            review_id = int(row[id_column])
            app = row['app_name']
            rating = int(row['rating'])
            date = row['review_date']
            category = row['category']
            helpful_count = int(row['helpful_count'])
            id = f"com.{app}_{review_id}"
            metadata = {'review_id': review_id, 'app': app, 'date': date, 'rating': rating, 'category': category, 'helpful_count': helpful_count}

            documents.append(review)
            ids.append(id)
            metadatas.append(metadata)

            if stop_num is not None and index >= stop_num:
                break
            
        chunks_added = self.batch_ingest_texts(documents, metadatas, ids, batch_size) #Total number of chunks inserted
        
        return chunks_added

    def get_stats(self) -> dict[str, Any]:
        '''Get stats about the vector store collection.'''
        count = self.vector_store.count()
        categories = self.vector_store.get_metadata_field_values('category')
        apps = self.vector_store.get_metadata_field_values('app')
        return {
            'total_documents': count,
            'unique_categories': len(categories),
            'unique_apps': len(apps),
            'categories': sorted(categories) if len(categories) < 20 else 'Too many to list',
        }