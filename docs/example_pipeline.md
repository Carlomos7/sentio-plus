Got it — here’s the **pipeline again**, using that same “outline example” style (clear stages + example inputs/outputs), and explicitly matching your requirements: **S3 → local code → ChromaDB → Bedrock LLM → RAG pipeline → business insights**.

---

# VoC Intelligence Agent — Pipeline (Reference Format)

## 0. Pipeline Goal

**Goal:** Turn raw product reviews into **evidence-backed business insights** using a **RAG pipeline**.

---

## 1. Input: Raw Reviews in Amazon S3

### **Input (stored in S3)**

**S3 Object (example):** `s3://voc-reviews/raw/macbook_2025_reviews.jsonl`

```json
{
  "review_id": "r_10234",
  "product_id": "macbook_2025",
  "rating": 2,
  "review_text": "The keyboard feels nice at first, but after two weeks it started missing keystrokes. Very frustrating.",
  "timestamp": "2025-01-12"
}
```

### **Output of this step**

✅ Raw review data is available for local processing.

---

## 2. Local Code: Load + Validate + Normalize

### **Input**

* S3 raw data objects (JSONL / CSV)
* Local config: columns expected, schema rules (optional)

### **Output**

A clean standardized record (same schema for all downstream steps):

```json
{
  "review_id": "r_10234",
  "product_id": "macbook_2025",
  "rating": 2,
  "review_text": "The keyboard feels nice at first, but after two weeks it started missing keystrokes. Very frustrating.",
  "timestamp": "2025-01-12"
}
```

---

## 3. Local Code: Sentiment Scoring (Your Sentiment Model)

### **Input to sentiment model**

```text
"The keyboard feels nice at first, but after two weeks it started missing keystrokes."
```

### **Output**

```json
{
  "sentiment": "negative",
  "confidence": 0.93
}
```

---

## 4. Local Code: Enrichment (Attach Sentiment + Metadata)

### **Input**

* Clean review record
* Sentiment model output

### **Output: Enriched record**

```json
{
  "review_id": "r_10234",
  "product_id": "macbook_2025",
  "rating": 2,
  "review_text": "The keyboard feels nice at first, but after two weeks it started missing keystrokes. Very frustrating.",
  "timestamp": "2025-01-12",
  "sentiment": "negative",
  "confidence": 0.93
}
```

---

## 5. Local Code: Embedding + Upsert into ChromaDB

### **Input**

* `review_text`
* metadata (product_id, sentiment, rating, timestamp, etc.)

### **Output: ChromaDB stored item**

(embedding shortened)

```json
{
  "id": "r_10234",
  "embedding": [0.012, -0.442, 0.891, "..."],
  "document": "The keyboard feels nice at first, but after two weeks it started missing keystrokes. Very frustrating.",
  "metadata": {
    "product_id": "macbook_2025",
    "sentiment": "negative",
    "rating": 2,
    "timestamp": "2025-01-12",
    "confidence": 0.93
  }
}
```

✅ Now your review corpus is searchable by **meaning**, and filterable by **metadata**.

---

## 6. Input: Business Question (User Query)

### **User Input**

```text
Why are customers unhappy with the MacBook 2025 keyboard?
```

---

## 7. RAG — Retrieval Step (ChromaDB Query)

### **Input**

* Embedded user question
* Filters (typical):

  * `product_id = macbook_2025`
  * optionally `sentiment = negative`
  * optionally time window (last 30 days)

### **Output: Retrieved evidence (Top-K reviews)**

```json
[
  {
    "review_text": "The keyboard started missing keystrokes after two weeks.",
    "rating": 2,
    "timestamp": "2025-01-12"
  },
  {
    "review_text": "Keys feel good initially, but reliability drops quickly.",
    "rating": 1,
    "timestamp": "2025-01-18"
  },
  {
    "review_text": "After the January update, typing became inconsistent.",
    "rating": 2,
    "timestamp": "2025-01-20"
  }
]
```

✅ This is the **R** in RAG: **Retrieval**.

---

## 8. RAG — Augmented Prompt to AWS Bedrock LLM

### **Input to Bedrock (prompt with evidence)**

```text
Role: You are a consulting-style business insights assistant.

Business Question:
"Why are customers unhappy with the MacBook 2025 keyboard?"

Retrieved Customer Evidence:
1) "The keyboard started missing keystrokes after two weeks."
2) "Keys feel good initially, but reliability drops quickly."
3) "After the January update, typing became inconsistent."

Task:
- Summarize the root causes
- Mention trend signals if present (new vs recurring)
- Provide actionable business recommendations
- Keep output concise and executive-friendly
```

✅ This is the **A** in RAG: **Augment**.

---

## 9. Output: Business Insights (Final Generated Answer)

### **Final Output**

> **Summary:** Customer dissatisfaction is driven mainly by keyboard reliability issues emerging after short-term use.
> **Root causes:** Reviews frequently cite missed keystrokes and inconsistent typing, sometimes tied to a recent update.
> **Trend signal:** Complaints are concentrated in recent dates, suggesting an emerging issue rather than isolated cases.
> **Recommendation:** Prioritize QA investigation into durability and post-update behavior, and consider proactive customer communication to reduce rating impact.

✅ This is the **G** in RAG: **Generation**.

---

## 10. Optional: Persist Outputs Back to S3 (for reporting)

### **Output stored to S3**

* Executive summaries (daily/weekly)
* Trend snapshots
* Evidence bundles used for explainability

Example:
`S3://voc-reviews/insights/weekly/macbook_2025_keyboard_week02.json`

---

# One-line version (how you say it)

> “Reviews live in S3, local code runs sentiment + embeddings, ChromaDB retrieves the most relevant evidence, and Bedrock generates an executive-style insight grounded in real customer quotes.”

If you want, paste your **exact column names** (or your current folder structure), and I’ll tailor this pipeline so it matches your repo 1:1 (names, paths, and step order).
