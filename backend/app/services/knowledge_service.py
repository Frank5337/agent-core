from datetime import datetime, UTC
from uuid import uuid4

from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseRead
from app.services.provider_service import provider_service


class KnowledgeService:
    def __init__(self) -> None:
        self._knowledge_bases: list[KnowledgeBaseRead] = []

    def list_knowledge_bases(self) -> list[KnowledgeBaseRead]:
        return self._knowledge_bases

    def create_knowledge_base(self, payload: KnowledgeBaseCreate) -> KnowledgeBaseRead:
        if (
            payload.embedding_provider_id is not None
            and provider_service.get_provider(payload.embedding_provider_id) is None
        ):
            raise ValueError("embedding_provider_id does not exist")

        knowledge_base = KnowledgeBaseRead(
            id=uuid4(),
            created_at=datetime.now(UTC),
            document_count=0,
            **payload.model_dump(),
        )
        self._knowledge_bases.append(knowledge_base)
        return knowledge_base


knowledge_service = KnowledgeService()

