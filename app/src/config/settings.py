'''Application Configurations'''
from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings, SettingsConfigDict

class ChromaClientType(str, Enum):
    PERSISTENT = "persistent"
    HTTP = "http"

class Settings(BaseSettings):
    '''Application settings'''

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8') #overwrites below

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
    chroma_port: int = 8000                     # For HTTP client
    chroma_collection_name: str = "sentio_reviews"
    
    # Retrieval
    retrieval_top_k: int = 5
    retrieval_threshold: float = 1.2
    
    # App
    debug_mode: bool = False
    
@lru_cache
def get_settings() -> Settings:
    '''Get cached settings instance'''
    return Settings()