"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    # Application
    app_name: str = "DocFlow RAG"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    # API
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    api_key_header: str = "X-API-Key"

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "docflow"
    postgres_password: str = "docflow"
    postgres_db: str = "docflow"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    @property
    def redis_url(self) -> str:
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # Milvus
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    milvus_collection: str = "docflow_child_chunks"

    # LLM
    llm_provider: str = "ollama"  # "ollama", "openai", "deepseek"
    llm_model: str = "qwen2.5:7b"
    llm_base_url: str = "http://localhost:11434"
    llm_api_key: str | None = None
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2048

    # Embedding
    embedding_model: str = "BAAI/bge-m3"
    embedding_device: str = "cpu"
    embedding_dim: int = 1024

    # Reranker
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_enabled: bool = True
    reranker_top_k: int = 5

    # Chunking
    child_chunk_size: int = 256
    child_chunk_overlap: int = 32
    parent_chunk_size: int = 1024
    parent_chunk_overlap: int = 64

    # Retrieval
    retrieval_top_k: int = 10
    dense_weight: float = 0.6
    sparse_weight: float = 0.4
    rrf_k: int = 60
    max_rewrite_count: int = 2
    relevance_threshold: float = 0.6

    # Cache
    cache_enabled: bool = True
    cache_ttl: int = 86400  # 24 hours
    cache_similarity_threshold: float = 0.92

    # Rate Limiting
    rate_limit_queries: int = 30  # per minute
    rate_limit_uploads: int = 10  # per minute


settings = Settings()
