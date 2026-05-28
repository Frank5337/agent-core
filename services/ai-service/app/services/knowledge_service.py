from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_base import KnowledgeBaseModel
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseRead
from app.services.provider_service import provider_service


class KnowledgeService:
    def list_knowledge_bases(self, db: Session) -> list[KnowledgeBaseRead]:
        knowledge_bases = db.scalars(select(KnowledgeBaseModel).order_by(KnowledgeBaseModel.created_at.desc())).all()
        return [KnowledgeBaseRead.model_validate(item) for item in knowledge_bases]

    def get_knowledge_base(self, db: Session, knowledge_base_id: str) -> KnowledgeBaseRead | None:
        knowledge_base = db.get(KnowledgeBaseModel, knowledge_base_id)
        return None if knowledge_base is None else KnowledgeBaseRead.model_validate(knowledge_base)

    def create_knowledge_base(self, db: Session, payload: KnowledgeBaseCreate) -> KnowledgeBaseRead:
        # 先在服务层挡住重名，后面即使接数据库唯一索引，错误语义也更稳定。
        existing = db.scalar(select(KnowledgeBaseModel).where(KnowledgeBaseModel.name == payload.name))
        if existing is not None:
            raise ValueError("knowledge base name already exists")

        if (
            payload.embedding_provider_id is not None
            and provider_service.get_provider_model(db, str(payload.embedding_provider_id)) is None
        ):
            raise ValueError("embedding_provider_id does not exist")

        # embedding_provider_id 统一转成字符串存储，方便和其他服务用 UUID 文本互通。
        knowledge_base = KnowledgeBaseModel(
            name=payload.name,
            description=payload.description,
            embedding_provider_id=(
                None if payload.embedding_provider_id is None else str(payload.embedding_provider_id)
            ),
        )
        db.add(knowledge_base)
        db.commit()
        db.refresh(knowledge_base)
        return KnowledgeBaseRead.model_validate(knowledge_base)

    def exists(self, db: Session, knowledge_base_id: str) -> bool:
        return db.get(KnowledgeBaseModel, knowledge_base_id) is not None


knowledge_service = KnowledgeService()
