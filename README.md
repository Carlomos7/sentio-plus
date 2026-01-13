# Sentio+

## Overview
Sentio+ is an AI-powered **decision-support platform** that transforms large-scale, unstructured customer review data into **actionable business insights** using a Retrieval-Augmented Generation (RAG) architecture. It is designed as an **internal intelligence tool** for Product, CX, Strategy, and Leadership teams to understand why customers feel the way they do and what actions should be taken as a result.

Unlike traditional sentiment dashboards that stop at positive vs. negative classification, Sentio+ enables **aspect-level reasoning** over customer feedback, grounding every insight directly in real review evidence.

---

## Core Problem Being Solved
Most sentiment analysis systems answer what customers feel, but fail to explain:

- **Why** customers are dissatisfied

- **Which product aspects** (e.g., usability, payments, performance, pricing) are driving ratings

- What **teams should fix first** to improve outcomes

Sentio+ addresses this gap by combining:

- Structured sentiment signals (ratings, categories, segments)

- Semantic retrieval over raw review text

- LLM-based synthesis grounded in retrieved evidence

This allows teams to ask business-critical questions such as:

- "What usability issues are driving 1-star reviews in Finance apps?"

- "How have payment-related complaints evolved over the last 6 months?"

- "What features do users in the 'Everyone' content segment value most?"

The system translates unstructured feedback into **decision-ready insights** that inform product prioritization, roadmap planning, and customer experience improvements.

---

## High-Level Architecture
<!-- insert architecture diagram-->

Sentio+ follows a **modular Retrieval-Augmented Generation (RAG) architecture** designed for scalability, traceability, and business interpretability. The system is structured to ensure that every generated insight is grounded in real customer evidence and aligned with decision-making needs.

### Architecture Flow
    Data → Embeddings → Retrieval → LLM Reasoning → Business Insight

### Design Principles
- Evidence-first answers (no hallucinated insights)

- Clear separation of preprocessing, retrieval, and generation

- Metadata-aware retrieval for precise filtering and analysis

---

## Tech Stack

### Data & Preprocessing
- **Python** for ETL and preprocessing logic

- **Pandas / NumPy** for data cleaning and transformation

- **Jupyter Notebooks** (```/notebooks``) for exploration, validation, and iterative development

- **KaggleHub** for dataset retrieval

### Vector Storage & Retrieval
- **ChromaDB** for vector persistence and semantic search

- Metadata-aware indexing (category, rating, date, segment)

- Cosine similarity–based retrieval

### LLM & RAG Layer
- **AWS Bedrock LLMs** for grounded text generation

- Retrieval-Augmented Generation (RAG) with top-K semantic search

- Two-step reasoning: retrieval → synthesis

### Backend
- **Python RAG services** for embedding, retrieval, and response assembly

- API-based LLM invocation

### Frontend
- **Next.js** web application (```/web```)

- Chat-style interface for natural language queries

- Streaming responses with cited evidence

- Interactive drill-down into retrieved review excerpts

### Storage & Infrastructure
- **Amazon S3** for raw and processed dataset storage
- Local execution for development with cloud-based model services

---

## Data
Sentio+ is powered by the [Google Play Store Reviews](https://www.kaggle.com/datasets/prakharrathi25/google-play-store-reviews/data) dataset.

- **Source:** Kaggle – Google Play Market Reviews
- **Scale:** ~1M reviews across ~500 app titles (subset used during prototyping)
- **Key Fields:**

    - Review text

    - Star rating (1–5)

    - App category

    - Review date

    - Content rating (Everyone, Teen, etc.)

**Purpose:** Enable fine-grained analysis of customer sentiment, feature requests, and recurring pain points across app categories.

---

## Key Innovation: Hybrid Stratified Signal Sampling
Rather than relying on naive random sampling, Sentio+ implements a **hybrid stratified sampling strategy** to maximize signal quality.

1. **Breadth (Coverage):** Reviews are balanced across all categories (Finance, Social, Productivity, etc.) and ratings (1-5 stars)

2. **Depth (Signal Quality)** Within each category/rating bucket, you prioritize:

    - Long reviews (>150 characters) for detailed evidence

    - Helpful reviews (high helpful_count) for peer-vetted insights

    - Recent reviews (~60% from last 12 months) for current relevance

The resulting dataset treats each review as **high-information testimony**, avoiding low-signal noise such as one-word feedback ("Good app"). This dramatically improves downstream retrieval and LLM reasoning quality.

---

## RAG Architecture
### Phase 1: Preprocessing & Indexing
1. Merge review data (```apps_reviews.csv```) with app metadata (```apps_info.csv```)

2. Clean categories, filter for quality (length, helpfulness)

3. Create enriched text with context headers:

```
[APP: Google Wallet | CAT: Finance | RATING: 1/5 | DATE: 2024-09 | SEGMENT: Everyone] 
USER REVIEW: The payment gateway keeps timing out.
```
4. Load into ChromaDB with dual metadata (structured fields + enriched text)

### Phase 2: Query & Retrieval 
1. User asks a natural language question

2. System performs semantic search in ChromaDB (with optional hard filters by category, date, rating)

3. Rerank results by helpfulness/recency

4. Retrieve top-K most relevant review chunks

### Phase 3: Generation & Grounding
1. LLM synthesizes insights from retrieved reviews

2. Response includes citations linking back to specific review_ids

3. UI displays original review excerpts as evidence

4. Users can drill down to full review context

---

## Key Capabilities
- Large-scale review ingestion via S3

- Aspect-level sentiment reasoning

- Metadata-aware semantic search

- Evidence-grounded natural language insights

- Trend detection across time and categories

- Business-ready summaries for non-technical stakeholders

---

## Example Walkthrough
### User Question
    "Why are 1-star reviews increasing for Finance apps in the last 6 months?"

### Retrieval Step
- Filters applied: category = Finance, rating = 1, date >= last 6 months
- Top-K reviews retrieved mentioning payment failures, login issues, and crashes

### LLM Synthesis Output
    "Recent 1-star reviews in Finance apps are primarily driven by payment gateway timeouts and authentication failures following recent updates. Multiple users report being unable to complete transactions, leading to trust and reliability concerns."

### Evidence (Cited Reviews)
- Review A (2024-09): "The payment gateway keeps timing out during checkout"
- Review B (2024-10): "After the update, I can't log in anymore"

This ensures every insight is **explainable, auditable, and trusted.**

---

## Example Queries
- "What are the most common reasons for 1-star reviews in Finance apps?"
- "Which features are users requesting most in the last quarter?"
- "How do Teen-rated app complaints differ from Everyone-rated apps?"
- "What issues are driving churn-related feedback this year?"

---

## Business Use Cases
### Product Teams
- Identify top recurring bugs and UX pain points
- Prioritize features based on real customer impact

### Strategy & Leadership
- Detect systemic issues across product lines
- Inform roadmap and investment decisions

## Customer Experience (CX)
- Understand root causes of negative sentiment
- Track shifts in customer perception over time

---

## Setup & Local Development
### 1. Clone the repository

``` 
git clone https://github.com/Carlomos7/sentio-plus.git
```
This project requires **Python 3.13 or higher and Docker.**

### 2. Set up Python environment and dependencies

### 3. Download dataset via Kagglehub

### 4. Run preprocessing notebooks/ETL scripts

### 5. Start ChromaDB and index embeddings

### 6. Launch backend services

### Run Next.js frontend

---

## Evaluation & Quality Considerations
While Sentio+ prioritizes decision support over raw accuracy metrics, quality is evaluated through:

- **Retrieval relevance:** Are returned reviews actually answering the question?
- **Groundedness:** Are all claims supported by cited evidence?
- **Business usefulness:** Do insights translate into clear action items?
- **Consistency:** Do similar queries yield stable themes over time?

Future work may introduce quantitative evaluation (e.g., retrieval precision@K, human-in-the-loop validation).

---

## Project Positioning: Use Cases
Sentio+ is intentionally designed as a consulting-grade internal analytics tool, not a consumer chatbot. Its primary value lies in converting raw customer feedback into strategic, explainable insights that organizations can act on with confidence.

1. **Product Prioritization:** "What are the top 3 recurring bugs users want fixed in Finance apps?"
2. **Competitive Analysis:** "How do user complaints about subscription pricing compare across categories?"
3. **Roadmap Planning:** "What features are users requesting most in the last quarter?"CX Improvements: "Why are 1-star reviews spiking for our top apps?"
4. **Audience Insights:** "What do Teen-rated app users complain about vs Everyone-rated apps?"

<!--link to detailed business logic-->

---

## Future Enhancements

---

## Contributors
<p align="center">
  <i>This project was originally collaborated on in Google Colab by:</i>
</p>

<p align="center">
  <a href="https://github.com/Carlomos7">
    <img src="https://avatars.githubusercontent.com/u/106279547?v=4" width="90px;" style="border-radius:50%;" alt="Carlos Segarra"/>
  </a>
  <a href="https://github.com/KyleAnthonyHay">
    <img src="https://avatars.githubusercontent.com/u/100221659?v=4" width="90px;" style="border-radius:50%;" alt="Kyle Anthony Hay"/>
  </a>
  <a href="https://github.com/chenchenchen12345">
    <img src="https://avatars.githubusercontent.com/u/109692467?v=4" width="90px;" style="border-radius:50%;" alt="Chenchen Liu"/>
  </a>
  <a href="https://github.com/JeffreyM10">
    <img src="https://avatars.githubusercontent.com/u/78449631?v=4" width="90px;" style="border-radius:50%;" alt="Jeffrey Mazariegos"/>
  </a>
  <a href="https://github.com/marlonmunoz">
    <img src="https://avatars.githubusercontent.com/u/48579081?v=4" width="90px;" style="border-radius:50%;" alt="Marlon Munoz"/>
  </a>
  <a href="https://github.com/Hayden-Ferguson">
    <img src="https://avatars.githubusercontent.com/u/105685979?v=4" width="90px;" style="border-radius:50%;" alt="Hayden Ferguson"/>
  </a>
</p>

<p align="center">
  <a href="https://github.com/Carlomos7"><b>Carlos</b></a> •
  <a href="https://github.com/KyleAnthonyHay"><b>Kyle</b></a> •
  <a href="https://github.com/chenchenchen12345"><b>Chenchen</b></a> •
  <a href="https://github.com/JeffreyM10"><b>Jeffrey</b></a> •
  <a href="https://github.com/marlonmunoz"><b>Marlon</b></a> •
  <a href="https://github.com/Hayden-Ferguson"><b>Hayden</b></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Team-6%20Members-blueviolet?style=for-the-badge" alt="Team Size"/>
</p>




