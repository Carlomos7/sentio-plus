# Initial RAG Outline

```mint
sentio-plus/
└── app/
    ├── __init__.py
    ├── main.py # FastAPI entry point
    ├── config.py # pydantic settings (s3 bucket, chroma path, bedrock model ID)
    ├── services/
    │   ├── __init__.py
    │   ├── vector_store.py # chromaDB ~ init, add_docs, query
    │   ├── llm.py # ChatBderock client wrapper
    │   ├── rag.py # Orchestration: retrieve -> generate
    │   └── ingest.py # chunk text -> call vector_store.add()
    ├── prompts/
    │   ├── __init__.py
    │   └── templates.py # rag prompt
    ├── schemas/
    │   ├── __init__.py
    │   └── api.py # Pydantic models (queryRequest, ReviewResponses, etc.)
    ├── routes/
    │   ├── __init__.py
    │   ├── query.py # POST /query endpoint
    │   └── ingest.py # POST /ingest endpoint (stretch)
    ├── chroma_data/ # mounted vol for persistent ChromaDB/
    │   └── .gitkeep
    ├── notebooks/ # jupyter notebooks
    ├── pyproject.toml
    ├── Dockerfile
    ├── docker-compose.yml
    ├── .dockerignore
    ├── .gitignore
    └── README.md
```