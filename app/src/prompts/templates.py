"""Prompt templates for RAG pipeline."""

SOURCE_SELECTION_PROMPT = """You are given a list of app names from product reviews.
Return ONLY the names of the apps that are relevant to the question.
If none are relevant, return "none".
Do not explain your reasoning.

Apps:
{sources}

Question:
{query}

Return format (comma-separated):
app1, app2, app3"""


RAG_PROMPT = """You are a helpful assistant analyzing product reviews. Use the following review excerpts to answer the question.

Rules:
1. Be concise and direct.
2. Base your answer ONLY on the provided reviews.
3. If the reviews don't contain relevant information, say so.
4. Mention specific apps when relevant.
5. Include sentiment (positive/negative) when discussing features.

Reviews:
{context}

Question: {question}

Answer:"""


SIMPLE_PROMPT = """You are a helpful assistant. Answer the following question concisely.

Question: {question}

Answer:"""