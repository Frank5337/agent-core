from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Middle Platform API"
    app_version: str = "0.1.0"
    default_model_provider: str = "mock-openai"

    model_config = SettingsConfigDict(
        env_prefix="AIMP_",
        env_file=".env",
        extra="ignore",
    )


settings = Settings()

