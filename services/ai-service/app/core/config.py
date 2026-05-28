import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Service API"
    app_version: str = "0.1.0"
    default_model_provider: str = "mock-openai"
    database_url: str = "sqlite:///./ai-service.db"

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    rag_embedding_model: str = "text-embedding-3-small"
    rag_generation_model: str = "gpt-4.1-mini"
    rag_retrieval_top_k: int = 4

    model_config = SettingsConfigDict(
        env_prefix="AIMP_",
        env_file=".env",
        extra="ignore",
    )

    @property
    def resolved_openai_api_key(self) -> str:
        return self.openai_api_key.strip() or os.getenv("OPENAI_API_KEY", "").strip()

    @property
    def openai_enabled(self) -> bool:
        return bool(self.resolved_openai_api_key)


settings = Settings()
