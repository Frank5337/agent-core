from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=500)
    embedding_provider_id: UUID | None = None


class KnowledgeBaseRead(KnowledgeBaseCreate):
    id: UUID = Field(default_factory=uuid4)
    document_count: int = 0
    created_at: datetime

