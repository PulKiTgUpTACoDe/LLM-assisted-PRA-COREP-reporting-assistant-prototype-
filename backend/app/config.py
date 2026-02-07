from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Google AI (Gemini)
    google_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "text-embedding-004"
    temperature: float = 0.1
    max_output_tokens: int = 8192
    
    # Vector Database
    chroma_persist_dir: str = "../data/chroma_db"
    collection_name: str = "pra_corep_knowledge"
    
    # Retrieval Configuration
    top_k_results: int = 10
    relevance_threshold: float = 0.65
    chunk_size: int = 800
    chunk_overlap: int = 100
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    
    # LangSmith Tracing (Optional)
    langsmith_tracing: str = "false"
    langsmith_api_key: str = ""
    langsmith_project: str = "corep-assistant"
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
