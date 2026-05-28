from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import ChunkModel
from app.schemas.chunk import ChunkCreate, ChunkRead
from app.services.document_service import document_service


class ChunkService:
    def list_chunks(self, db: Session, knowledge_base_id: str, document_id: str) -> list[ChunkRead]:
        chunks = db.scalars(
            select(ChunkModel)
            .where(
                ChunkModel.knowledge_base_id == knowledge_base_id,
                ChunkModel.document_id == document_id,
            )
            .order_by(ChunkModel.chunk_index.asc())
        ).all()
        return [ChunkRead.model_validate(item) for item in chunks]

    def create_chunk(
        self,
        db: Session,
        knowledge_base_id: str,
        document_id: str,
        payload: ChunkCreate,
    ) -> ChunkRead:
        document = document_service.get_document_model(db, knowledge_base_id, document_id)
        if document is None:
            raise ValueError("document_id does not exist")

        existing = db.scalar(
            select(ChunkModel).where(
                ChunkModel.document_id == document_id,
                ChunkModel.chunk_index == payload.chunk_index,
            )
        )
        if existing is not None:
            raise ValueError("chunk_index already exists for this document")

        chunk = ChunkModel(
            knowledge_base_id=knowledge_base_id,
            document_id=document_id,
            chunk_index=payload.chunk_index,
            content=payload.content,
            token_count=payload.token_count,
        )
        db.add(chunk)
        # document 上保留 chunk_count，方便知识库侧快速展示处理进度。
        document.chunk_count += 1
        db.commit()
        db.refresh(chunk)
        return ChunkRead.model_validate(chunk)

    def get_chunk_count(self, db: Session, document_id: str) -> int:
        chunks = db.scalars(select(ChunkModel).where(ChunkModel.document_id == document_id)).all()
        return len(chunks)


chunk_service = ChunkService()
