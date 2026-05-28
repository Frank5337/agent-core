from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str = Field(min_length=1, max_length=8000)


class ChatCompletionRequest(BaseModel):
    application_id: UUID | None = None
    provider_id: UUID | None = None
    messages: list[ChatMessage] = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatCompletionResponse(BaseModel):
    provider: str
    model: str
    reply: str
    usage: dict[str, int]

