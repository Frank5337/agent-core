from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    # 文档记录原始内容和来源信息，后续解析后再生成 chunk。
    name: str = Field(min_length=1, max_length=150)
    source_type: Literal["text", "file", "url", "manual"] = "text"
    source_uri: str = Field(default="", max_length=1000)
    mime_type: str = Field(default="", max_length=100)
    status: Literal["draft", "parsed", "indexed"] = "draft"
    content: str = Field(default="", max_length=200000)


class DocumentStatusUpdate(BaseModel):
    # 单独拆出状态变更请求，方便以后挂审批或异步任务状态机。
    status: Literal["draft", "parsed", "indexed"]


class DocumentParseRequest(BaseModel):
    # 解析请求先暴露最基础的切块参数，便于后面逐步演进策略。
    chunk_size: int = Field(default=500, ge=50, le=5000)
    chunk_overlap: int = Field(default=50, ge=0, le=1000)
    target_status: Literal["parsed", "indexed"] = "parsed"


class DocumentRead(DocumentCreate):
    # 读取文档时补齐知识库归属和 chunk 统计信息。
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    knowledge_base_id: UUID
    chunk_count: int
    created_at: datetime
    updated_at: datetime
