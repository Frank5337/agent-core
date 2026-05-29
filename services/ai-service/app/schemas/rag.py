from uuid import UUID

from pydantic import BaseModel, Field


class WebsiteIngestRequest(BaseModel):
    # 允许用户直接输入域名，协议统一在服务层自动补齐。
    url: str = Field(min_length=1, max_length=2048)
    knowledge_base_name: str | None = Field(default=None, max_length=100)
    chunk_size: int = Field(default=800, ge=100, le=5000)
    chunk_overlap: int = Field(default=100, ge=0, le=1000)
    max_pages: int = Field(default=5, ge=1, le=20)
    same_domain_only: bool = True


class WebsiteIngestedPage(BaseModel):
    document_id: UUID
    document_name: str
    source_url: str
    chunk_count: int


class WebsiteIngestResponse(BaseModel):
    knowledge_base_id: UUID
    knowledge_base_name: str
    document_count: int
    total_chunk_count: int
    pages: list[WebsiteIngestedPage]


class RagMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4000)


class RagAskRequest(BaseModel):
    knowledge_base_id: UUID
    question: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=3, ge=1, le=8)
    history: list[RagMessage] = Field(default_factory=list, max_length=20)


class RagCitation(BaseModel):
    document_id: UUID
    document_name: str
    source_url: str
    chunk_id: UUID
    chunk_index: int
    snippet: str
    score: float


class RagAskResponse(BaseModel):
    knowledge_base_id: UUID
    question: str
    answer: str
    citations: list[RagCitation]
