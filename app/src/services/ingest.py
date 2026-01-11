from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.services.vector_store import VectorStore
import pandas as pd

def ingest_text(
    *,
    vector_store: VectorStore,
    raw_text: str,
    metadata: dict,
) -> int:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = splitter.split_text(raw_text)
    metadatas = [metadata for _ in chunks]

    return vector_store.add_documents(
        documents=chunks,
        metadatas=metadatas,
    )

def batch_ingest_text(
    *,
    vector_store: VectorStore,
    raw_texts: list[str],
    metadatas: list[dict],
    ids: list[str] = None,
    batch_size: int = 500
) -> int:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )
    #Batch injests the provided list of texts using the provided list of metadatas

    total=0 #total number of added documents (chunks)

    for i in range(0, len(raw_texts), batch_size):
        batch_chunks = []
        batch_metadata = []
        batch_ids = [] #TODO: Implement batch ids
        for j in range(i, min(i+batch_size, len(raw_texts))):
            chunks = splitter.split_text(raw_texts[j])
            batch_chunks.extend(chunks)
            batch_metadata.extend([metadatas[j] for _ in chunks]) #use text metadata for every chunk #TODO: Add chunk number

        if ids is None:
            total += vector_store.add_documents(
                documents=batch_chunks,
                metadatas=batch_metadata,
            )
        else:
            pass
    return total

#injests the preprocessed csv in path
def injest_csv(path=None):
    try:
        data = pd.read_csv(path)
    except Exception as e:
        print(f"There was a problem reading {path}: {e}")
        return
    
    for index, row in data.iterrows(): #For row in data
        enriched_review = data['enriched_text']
        review = enriched_review.split("USER REVIEW: ")[1]
        review_id = data['review_id']
        app_name = data['app_name']
        rating = data['rating']
        date = data['review_date']
        category = data['category']


