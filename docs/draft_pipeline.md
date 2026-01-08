# Sentio-Plus: Product Review Chatbot

## Technical Scope Document

---

## 1. Project Overview

A RAG-based chatbot that ingests product reviews, extracts **aspect-level opinions** (what people like/dislike about specific features), and answers semantic queries about customer sentiment. Goes beyond positive/negative labels to understand *what* customers think *about what*.

### Core Value Proposition

| Traditional Sentiment | Sentio-Plus Semantic Sentiment |
|-----------------------|--------------------------------|
| "This review is positive" | "Customers love the keyboard feel but hate the price" |
| Single score per review | Multiple opinions per review |
| No feature granularity | Aspect-level breakdown |

---

## 2. Tech Stack

| Component | Technology | Cost |
|-----------|------------|------|
| Vector Store | ChromaDB Local (PersistentClient) | Free |
| Data Storage | AWS S3 | Free tier / lab credits |
| Embeddings | ChromaDB default (all-MiniLM-L6-v2) | Free |
| LLM | AWS Bedrock (Claude 3 Sonnet) | Lab credits |
| Orchestration | LangChain | Free |
| Runtime | Local Jupyter | Free |

### Model Configuration

```python
# AWS Bedrock
BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
AWS_REGION = "us-west-2"
```

---

## 3. Architecture

### 3.1 High-Level Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INGESTION PIPELINE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────┐      ┌─────────────┐      ┌──────────────────┐               │
│   │   S3    │ ───▶ │   Parse     │ ───▶ │ Aspect Extraction │               │
│   │ Bucket  │      │   JSON      │      │   (LLM Call)      │               │
│   └─────────┘      └─────────────┘      └──────────────────┘               │
│                                                   │                         │
│                                                   ▼                         │
│                                         ┌──────────────────┐               │
│                                         │    Normalize     │               │
│                                         │     Aspects      │               │
│                                         └──────────────────┘               │
│                                                   │                         │
│                          ┌────────────────────────┼────────────────────┐   │
│                          ▼                        ▼                    │   │
│                 ┌─────────────────┐      ┌─────────────────┐          │   │
│                 │    reviews      │      │    opinions     │          │   │
│                 │   collection    │      │   collection    │          │   │
│                 └─────────────────┘      └─────────────────┘          │   │
│                                                                        │   │
│                              ChromaDB (Local Persistent)               │   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            QUERY PIPELINE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────┐      ┌─────────────┐      ┌──────────────────┐               │
│   │  User   │ ───▶ │   Query     │ ───▶ │    Retrieve      │               │
│   │  Query  │      │  Classify   │      │   + Filter       │               │
│   └─────────┘      └─────────────┘      └──────────────────┘               │
│                                                   │                         │
│                                                   ▼                         │
│                                         ┌──────────────────┐               │
│                                         │    Aggregate     │               │
│                                         │    by Aspect     │               │
│                                         └──────────────────┘               │
│                                                   │                         │
│                                                   ▼                         │
│                                         ┌──────────────────┐               │
│                                         │  LLM Generate    │               │
│                                         │    Response      │               │
│                                         └──────────────────┘               │
│                                                   │                         │
│                                                   ▼                         │
│                                         ┌──────────────────┐               │
│                                         │  Conversational  │               │
│                                         │     Answer       │               │
│                                         └──────────────────┘               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Semantic Sentiment Model

Instead of a single sentiment score, each review is decomposed into **opinion units**:

```
Review: "Love the keyboard feel but the battery dies too fast and it's overpriced"

Extracted Opinions:
├── Aspect: keyboard      → Sentiment: positive   → "Love the keyboard feel"
├── Aspect: battery       → Sentiment: negative   → "battery dies too fast"
└── Aspect: price         → Sentiment: negative   → "overpriced"
```

---

## 4. Data Storage

### 4.1 S3 Structure

```
s3://sentio-plus-reviews/
└── reviews/
    ├── keyboard_2025.json
    ├── airpods_pro.json
    └── macbook_m4.json
```

### 4.2 Product File Schema

One JSON file per product containing all its reviews:

```json
{
  "product_id": "p_keyboard_2025",
  "product_name": "Mac 2025 Keyboard",
  "reviews": [
    {
      "review_id": "r_001",
      "rating": 4,
      "review_text": "Love the tactile feel but it's overpriced",
      "timestamp": "2025-01-05"
    },
    {
      "review_id": "r_002",
      "rating": 2,
      "review_text": "Keys are too shallow and the function row is confusing",
      "timestamp": "2025-01-04"
    }
  ]
}
```

---

## 5. ChromaDB Configuration

### 5.1 Client Initialization

```python
import chromadb

# Local persistent storage (data survives restarts)
CHROMA_PATH = "./chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Create collections
reviews_collection = chroma_client.get_or_create_collection(
    name="reviews",
    metadata={"description": "Full product reviews"}
)

opinions_collection = chroma_client.get_or_create_collection(
    name="opinions",
    metadata={"description": "Extracted aspect-level opinions"}
)
```

### 5.2 Collection: `reviews`

Stores full review text for retrieval queries.

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `id` | string | `"rv_uuid_123"` | Unique document ID (UUID) |
| `document` | string | `"Love the tactile feel but it's overpriced"` | Full review text (embedded) |
| `metadata.review_id` | string | `"r_001"` | Original review ID from source |
| `metadata.product_id` | string | `"p_keyboard_2025"` | Product identifier for filtering |
| `metadata.product_name` | string | `"Mac 2025 Keyboard"` | Human-readable product name |
| `metadata.rating` | int | `4` | Star rating 1-5 |
| `metadata.timestamp` | string | `"2025-01-05"` | Review date |

**Upsert Example:**

```python
import uuid

reviews_collection.add(
    ids=[str(uuid.uuid4())],
    documents=["Love the tactile feel but it's overpriced"],
    metadatas=[{
        "review_id": "r_001",
        "product_id": "p_keyboard_2025",
        "product_name": "Mac 2025 Keyboard",
        "rating": 4,
        "timestamp": "2025-01-05"
    }]
)
```

### 5.3 Collection: `opinions`

Stores extracted opinion phrases for semantic sentiment queries.

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `id` | string | `"op_uuid_456"` | Unique document ID (UUID) |
| `document` | string | `"Love the tactile feel"` | Opinion phrase (embedded) |
| `metadata.opinion_id` | string | `"r_001_0"` | Review ID + opinion index |
| `metadata.review_id` | string | `"r_001"` | Parent review reference |
| `metadata.product_id` | string | `"p_keyboard_2025"` | Product for filtering |
| `metadata.product_name` | string | `"Mac 2025 Keyboard"` | Human-readable name |
| `metadata.aspect` | string | `"tactile feel"` | Raw extracted aspect |
| `metadata.aspect_normalized` | string | `"keyboard"` | Canonical aspect category |
| `metadata.sentiment` | string | `"positive"` | positive / negative / mixed |

**Upsert Example:**

```python
import uuid

opinions_collection.add(
    ids=[str(uuid.uuid4()), str(uuid.uuid4())],
    documents=[
        "Love the tactile feel",
        "it's overpriced"
    ],
    metadatas=[
        {
            "opinion_id": "r_001_0",
            "review_id": "r_001",
            "product_id": "p_keyboard_2025",
            "product_name": "Mac 2025 Keyboard",
            "aspect": "tactile feel",
            "aspect_normalized": "keyboard",
            "sentiment": "positive"
        },
        {
            "opinion_id": "r_001_1",
            "review_id": "r_001",
            "product_id": "p_keyboard_2025",
            "product_name": "Mac 2025 Keyboard",
            "aspect": "price",
            "aspect_normalized": "price",
            "sentiment": "negative"
        }
    ]
)
```

---

## 6. Aspect Taxonomy

Maps raw extracted aspects to canonical categories for consistent filtering.

```python
ASPECT_TAXONOMY = {
    "keyboard": ["keyboard", "keys", "typing", "tactile", "key travel", "keystrokes"],
    "battery": ["battery", "battery life", "power", "charge", "dies", "charging"],
    "display": ["screen", "display", "monitor", "brightness", "resolution", "glare"],
    "price": ["price", "cost", "expensive", "value", "worth", "overpriced", "cheap"],
    "performance": ["speed", "fast", "slow", "performance", "lag", "responsive"],
    "build": ["design", "build", "quality", "materials", "durability", "premium"],
    "audio": ["sound", "speakers", "audio", "volume", "noise cancellation"],
    "comfort": ["comfortable", "ergonomic", "fit", "weight", "portable"]
}

def normalize_aspect(raw_aspect: str) -> str:
    """Map raw aspect to canonical name."""
    raw_lower = raw_aspect.lower()
    for canonical, synonyms in ASPECT_TAXONOMY.items():
        if any(syn in raw_lower for syn in synonyms):
            return canonical
    return "other"
```

---

## 7. Query Types & Returns

### 7.1 Type 1: Opinion Summary

**Intent:** General sentiment overview for a product

| Trigger Phrases |
|-----------------|
| "What do people think about X?" |
| "What do customers say about X?" |
| "How is the X?" |
| "Tell me about the X" |

**Collection:** `opinions`

**Filters:** `product_id`

**Query Example:**

```python
results = opinions_collection.query(
    query_texts=["customer opinions feedback"],
    n_results=20,
    where={"product_id": "p_keyboard_2025"},
    include=["documents", "metadatas", "distances"]
)
```

**Response Format:**

```
Customers have mixed feelings about the Mac 2025 Keyboard. 
The tactile feedback and quiet keys get consistent praise, 
but many find it overpriced for what it offers. A few users 
mention the function row layout takes getting used to.
```

---

### 7.2 Type 2: Positive Opinion Discovery

**Intent:** What customers like about a product

| Trigger Phrases |
|-----------------|
| "What do people like about X?" |
| "What's good about X?" |
| "Any positive feedback on X?" |
| "What are the pros of X?" |

**Collection:** `opinions`

**Filters:** `product_id` + `sentiment = "positive"`

**Query Example:**

```python
results = opinions_collection.query(
    query_texts=["positive feedback likes love great"],
    n_results=15,
    where={
        "$and": [
            {"product_id": "p_keyboard_2025"},
            {"sentiment": "positive"}
        ]
    },
    include=["documents", "metadatas", "distances"]
)
```

**Response Format:**

```
Customers praise the Mac 2025 Keyboard for its tactile feel 
and satisfying keystrokes. The low-profile design and quiet 
operation are frequently mentioned positives. Several users 
appreciate the premium build quality.
```

---

### 7.3 Type 3: Negative Opinion Discovery

**Intent:** What customers dislike/complain about

| Trigger Phrases |
|-----------------|
| "What do people complain about X?" |
| "What's wrong with X?" |
| "Any issues with X?" |
| "What don't people like about X?" |
| "What are the cons of X?" |

**Collection:** `opinions`

**Filters:** `product_id` + `sentiment = "negative"`

**Query Example:**

```python
results = opinions_collection.query(
    query_texts=["complaints issues problems hate bad"],
    n_results=15,
    where={
        "$and": [
            {"product_id": "p_keyboard_2025"},
            {"sentiment": "negative"}
        ]
    },
    include=["documents", "metadatas", "distances"]
)
```

**Response Format:**

```
Common complaints about the Mac 2025 Keyboard include the 
high price point and shallow key travel. Some users find 
the function row layout confusing, and a few report 
connectivity issues with older Macs.
```

---

### 7.4 Type 4: Aspect-Specific Inquiry

**Intent:** Sentiment about a specific feature/aspect

| Trigger Phrases |
|-----------------|
| "How do people feel about the battery?" |
| "What do people say about the price?" |
| "Is the keyboard good?" |
| "How's the screen quality?" |

**Collection:** `opinions`

**Filters:** `product_id` + `aspect_normalized`

**Query Example:**

```python
results = opinions_collection.query(
    query_texts=["battery life power charge"],
    n_results=10,
    where={
        "$and": [
            {"product_id": "p_airpods_pro"},
            {"aspect_normalized": "battery"}
        ]
    },
    include=["documents", "metadatas", "distances"]
)
```

**Response Format:**

```
Battery feedback for AirPods Pro is mixed. Users appreciate 
the case providing multiple charges, but several complain 
that the buds themselves die faster than expected, especially 
with noise cancellation enabled.
```

---

### 7.5 Type 5: Review Retrieval

**Intent:** Show actual review excerpts/quotes

| Trigger Phrases |
|-----------------|
| "Show me negative reviews for X" |
| "Give me examples of complaints" |
| "What are people actually saying?" |
| "Show me reviews about X" |

**Collection:** `reviews` (may chain from `opinions` first)

**Filters:** `product_id` (+ post-filter by sentiment via opinion linkage)

**Query Example:**

```python
# Option A: Direct review search
results = reviews_collection.query(
    query_texts=["problems issues complaints"],
    n_results=5,
    where={"product_id": "p_keyboard_2025"},
    include=["documents", "metadatas", "distances"]
)

# Option B: Chain from opinions to get specific sentiment
opinion_results = opinions_collection.query(
    query_texts=["complaints problems"],
    n_results=5,
    where={
        "$and": [
            {"product_id": "p_keyboard_2025"},
            {"sentiment": "negative"}
        ]
    }
)

# Get unique review IDs from opinions
review_ids = list(set([m["review_id"] for m in opinion_results["metadatas"][0]]))

# Fetch full reviews by ID
reviews = reviews_collection.get(
    where={"review_id": {"$in": review_ids}},
    include=["documents", "metadatas"]
)
```

**Response Format:**

```
Here are some negative reviews for the Mac 2025 Keyboard:

"Keys are too shallow and the function row is confusing. 
Not worth the premium price." - 2 stars

"Connectivity drops randomly. Had to re-pair multiple times 
in the first week." - 1 star

"Build quality is nice but for $200 I expected more." - 3 stars
```

---

## 8. Query Classification

### 8.1 Classification Function

```python
def classify_query(query: str) -> dict:
    """
    Parse user query to determine intent and filters.
    
    Returns:
        {
            "intent": str,           # summary | positive | negative | aspect | retrieval
            "product_hint": str,     # extracted product name or None
            "aspect_hint": str,      # detected aspect or None
            "sentiment_filter": str  # positive | negative | None
        }
    """
    query_lower = query.lower()
    
    result = {
        "intent": "summary",
        "product_hint": None,
        "aspect_hint": None,
        "sentiment_filter": None
    }
    
    # Intent detection signals
    positive_signals = ["like", "good", "love", "best", "positive", "praise", "pros", "appreciate"]
    negative_signals = ["dislike", "hate", "bad", "worst", "complain", "issue", "problem", 
                        "negative", "cons", "wrong", "don't like"]
    retrieval_signals = ["show me", "give me", "examples", "actual reviews", "what are people saying"]
    
    # Determine intent
    if any(sig in query_lower for sig in retrieval_signals):
        result["intent"] = "retrieval"
    elif any(sig in query_lower for sig in positive_signals):
        result["intent"] = "positive"
        result["sentiment_filter"] = "positive"
    elif any(sig in query_lower for sig in negative_signals):
        result["intent"] = "negative"
        result["sentiment_filter"] = "negative"
    
    # Detect aspect hints (check taxonomy keys)
    for aspect in ASPECT_TAXONOMY.keys():
        if aspect in query_lower:
            result["intent"] = "aspect"
            result["aspect_hint"] = aspect
            break
    
    # Also check taxonomy synonyms for aspect detection
    for canonical, synonyms in ASPECT_TAXONOMY.items():
        if any(syn in query_lower for syn in synonyms):
            result["aspect_hint"] = canonical
            if result["intent"] not in ["positive", "negative", "retrieval"]:
                result["intent"] = "aspect"
            break
    
    return result
```

### 8.2 Classification Examples

| Query | Intent | Sentiment Filter | Aspect Hint |
|-------|--------|------------------|-------------|
| "What do people think about the keyboard?" | summary | None | None |
| "What do people like about the AirPods?" | positive | positive | None |
| "Any complaints about the MacBook?" | negative | negative | None |
| "How's the battery life?" | aspect | None | battery |
| "Show me negative reviews" | retrieval | None | None |
| "What do people hate about the price?" | negative | negative | price |

---

## 9. Retrieval Functions

### 9.1 Opinion Retrieval

```python
def retrieve_opinions(
    query: str,
    product_id: str = None,
    sentiment: str = None,
    aspect: str = None,
    n_results: int = 10,
    threshold: float = 1.5
) -> list[dict]:
    """
    Retrieve relevant opinions with metadata filtering.
    
    Args:
        query: Search query text
        product_id: Filter to specific product
        sentiment: Filter to positive/negative/mixed
        aspect: Filter to normalized aspect
        n_results: Max results to return
        threshold: Max distance (lower = stricter match)
    
    Returns:
        List of opinion dicts with text, sentiment, aspect, etc.
    """
    # Build where filter
    conditions = []
    if product_id:
        conditions.append({"product_id": product_id})
    if sentiment:
        conditions.append({"sentiment": sentiment})
    if aspect:
        conditions.append({"aspect_normalized": aspect})
    
    where_filter = None
    if len(conditions) == 1:
        where_filter = conditions[0]
    elif len(conditions) > 1:
        where_filter = {"$and": conditions}
    
    # Query ChromaDB
    results = opinions_collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )
    
    # Filter by distance threshold and format response
    docs = []
    if results["documents"] and results["documents"][0]:
        for text, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            if dist <= threshold:
                docs.append({
                    "text": text,
                    "sentiment": meta.get("sentiment"),
                    "aspect": meta.get("aspect_normalized"),
                    "product_name": meta.get("product_name"),
                    "review_id": meta.get("review_id"),
                    "distance": dist
                })
    
    print(f"Retrieved {len(docs)} opinions (threshold: {threshold})")
    return docs
```

### 9.2 Review Retrieval

```python
def retrieve_reviews(
    query: str,
    product_id: str = None,
    n_results: int = 5,
    threshold: float = 1.5
) -> list[dict]:
    """
    Retrieve full reviews for citation/display.
    
    Args:
        query: Search query text
        product_id: Filter to specific product
        n_results: Max results to return
        threshold: Max distance
    
    Returns:
        List of review dicts with full text, rating, etc.
    """
    where_filter = {"product_id": product_id} if product_id else None
    
    results = reviews_collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )
    
    docs = []
    if results["documents"] and results["documents"][0]:
        for text, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            if dist <= threshold:
                docs.append({
                    "text": text,
                    "rating": meta.get("rating"),
                    "product_name": meta.get("product_name"),
                    "review_id": meta.get("review_id"),
                    "timestamp": meta.get("timestamp"),
                    "distance": dist
                })
    
    print(f"Retrieved {len(docs)} reviews (threshold: {threshold})")
    return docs
```

### 9.3 Chained Retrieval (Opinions → Reviews)

```python
def retrieve_reviews_by_sentiment(
    query: str,
    product_id: str,
    sentiment: str,
    n_results: int = 5
) -> list[dict]:
    """
    Get full reviews that contain opinions matching sentiment.
    
    1. Find opinions matching sentiment filter
    2. Extract unique review IDs
    3. Fetch full reviews
    """
    # Step 1: Get matching opinions
    opinions = retrieve_opinions(
        query=query,
        product_id=product_id,
        sentiment=sentiment,
        n_results=n_results * 2  # Get extra to account for duplicates
    )
    
    if not opinions:
        return []
    
    # Step 2: Get unique review IDs
    review_ids = list(set([op["review_id"] for op in opinions]))[:n_results]
    
    # Step 3: Fetch full reviews
    reviews = reviews_collection.get(
        where={"review_id": {"$in": review_ids}},
        include=["documents", "metadatas"]
    )
    
    # Format response
    docs = []
    if reviews["documents"]:
        for text, meta in zip(reviews["documents"], reviews["metadatas"]):
            docs.append({
                "text": text,
                "rating": meta.get("rating"),
                "product_name": meta.get("product_name"),
                "review_id": meta.get("review_id"),
                "timestamp": meta.get("timestamp")
            })
    
    return docs
```

---

## 10. LLM Prompts

### 10.1 Aspect Extraction Prompt (Ingestion)

Used during ingestion to extract opinion units from each review.

```python
EXTRACTION_PROMPT = """Human: Extract opinions from this product review. For each distinct opinion, identify:
- aspect: the product feature being discussed (e.g., battery, keyboard, price, design, screen)
- sentiment: positive, negative, or mixed
- phrase: the exact words from the review expressing this opinion

Return ONLY a valid JSON array. No explanation or preamble.

Review: "{review_text}"
Assistant:

Assistant:

Example output:
\`\`\`json
[
  {"aspect": "tactile feel", "sentiment": "positive", "phrase": "Love the tactile feel"},
  {"aspect": "price", "sentiment": "negative", "phrase": "overpriced"}
]
\`\`\`
"""
\`\`\`

### 10.2 Summary Generation Prompt

Used to generate conversational summaries from retrieved opinions.

Assistant:"""
```

### 10.3 Retrieval Prompt

Used when showing actual review excerpts.

```python
RETRIEVAL_PROMPT = """Human: Present customer reviews with direct quotes.

Rules:
1. Most relevant first
2. Include star rating  
3. Be concise

Question: {query}
Reviews: {context}

Present the reviews.

Assistant:"""
```

---

## 11. Pipeline Implementation Phases

### Phase 1: Setup & Configuration

```python
# Dependencies
# pip install boto3 chromadb langchain langchain-aws langchain-text-splitters

import os
import boto3
import chromadb

# AWS Configuration
AWS_ACCESS_KEY_ID = "your-key"
AWS_SECRET_ACCESS_KEY = "your-secret"  
AWS_REGION = "us-west-2"
S3_BUCKET = "sentio-plus-reviews"

# Bedrock Configuration
BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

# ChromaDB Configuration  
CHROMA_PATH = "./chroma_db"

# Initialize Clients
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)
bedrock_client = session.client("bedrock-runtime")
s3_client = session.client("s3")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
reviews_collection = chroma_client.get_or_create_collection(name="reviews")
opinions_collection = chroma_client.get_or_create_collection(name="opinions")
```

### Phase 2: Data Ingestion (S3)

```python
import json

def load_reviews_from_s3(bucket: str, prefix: str = "reviews/") -> list[dict]:
    """Download and parse all product review files from S3."""
    all_reviews = []
    
    # List objects in bucket
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    
    for obj in response.get("Contents", []):
        key = obj["Key"]
        if key.endswith(".json"):
            # Download file
            file_obj = s3_client.get_object(Bucket=bucket, Key=key)
            content = file_obj["Body"].read().decode("utf-8")
            product_data = json.loads(content)
            
            # Extract reviews with product info
            product_id = product_data["product_id"]
            product_name = product_data["product_name"]
            
            for review in product_data["reviews"]:
                review["product_id"] = product_id
                review["product_name"] = product_name
                all_reviews.append(review)
    
    print(f"Loaded {len(all_reviews)} reviews from S3")
    return all_reviews
```

### Phase 3: Aspect Extraction & Embedding

```python
import uuid
from langchain_aws import ChatBedrock

llm = ChatBedrock(
    model_id=BEDROCK_MODEL_ID,
    client=bedrock_client,
    model_kwargs={"max_tokens": 1000, "temperature": 0.1}
)

def extract_opinions(review_text: str) -> list[dict]:
    """Use LLM to extract aspect-sentiment-phrase tuples."""
    prompt = EXTRACTION_PROMPT.format(review_text=review_text)
    response = llm.invoke(prompt)
    
    try:
        opinions = json.loads(response.content)
        return opinions
    except json.JSONDecodeError:
        return []

def process_and_embed_reviews(reviews: list[dict]):
    """Process all reviews: extract opinions, normalize, embed, store."""
    
    for review in reviews:
        review_id = review["review_id"]
        product_id = review["product_id"]
        product_name = review["product_name"]
        review_text = review["review_text"]
        rating = review["rating"]
        timestamp = review.get("timestamp", "")
        
        # 1. Add full review to reviews_collection
        reviews_collection.add(
            ids=[str(uuid.uuid4())],
            documents=[review_text],
            metadatas=[{
                "review_id": review_id,
                "product_id": product_id,
                "product_name": product_name,
                "rating": rating,
                "timestamp": timestamp
            }]
        )
        
        # 2. Extract opinions using LLM
        opinions = extract_opinions(review_text)
        
        # 3. Process each opinion
        for i, op in enumerate(opinions):
            aspect_normalized = normalize_aspect(op.get("aspect", "other"))
            
            opinions_collection.add(
                ids=[str(uuid.uuid4())],
                documents=[op.get("phrase", "")],
                metadatas=[{
                    "opinion_id": f"{review_id}_{i}",
                    "review_id": review_id,
                    "product_id": product_id,
                    "product_name": product_name,
                    "aspect": op.get("aspect", ""),
                    "aspect_normalized": aspect_normalized,
                    "sentiment": op.get("sentiment", "mixed")
                }]
            )
    
    print(f"Processed {len(reviews)} reviews")
    print(f"Reviews collection: {reviews_collection.count()}")
    print(f"Opinions collection: {opinions_collection.count()}")
```

### Phase 4: Query & Response Generation

```python
def generate_answer(query: str, product_id: str = None):
    """Main query handler - classifies, retrieves, generates response."""
    
    # 1. Classify query
    classification = classify_query(query)
    intent = classification["intent"]
    sentiment_filter = classification["sentiment_filter"]
    aspect_hint = classification["aspect_hint"]
    
    # 2. Retrieve based on intent
    if intent == "retrieval":
        docs = retrieve_reviews_by_sentiment(
            query=query,
            product_id=product_id,
            sentiment=sentiment_filter or "negative",
            n_results=5
        )
        prompt = RETRIEVAL_PROMPT
    else:
        docs = retrieve_opinions(
            query=query,
            product_id=product_id,
            sentiment=sentiment_filter,
            aspect=aspect_hint,
            n_results=15
        )
        prompt = SUMMARY_PROMPT
    
    if not docs:
        return "I could not find relevant reviews for that query."
    
    # 3. Format context
    context = "
".join([f"- {d['text']}" for d in docs])
    product_name = docs[0].get("product_name", "this product")
    
    # 4. Generate response
    final_prompt = prompt.format(
        product_name=product_name,
        query=query,
        context=context
    )
    
    response = llm.invoke(final_prompt)
    return response.content
```

---

## 12. MVP Deliverables (Tuesday)

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | S3 Bucket | Sample reviews: 50-100 reviews across 3-5 products |
| 2 | Phase 1 Cells | AWS + ChromaDB setup and initialization |
| 3 | Phase 2 Cells | S3 ingestion and JSON parsing |
| 4 | Phase 3 Cells | Aspect extraction + embedding pipeline |
| 5 | Phase 4 Cells | Retrieval + generation functions |
| 6 | Demo | End-to-end query examples working |

---

## 13. Sample Data Structure

### Sample Products

```json
[
  {"product_id": "p_keyboard_2025", "product_name": "Mac 2025 Keyboard"},
  {"product_id": "p_airpods_pro", "product_name": "AirPods Pro 2"},
  {"product_id": "p_macbook_m4", "product_name": "MacBook Pro M4"}
]
```

### Reviews Per Product

- 20-30 reviews each
- Mix of positive, negative, mixed sentiment
- Cover multiple aspects (battery, price, design, performance, etc.)
- Ratings distributed 1-5 stars

---

## 14. Success Criteria

| Criteria | Metric |
|----------|--------|
| Aspect Accuracy | Extracted aspects match human judgment |
| Sentiment Correctness | Positive opinions not labeled negative |
| Query Understanding | System interprets like/dislike correctly |
| Grounded Responses | Summaries reflect retrieved opinions |
| Useful Granularity | Responses distinguish between aspects |
| Latency | < 5 seconds per query |

---

## 15. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| LLM extracts wrong aspects | Validate against star rating; spot-check |
| Aspect normalization misses synonyms | Start small taxonomy; expand on errors |
| Vague queries | Default to top 3 liked + top 3 disliked |
| Not enough opinions per aspect | Return "limited feedback" honestly |
| Bedrock rate limits | Batch processing; add delays |

---

*Document Version: 1.0*  
*Last Updated: January 2025*  
*Project Due: Tuesday*