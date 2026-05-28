from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ModelProviderCreate(BaseModel):
    # 这里描述一个可被平台引用的模型提供商配置。
    name: str = Field(min_length=2, max_length=100)
    provider_type: Literal["openai", "azure-openai", "claude", "qwen", "local", "custom"]
    model_name: str = Field(min_length=1, max_length=100)
    endpoint: str = Field(default="", max_length=255)
    api_key_masked: str = Field(default="", max_length=64)
    is_default: bool = False


class ModelProviderRead(ModelProviderCreate):
    # 读模型直接复用创建字段，补上持久化产生的标识和时间。
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
