import pandas as pd
import chromadb
from pathlib import Path

DATASET_DIR = Path(__file__).parent / "dataset"
CHROMA_DIR = Path(__file__).parent / "chroma_db"

def load_to_chromadb(collection_name: str = "app_reviews") -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "App reviews with metadata"}
    )
    
    df = pd.read_csv(DATASET_DIR / "apps_and_reviews.csv")
    df = df.fillna("")
    
    documents = df["review_text"].astype(str).tolist()
    ids = df["review_id"].astype(str).tolist()
    
    metadata_cols = [
        "app_id", "app_name", "app_score", "ratings_count",
        "downloads", "content_rating", "section", "categories",
        "review_score", "review_date", "helpful_count"
    ]
    
    metadatas = df[metadata_cols].to_dict(orient="records")
    for m in metadatas:
        for k, v in m.items():
            if isinstance(v, float):
                m[k] = int(v) if v == int(v) else v
    
    collection.upsert(documents=documents, ids=ids, metadatas=metadatas)
    
    print(f"Loaded {len(documents)} reviews into collection '{collection_name}'")
    return collection

SIMILARITY_THRESHOLD = 1.0  # cosine distance: 0=identical, 2=opposite

def query_reviews(query: str, n_results: int = 5, collection_name: str = "app_reviews"):
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection(name=collection_name)
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    docs, metas, dists = results["documents"][0], results["metadatas"][0], results["distances"][0]
    filtered = [(d, m, dist) for d, m, dist in zip(docs, metas, dists) if dist <= SIMILARITY_THRESHOLD]
    
    if not filtered:
        best_dist = min(dists) if dists else None
        return {
            "documents": [[]], "metadatas": [[]], "distances": [[]],
            "message": f"No records in the database match your query. (closest distance: {best_dist:.3f}, threshold: {SIMILARITY_THRESHOLD})"
        }
    
    return {
        "documents": [[f[0] for f in filtered]],
        "metadatas": [[f[1] for f in filtered]],
        "distances": [[f[2] for f in filtered]],
        "message": None
    }

if __name__ == "__main__":
    # collection = load_to_chromadb()
    
    results = query_reviews("money transfer failed", n_results=3)
    
    if results["message"]:
        print(f"\n{results['message']}")
    else:
        print("\nSample query results:")
        for i, (doc, meta, dist) in enumerate(zip(results["documents"][0], results["metadatas"][0], results["distances"][0])):
            print(f"\n{i+1}. {meta['app_name']} (score: {meta['review_score']}, distance: {dist:.3f})")
            print(f"   {doc[:100]}...")
