from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=500)
    app_type: Literal["chatbot", "knowledge", "agent"] = "chatbot"
    system_prompt: str = Field(default="", max_length=4000)
    provider_id: UUID | None = None


class ApplicationRead(ApplicationCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime

