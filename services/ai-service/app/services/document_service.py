from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import ChunkModel
from app.models.document import DocumentModel
from app.models.knowledge_base import KnowledgeBaseModel
from app.schemas.document import DocumentCreate, DocumentParseRequest, DocumentRead


class DocumentService:
    def list_documents(self, db: Session, knowledge_base_id: str) -> list[DocumentRead]:
        documents = db.scalars(
            select(DocumentModel)
            .where(DocumentModel.knowledge_base_id == knowledge_base_id)
            .order_by(DocumentModel.created_at.desc())
        ).all()
        return [DocumentRead.model_validate(item) for item in documents]

    def get_document(self, db: Session, knowledge_base_id: str, document_id: str) -> DocumentRead | None:
        document = db.scalar(
            select(DocumentModel).where(
                DocumentModel.knowledge_base_id == knowledge_base_id,
                DocumentModel.id == document_id,
            )
        )
        return None if document is None else DocumentRead.model_validate(document)

    def get_document_or_raise(self, db: Session, knowledge_base_id: str, document_id: str) -> DocumentModel:
        document = self.get_document_model(db, knowledge_base_id, document_id)
        if document is None:
            raise ValueError("document not found")
        return document

    def create_document(self, db: Session, knowledge_base_id: str, payload: DocumentCreate) -> DocumentRead:
        knowledge_base = db.get(KnowledgeBaseModel, knowledge_base_id)
        if knowledge_base is None:
            raise ValueError("knowledge_base_id does not exist")

        document = DocumentModel(
            knowledge_base_id=knowledge_base_id,
            name=payload.name,
            source_type=payload.source_type,
            source_uri=payload.source_uri,
            mime_type=payload.mime_type,
            status=payload.status,
            content=payload.content,
        )
        db.add(document)
        # 文档数先在知识库维度做冗余统计，后面列表页不用每次现算。
        knowledge_base.document_count += 1
        db.commit()
        db.refresh(document)
        return DocumentRead.model_validate(document)

    def get_document_model(self, db: Session, knowledge_base_id: str, document_id: str) -> DocumentModel | None:
        return db.scalar(
            select(DocumentModel).where(
                DocumentModel.knowledge_base_id == knowledge_base_id,
                DocumentModel.id == document_id,
            )
        )

    def update_status(
        self,
        db: Session,
        knowledge_base_id: str,
        document_id: str,
        status: str,
    ) -> DocumentRead:
        document = self.get_document_or_raise(db, knowledge_base_id, document_id)
        document.status = status
        db.commit()
        db.refresh(document)
        return DocumentRead.model_validate(document)

    def parse_document(
        self,
        db: Session,
        knowledge_base_id: str,
        document_id: str,
        payload: DocumentParseRequest,
    ) -> DocumentRead:
        document = self.get_document_or_raise(db, knowledge_base_id, document_id)
        if not document.content.strip():
            raise ValueError("document content is empty")
        if payload.chunk_overlap >= payload.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        # 当前先做同步切块；后续接异步任务时，这段逻辑可以搬到 worker 里复用。
        existing_chunks = db.scalars(
            select(ChunkModel).where(ChunkModel.document_id == document_id)
        ).all()
        for chunk in existing_chunks:
            db.delete(chunk)

        chunks = self._split_content(document.content, payload.chunk_size, payload.chunk_overlap)
        for index, content in enumerate(chunks):
            db.add(
                ChunkModel(
                    knowledge_base_id=knowledge_base_id,
                    document_id=document_id,
                    chunk_index=index,
                    content=content,
                    token_count=max(1, len(content) // 4),
                )
            )

        document.chunk_count = len(chunks)
        document.status = payload.target_status
        db.commit()
        db.refresh(document)
        return DocumentRead.model_validate(document)

    def _split_content(self, content: str, chunk_size: int, chunk_overlap: int) -> list[str]:
        text = content.strip()
        if not text:
            return []

        step = chunk_size - chunk_overlap
        chunks: list[str] = []
        start = 0
        # 用固定窗口切片，先把数据结构跑通，后面再替换成更智能的分段策略。
        while start < len(text):
            end = min(len(text), start + chunk_size)
            chunks.append(text[start:end])
            if end == len(text):
                break
            start += step
        return chunks


document_service = DocumentService()
