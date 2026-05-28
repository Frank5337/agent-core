from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ModelProviderCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    provider_type: Literal["openai", "azure-openai", "claude", "qwen", "local", "custom"]
    model_name: str = Field(min_length=1, max_length=100)
    endpoint: str = Field(default="", max_length=255)
    api_key_masked: str = Field(default="", max_length=64)
    is_default: bool = False


class ModelProviderRead(ModelProviderCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime

