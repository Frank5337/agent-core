from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeBaseCreate(BaseModel):
    # 知识库先聚焦元数据，真正的内容明细通过 document/chunk 管理。
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=500)
    embedding_provider_id: UUID | None = None


class KnowledgeBaseRead(KnowledgeBaseCreate):
    # document_count 是一个冗余字段，列表页可以直接展示处理规模。
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_count: int = 0
    created_at: datetime
