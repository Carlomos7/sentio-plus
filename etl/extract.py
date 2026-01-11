import hashlib
import pandas as pd
from pathlib import Path

DATASET_DIR = Path(__file__).parent / "dataset"

def generate_review_id(row: pd.Series) -> str:
    key = f"{row['app_id']}|{row['review_date']}|{row['review_text']}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]

def create_apps_and_reviews(limit: int = 100) -> pd.DataFrame:
    apps_info = pd.read_csv(DATASET_DIR / "apps_info.csv")
    apps_reviews = pd.read_csv(DATASET_DIR / "apps_reviews.csv")
    
    merged = apps_info.merge(apps_reviews, on="app_id", how="inner")
    merged["review_id"] = merged.apply(generate_review_id, axis=1)
    merged = merged.rename(columns={"score": "app_score"})
    
    columns = [
        "review_id", "app_id", "app_name", "app_score", "ratings_count",
        "downloads", "content_rating", "section", "categories",
        "review_text", "review_score", "review_date", "helpful_count"
    ]
    
    result = merged[columns].head(limit)
    
    output_path = DATASET_DIR / "apps_and_reviews.csv"
    result.to_csv(output_path, index=False)
    print(f"Created {output_path} with {len(result)} rows")
    
    return result

if __name__ == "__main__":
    df = create_apps_and_reviews(100)
    print(df.head())
