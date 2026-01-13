'''Application Configurations'''
from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Paths: app/src/config/settings.py -> app/ -> project root
APP_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = Path(__file__).parent

# PROJECT_ROOT: where data/ directory lives
# Docker: /app/data (mounted), so PROJECT_ROOT = /app
# Local: ./data (sibling to app/), so PROJECT_ROOT = app/ parent
PROJECT_ROOT = APP_ROOT if str(APP_ROOT) == "/app" else APP_ROOT.parent

class ChromaClientType(str, Enum):
    """ChromaDB client type."""
    PERSISTENT = "persistent"
    HTTP = "http"
    CLOUD = "cloud"

class LLMProvider(str, Enum):
    """LLM provider type."""

    OPENAI = "openai"    # Any OpenAI-compatible API (Ollama, LM Studio, vLLM, OpenAI)
    BEDROCK = "bedrock"  # AWS Bedrock

class Settings(BaseSettings):
    '''Application settings'''

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8') #overwrites below
    
    # App
    app_name: str = "Sentio+ RAG API"
    app_description: str = "RAG chatbot for product review insights"
    version: str = "0.1.0"
    debug_mode: bool = False

    # LLM - Universal config
    llm_provider: LLMProvider = LLMProvider.BEDROCK
    llm_base_url: str = "" 
    llm_model: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    llm_api_key: str = ""  # Local models don't need this
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1000

    # AWS (only for Bedrock)
    aws_region: str = "us-west-2"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    
    # ChromaDB
    chroma_client_type: ChromaClientType = ChromaClientType.PERSISTENT
    chroma_persist_path: Path = Path("./chroma_data")  # For persistent client
    chroma_host: str = "localhost"              # For HTTP client
    chroma_port: int = 8000                     # For HTTP client
    chroma_tenant_id: str | None = None
    chroma_database: str | None = None
    chroma_cloud_api_key: str | None = None
    chroma_collection_name: str = "sentio_reviews"
    
    # Retrieval
    retrieval_top_k: int = 5
    retrieval_threshold: float = 1.2

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 100

    # Ingestion
    ingest_limit: int | None = 1000  # None = no limit

    # Logging
    log_level: str = "INFO"
    log_to_file: bool = True

    # Directories
    data_dir: Path = PROJECT_ROOT / "data"
    log_dir: Path = PROJECT_ROOT / "logs"
    logging_config_file: Path = CONFIG_DIR / "logging_conf.json"

    @property
    def raw_data_dir(self) -> Path:
        """Path to raw data directory."""
        return self.data_dir / "raw"

    @property
    def processed_data_dir(self) -> Path:
        """Path to processed data directory."""
        return self.data_dir / "processed"

    @property
    def cache_dir(self) -> Path:
        """Path to cache directory."""
        return self.data_dir / "cache"
    
@lru_cache
def get_settings() -> Settings:
    '''Get cached settings instance'''
    return Settings()