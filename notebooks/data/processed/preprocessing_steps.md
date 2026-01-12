RAG Preprocessing Specification: Sentio+
This document outlines the strategy for transforming raw App Store data into a high-signal corpus for a decision-support RAG chatbot.

1. Objective
To curate a dataset of 50,000 high-signal reviews that allows an LLM to extract fine-grained, evidence-backed insights regarding product features, usability, and business priorities, rather than simple sentiment.

2. Data Integration & Cleaning
Source Files: apps_reviews.csv and apps_info.csv (Games excluded).
Merge Logic: Left-join reviews with info on app_id.
Category Normalization: Clean messy string categories (e.g., #9 top free finance, Finance $\rightarrow$ Finance).
Null Handling: Drop rows missing review_text, app_name, or category.
3. The "Hybrid Stratified Signal" Sampling
We move away from Random sampling to Signal-Based sampling to ensure the RAG model has "meat" to analyze.

Stage A: The Quality Gate
Before sampling, filter the entire pool to remove "noise":

Length Threshold: Minimum 150 characters. (Excludes low-signal reviews like "Great app!").
Helpfulness Weighting: Prioritize reviews with helpful_count > 0.
Recency Weighting: Ensure ~60% of the sample is from the last 12 months to keep insights relevant to current product roadmaps.
Stage B: Stratified Selection
Bucketization: Divide the filtered pool into buckets by Category and Rating (1-5).
Signal Sorting: Within each bucket, sort reviews by text_length and helpful_count (Descending).
Top-K Extraction: Select the top $N$ reviews from each bucket until the 50,000 target is met.
Result: A perfectly balanced dataset where every single review is the most articulate "representative" of its category/rating.
4. Metadata Enrichment (The "Context Header")
To ensure the RAG chatbot remains "grounded," we construct an Enriched Text column. This prepends structured context to the raw review text so the LLM always knows "who" is speaking.

Format:

[APP: {app_name} | CAT: {category} | RATING: {rating}/5 | DATE: {date} | SEGMENT: {content_rating}] USER REVIEW: {review_text}

5. Metadata Preservation List
These fields must be preserved as separate columns in the final CSV/Vector Store to enable Hard Filtering (e.g., "Find only 1-star reviews in Finance"):

For Grounding: review_id, app_name.
For Filtering: category, rating, review_date, content_rating (Audience Proxy).
For Bias/Importance: helpful_count, downloads.
6. Chunking Strategy: "Focus over Fit"
Because app reviews are naturally small, we avoid arbitrary splitting:

The Default: 1 Review = 1 Chunk. This preserved the complete context of a user's thought.
The Exception: If a review exceeds 750 characters, split it by paragraph. Prepend the "Context Header" to every resulting chunk so the metadata is never lost.
7. Output Result
A single sentio_plus_rag_ready.csv containing:

Original metadata columns.
Enriched Text: The main input for the embedding model.
Signal Scores: (Length, Helpful) used for audit and ranking.