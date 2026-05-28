from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChunkCreate(BaseModel):
    chunk_index: int = Field(ge=0)
    content: str = Field(min_length=1, max_length=50000)
    token_count: int = Field(default=0, ge=0)


class ChunkRead(ChunkCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    knowledge_base_id: UUID
    document_id: UUID
    created_at: datetime

