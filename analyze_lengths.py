import pandas as pd
import numpy as np
import os
from pathlib import Path

# Paths
processed_path = Path("data/processed/sentio_plus_reviews.parquet")
raw_path_dir = Path("/Users/chenchenliu/.cache/kagglehub/datasets/dmytrobuhai/play-market-2025-1m-reviews-500-titles/versions/1")

df = None

if processed_path.exists():
    print(f"Loading processed data from {processed_path}")
    df = pd.read_parquet(processed_path)
else:
    print(f"Processed file not found at {processed_path}")
    print("Attempting to load raw games_reviews.csv as fallback...")
    raw_file = raw_path_dir / "games_reviews.csv"
    if raw_file.exists():
        df = pd.read_csv(raw_file, nrows=10000) # Sample 10k
        print(f"Loaded 10k sample from {raw_file}")
    else:
        print("No data found.")
        exit(1)

# Calculate stats
if df is not None:
    # Handle different column names if raw
    col_text = "review_text"
    
    df["char_count"] = df[col_text].astype(str).str.len()
    df["word_count"] = df[col_text].astype(str).str.split().str.len()

    print("\n--- Review Length Statistics ---")
    print(df[["char_count", "word_count"]].describe(percentiles=[0.5, 0.75, 0.90, 0.95, 0.99]))

    long_reviews = df[df["char_count"] > 2000]
    print(f"\nReviews > 2000 chars (approx 500 tokens): {len(long_reviews)} / {len(df)} ({len(long_reviews)/len(df):.2%})")
