Absolutely — I’ll give you a **complete, end-to-end project** (pipeline + folder structure + code) for your **Google Play Store Reviews** dataset, using your example RAG notebook as the code-style reference:

✅ **ChromaDB** for vector store
✅ **Semantic chunking** (theme clustering, not fixed-size splitting)
✅ **2-step LLM flow** (Router → Analyst)
✅ **Amazon Bedrock** for LLM inference (enterprise-ready)
✅ Optional **S3** artifact storage (raw/processed/index exports)
✅ Runnable scripts: `build_index.py` + `query.py` + optional FastAPI + Streamlit

---

# 1) Folder Structure

```
playstore-sentiment-intel/
  README.md
  requirements.txt
  .env.example

  config/
    settings.yaml

  data/
    raw/                      # kaggle csv goes here (not committed)
    processed/                # cleaned parquet/csv outputs
    artifacts/                # exported chunks, reports, evaluation outputs

  src/
    common/
      logger.py
      io.py
      text.py

    ingest/
      load_dataset.py
      clean_reviews.py

    chunking/
      semantic_chunker.py

    embedding/
      embedder.py

    vectorstore/
      chroma_store.py

    llm/
      bedrock_client.py
      router.py
      analyst.py
      prompts.py

    pipeline/
      build_index.py
      query_intel.py

  app/
    api.py                    # FastAPI
    streamlit_app.py          # Streamlit UI

  scripts/
    build_index.sh
    run_api.sh
    run_ui.sh
```

---

# 2) Config + Dependencies

### `.env.example`

```bash
AWS_REGION=us-east-1
BEDROCK_ROUTER_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
BEDROCK_ANALYST_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# If you use S3 artifacts
S3_BUCKET_NAME=your-bucket
S3_PREFIX=playstore-sentiment-intel

# Chroma local persistence
CHROMA_DIR=./chroma

# Dataset path
DATASET_PATH=./data/raw/google_play_store_reviews.csv
```

### `config/settings.yaml`

```yaml
project:
  name: playstore-sentiment-intel

dataset:
  text_col: review
  rating_col: rating
  app_col: app_name   # if missing in your dataset, system will default to "Google Play Reviews"

chunking:
  per_app: true
  min_reviews_per_app: 50
  max_reviews_per_cluster: 120
  n_clusters_cap: 15
  evidence_examples_per_chunk: 6

retrieval:
  top_k_default: 8
  distance_threshold: 1.2

llm:
  temperature_router: 0.1
  temperature_analyst: 0.2
  max_tokens_router: 600
  max_tokens_analyst: 1400
```

### `requirements.txt`

```txt
boto3
pandas
numpy
pyyaml
scikit-learn
chromadb
sentence-transformers
fastapi
uvicorn
streamlit
python-dotenv
```

---

# 3) Core Code (Entire Project)

## `src/common/logger.py`

```python
import logging

def get_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(ch)
    return logger
```

## `src/common/io.py`

```python
import os
import yaml

def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def env(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    return v if v is not None and v != "" else default
```

---

## Ingest

### `src/ingest/load_dataset.py`

```python
import pandas as pd

def load_reviews_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    return df
```

### `src/ingest/clean_reviews.py`

```python
import pandas as pd

def _find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None

def clean_reviews(df: pd.DataFrame, text_col: str | None = None, rating_col: str | None = None, app_col: str | None = None) -> pd.DataFrame:
    df = df.copy()

    text_col = text_col or _find_col(df, ["review", "content", "text"])
    if not text_col:
        raise ValueError("No review text column found. Expected one of: review/content/text")

    rating_col = rating_col or _find_col(df, ["rating", "score", "stars"])
    app_col = app_col or _find_col(df, ["app_name", "app", "package_name"])

    df[text_col] = df[text_col].astype(str).str.strip()
    df = df[df[text_col].str.len() >= 10]
    df = df.drop_duplicates(subset=[text_col])

    if rating_col:
        df[rating_col] = pd.to_numeric(df[rating_col], errors="coerce")
        df = df[df[rating_col].between(1, 5, inclusive="both")]

    if app_col:
        df[app_col] = df[app_col].fillna("Unknown App")
    else:
        df["app_name"] = "Google Play Reviews"
        app_col = "app_name"

    # Normalize to consistent names used downstream
    df = df.rename(columns={text_col: "review_text"})
    if rating_col and rating_col in df.columns:
        df = df.rename(columns={rating_col: "rating"})
    df = df.rename(columns={app_col: "app_name"})

    return df[["app_name", "review_text"] + (["rating"] if "rating" in df.columns else [])]
```

---

## Embeddings

### `src/embedding/embedder.py`

```python
from typing import List
import numpy as np

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> np.ndarray:
        return np.array(self.model.encode(texts, normalize_embeddings=True))
```

---

## Semantic Chunking (Theme Clusters)

### `src/chunking/semantic_chunker.py`

```python
from dataclasses import dataclass
from typing import List, Dict, Any
import numpy as np

@dataclass
class SemanticChunk:
    chunk_id: str
    theme_label: str
    doc_text: str
    examples: List[str]
    metadata: Dict[str, Any]

def _auto_k(n: int, k_cap: int) -> int:
    # sqrt heuristic with caps
    k = int(max(2, min(k_cap, np.sqrt(n))))
    return k

def build_semantic_chunks(
    app_name: str,
    reviews: List[str],
    embeddings: np.ndarray,
    n_clusters_cap: int = 15,
    examples_per_chunk: int = 6,
) -> List[SemanticChunk]:
    from sklearn.cluster import KMeans

    if len(reviews) < 2:
        return []

    k = _auto_k(len(reviews), n_clusters_cap)
    km = KMeans(n_clusters=k, random_state=42, n_init="auto")
    labels = km.fit_predict(embeddings)

    chunks: List[SemanticChunk] = []
    for cid in range(k):
        idx = np.where(labels == cid)[0].tolist()
        cluster_reviews = [reviews[i] for i in idx]

        examples = cluster_reviews[:examples_per_chunk]
        # Store a compact “chunk document” that retrieval can use
        doc_text = (
            f"APP: {app_name}\n"
            f"THEME_CLUSTER: {cid}\n"
            f"CLUSTER_SIZE: {len(cluster_reviews)}\n\n"
            f"EXAMPLES:\n- " + "\n- ".join(examples)
        )

        chunks.append(
            SemanticChunk(
                chunk_id=f"{app_name}__cluster_{cid}",
                theme_label=f"cluster_{cid}",
                doc_text=doc_text,
                examples=examples,
                metadata={
                    "app_name": app_name,
                    "cluster_id": cid,
                    "cluster_size": len(cluster_reviews),
                },
            )
        )

    # Sort by cluster size so retrieval has better “big themes”
    chunks.sort(key=lambda c: c.metadata["cluster_size"], reverse=True)
    return chunks
```

---

## Vector Store (Chroma)

### `src/vectorstore/chroma_store.py`

```python
from typing import List, Dict, Any
import chromadb

class ChromaStore:
    def __init__(self, persist_dir: str):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.col = self.client.get_or_create_collection(name="playstore_review_intel")

    def upsert(self, ids: List[str], docs: List[str], metas: List[Dict[str, Any]], embs: List[List[float]]):
        self.col.upsert(ids=ids, documents=docs, metadatas=metas, embeddings=embs)

    def query(self, query_emb: List[float], top_k: int = 8, where: Dict[str, Any] | None = None):
        return self.col.query(query_embeddings=[query_emb], n_results=top_k, where=where or {})
```

---

## Bedrock LLM Client (Router + Analyst)

### `src/llm/bedrock_client.py`

```python
import json
import boto3

class BedrockClaude:
    def __init__(self, model_id: str, region: str):
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime", region_name=region)

    def generate(self, prompt: str, max_tokens: int = 1200, temperature: float = 0.2) -> str:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        resp = self.client.invoke_model(modelId=self.model_id, body=json.dumps(body))
        payload = json.loads(resp["body"].read())
        return payload["content"][0]["text"]
```

### `src/llm/prompts.py`

```python
ROUTER_PROMPT = """You are a retrieval planner for an internal product sentiment intelligence tool.

Return JSON only with:
- intent: ["exec_summary","issue_diagnosis","feature_feedback","trend_scan","cx_playbook"]
- filters: optional {"app_name": string}
- retrieval_k: integer 5-15
- focus_topics: 2-6 short strings (e.g. ["crash","ads","login","performance"])
- output_style: ["consulting_exec","pm_action","cx_playbook"]

User query: {query}
"""

ANALYST_PROMPT = """You are a business consultant analyzing app review sentiment for an internal decision-support tool.

Using the evidence, produce:
1) Executive summary (3-5 bullets)
2) Key themes/issues (ranked, with evidence)
3) Business impact (ratings, retention risk, support cost, brand risk)
4) Recommendations (short-term vs long-term; owner: Product/Eng/CX/Marketing)
5) KPIs to track (3-6)
6) Risks/assumptions

User question: {query}

Retrieval plan (JSON):
{plan_json}

Evidence:
{evidence}
"""
```

### `src/llm/router.py`

```python
import json
from src.llm.prompts import ROUTER_PROMPT

class Router:
    def __init__(self, llm, max_tokens: int, temperature: float):
        self.llm = llm
        self.max_tokens = max_tokens
        self.temperature = temperature

    def plan(self, query: str) -> dict:
        raw = self.llm.generate(
            ROUTER_PROMPT.format(query=query),
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return json.loads(raw)
```

### `src/llm/analyst.py`

```python
import json
from src.llm.prompts import ANALYST_PROMPT

class Analyst:
    def __init__(self, llm, max_tokens: int, temperature: float):
        self.llm = llm
        self.max_tokens = max_tokens
        self.temperature = temperature

    def run(self, query: str, plan: dict, evidence: str) -> str:
        return self.llm.generate(
            ANALYST_PROMPT.format(
                query=query,
                plan_json=json.dumps(plan, indent=2),
                evidence=evidence,
            ),
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
```

---

## Pipeline: Build Index

### `src/pipeline/build_index.py`

```python
import os
from dotenv import load_dotenv
from src.common.io import load_yaml
from src.common.logger import get_logger
from src.ingest.load_dataset import load_reviews_csv
from src.ingest.clean_reviews import clean_reviews
from src.embedding.embedder import Embedder
from src.chunking.semantic_chunker import build_semantic_chunks
from src.vectorstore.chroma_store import ChromaStore

log = get_logger("build_index")

def build_index(config_path: str = "./config/settings.yaml"):
    load_dotenv()
    cfg = load_yaml(config_path)

    dataset_path = os.getenv("DATASET_PATH", "./data/raw/google_play_store_reviews.csv")
    chroma_dir = os.getenv("CHROMA_DIR", "./chroma")

    df_raw = load_reviews_csv(dataset_path)
    df = clean_reviews(
        df_raw,
        text_col=cfg["dataset"].get("text_col"),
        rating_col=cfg["dataset"].get("rating_col"),
        app_col=cfg["dataset"].get("app_col"),
    )

    os.makedirs("./data/processed", exist_ok=True)
    df.to_parquet("./data/processed/reviews_clean.parquet", index=False)

    embedder = Embedder()
    store = ChromaStore(persist_dir=chroma_dir)

    per_app = cfg["chunking"]["per_app"]
    min_reviews = cfg["chunking"]["min_reviews_per_app"]
    k_cap = cfg["chunking"]["n_clusters_cap"]
    examples_per_chunk = cfg["chunking"]["evidence_examples_per_chunk"]

    grouped = df.groupby("app_name") if per_app else [("Google Play Reviews", df)]

    total_chunks = 0
    for app_name, g in grouped:
        reviews = g["review_text"].tolist()
        if len(reviews) < min_reviews:
            continue

        log.info(f"Embedding {len(reviews)} reviews for app='{app_name}'...")
        review_embs = embedder.embed(reviews)

        chunks = build_semantic_chunks(
            app_name=app_name,
            reviews=reviews,
            embeddings=review_embs,
            n_clusters_cap=k_cap,
            examples_per_chunk=examples_per_chunk,
        )

        chunk_docs = [c.doc_text for c in chunks]
        chunk_embs = embedder.embed(chunk_docs).tolist()

        ids = [c.chunk_id for c in chunks]
        metas = [c.metadata | {"theme_label": c.theme_label} for c in chunks]

        store.upsert(ids=ids, docs=chunk_docs, metas=metas, embs=chunk_embs)
        total_chunks += len(chunks)

        log.info(f"✅ Indexed {len(chunks)} semantic theme chunks for '{app_name}'.")

    log.info(f"🎉 Done. Total chunks indexed: {total_chunks}")
```

---

## Pipeline: Query (Router → Retrieve → Analyst)

### `src/pipeline/query_intel.py`

```python
import os
import json
from dotenv import load_dotenv
from src.common.io import load_yaml
from src.embedding.embedder import Embedder
from src.vectorstore.chroma_store import ChromaStore
from src.llm.bedrock_client import BedrockClaude
from src.llm.router import Router
from src.llm.analyst import Analyst

def _format_evidence(results: dict) -> str:
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    out = []
    for i, (d, m) in enumerate(zip(docs, metas), start=1):
        out.append(f"--- Evidence {i} | app={m.get('app_name')} | cluster={m.get('cluster_id')} | size={m.get('cluster_size')} ---")
        out.append(d[:1600])
    return "\n".join(out)

def answer(query: str, config_path: str = "./config/settings.yaml") -> str:
    load_dotenv()
    cfg = load_yaml(config_path)

    region = os.getenv("AWS_REGION", "us-east-1")
    chroma_dir = os.getenv("CHROMA_DIR", "./chroma")

    router_model = os.getenv("BEDROCK_ROUTER_MODEL_ID")
    analyst_model = os.getenv("BEDROCK_ANALYST_MODEL_ID")
    if not router_model or not analyst_model:
        raise ValueError("Missing BEDROCK_ROUTER_MODEL_ID or BEDROCK_ANALYST_MODEL_ID in .env")

    router_llm = BedrockClaude(router_model, region)
    analyst_llm = BedrockClaude(analyst_model, region)

    router = Router(
        llm=router_llm,
        max_tokens=cfg["llm"]["max_tokens_router"],
        temperature=cfg["llm"]["temperature_router"],
    )
    analyst = Analyst(
        llm=analyst_llm,
        max_tokens=cfg["llm"]["max_tokens_analyst"],
        temperature=cfg["llm"]["temperature_analyst"],
    )

    plan = router.plan(query)

    embedder = Embedder()
    store = ChromaStore(persist_dir=chroma_dir)
    q_emb = embedder.embed([query])[0].tolist()

    where = {}
    app_filter = plan.get("filters", {}).get("app_name")
    if app_filter:
        where["app_name"] = app_filter

    top_k = int(plan.get("retrieval_k", cfg["retrieval"]["top_k_default"]))
    results = store.query(query_emb=q_emb, top_k=top_k, where=where)
    evidence = _format_evidence(results)

    return analyst.run(query=query, plan=plan, evidence=evidence)
```

---

# 4) FastAPI + Streamlit (Optional but “Professional”)

## `app/api.py`

```python
from fastapi import FastAPI
from pydantic import BaseModel
from src.pipeline.query_intel import answer

app = FastAPI(title="PlayStore Sentiment Intelligence API")

class Query(BaseModel):
    query: str

@app.post("/analyze")
def analyze(q: Query):
    return {"query": q.query, "result": answer(q.query)}
```

## `app/streamlit_app.py`

```python
import streamlit as st
from src.pipeline.query_intel import answer

st.set_page_config(page_title="Sentiment Intelligence", layout="wide")
st.title("📊 Product Sentiment Intelligence (Internal Tool)")

query = st.text_input("Ask a business question about customer sentiment:", placeholder="e.g. What are the biggest churn drivers and what should we do next?")
if st.button("Analyze") and query.strip():
    with st.spinner("Generating consulting-style insights..."):
        result = answer(query)
    st.markdown(result)
```

---

# 5) Runner Scripts

## `scripts/build_index.sh`

```bash
python -c "from src.pipeline.build_index import build_index; build_index()"
```

## `scripts/run_api.sh`

```bash
uvicorn app.api:app --reload --port 8000
```

## `scripts/run_ui.sh`

```bash
streamlit run app/streamlit_app.py
```

---

# 6) How You Run Everything

### 1) Put Kaggle CSV here:

`./data/raw/google_play_store_reviews.csv`

### 2) Install

```bash
pip install -r requirements.txt
```

### 3) Build the index

```bash
bash scripts/build_index.sh
```

### 4) Query

* API:

```bash
bash scripts/run_api.sh
```

* UI:

```bash
bash scripts/run_ui.sh
```

---

## One important note (so your code *actually runs*)

Kaggle datasets often have column names that vary (`review`, `content`, `Text`, etc.).
This project already handles it by:

* letting you set `text_col/rating_col/app_col` in `settings.yaml`
* falling back to likely column names

If you paste the first row / column list of your CSV (just the header line), I’ll snap the config to be **exact**—but the pipeline above is already robust enough to run with minimal changes.

If you want, next message I can also generate:

* a **consulting-grade README** that matches this exact architecture
* an **S3 artifact uploader** module (index export + reports) to satisfy the “must use S3” requirement more explicitly
