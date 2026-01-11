'''Application Configurations'''
from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path(__file__).parent
PROJECT_ROOT = CONFIG_DIR.parent.parent

class ChromaClientType(str, Enum):
    """ChromaDB client type."""
    PERSISTENT = "persistent"
    HTTP = "http"

class Settings(BaseSettings):
    '''Application settings'''

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8') #overwrites below
    
    # App
    app_name: str = "Sentio+ RAG API"
    app_description: str = "RAG chatbot for product review insights"
    version: str = "0.1.0"
    debug_mode: bool = False

    # AWS
    aws_region: str = "us-west-2"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    
    # Bedrock
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # ChromaDB
    chroma_client_type: ChromaClientType = ChromaClientType.PERSISTENT
    chroma_persist_path: Path = Path("./chroma_data")  # For persistent client
    chroma_host: str = "localhost"              # For HTTP client
    chroma_port: int = 8001                     # For HTTP client
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