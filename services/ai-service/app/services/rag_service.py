from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import ChunkModel
from app.models.document import DocumentModel
from app.models.knowledge_base import KnowledgeBaseModel
from app.schemas.document import DocumentCreate, DocumentParseRequest
from app.schemas.knowledge_base import KnowledgeBaseCreate
from app.schemas.rag import (
    RagAskRequest,
    RagAskResponse,
    RagCitation,
    WebsiteIngestedPage,
    WebsiteIngestRequest,
    WebsiteIngestResponse,
)
from app.services.document_service import document_service
from app.services.embedding_service import embedding_service
from app.services.generation_service import generation_service
from app.services.knowledge_service import knowledge_service
from app.services.retrieval_service import retrieval_service
from app.services.website_service import WebsiteContent, website_service


class RagService:
    def ingest_website(self, db: Session, payload: WebsiteIngestRequest) -> WebsiteIngestResponse:
        normalized_url = website_service._normalize_url(payload.url)
        contents = website_service.crawl(
            normalized_url,
            max_pages=payload.max_pages,
            same_domain_only=payload.same_domain_only,
        )
        knowledge_base_name = payload.knowledge_base_name or self._default_knowledge_base_name(normalized_url)
        knowledge_base = self._get_or_create_knowledge_base(db, knowledge_base_name)
        self._reset_knowledge_base_documents(db, str(knowledge_base.id))

        pages: list[WebsiteIngestedPage] = []
        total_chunk_count = 0

        for content in contents:
            parsed_document = self._upsert_document(
                db=db,
                knowledge_base_id=str(knowledge_base.id),
                content=content,
                chunk_size=payload.chunk_size,
                chunk_overlap=payload.chunk_overlap,
            )
            embedding_service.ensure_chunk_embeddings(
                db,
                knowledge_base_id=str(knowledge_base.id),
                document_id=str(parsed_document.id),
            )

            pages.append(
                WebsiteIngestedPage(
                    document_id=parsed_document.id,
                    document_name=parsed_document.name,
                    source_url=content.url,
                    chunk_count=parsed_document.chunk_count,
                )
            )
            total_chunk_count += parsed_document.chunk_count

        return WebsiteIngestResponse(
            knowledge_base_id=knowledge_base.id,
            knowledge_base_name=knowledge_base.name,
            document_count=len(pages),
            total_chunk_count=total_chunk_count,
            pages=pages,
        )

    def ask(self, db: Session, payload: RagAskRequest) -> RagAskResponse:
        knowledge_base = knowledge_service.get_knowledge_base(db, str(payload.knowledge_base_id))
        if knowledge_base is None:
            raise ValueError("knowledge_base_id does not exist")

        results = retrieval_service.search(
            db=db,
            knowledge_base_id=str(payload.knowledge_base_id),
            query=payload.question,
            top_k=payload.top_k,
        )

        citations = [
            RagCitation(
                document_id=item.document_id,
                document_name=item.document_name,
                source_url=item.source_url,
                chunk_id=item.chunk_id,
                chunk_index=item.chunk_index,
                snippet=item.snippet,
                score=item.score,
            )
            for item in results
        ]

        answer = generation_service.answer_question(payload.question, results)

        return RagAskResponse(
            knowledge_base_id=payload.knowledge_base_id,
            question=payload.question,
            answer=answer,
            citations=citations,
        )

    def _reset_knowledge_base_documents(self, db: Session, knowledge_base_id: str) -> None:
        documents = db.scalars(
            select(DocumentModel).where(DocumentModel.knowledge_base_id == knowledge_base_id)
        ).all()
        for document in documents:
            chunks = db.scalars(select(ChunkModel).where(ChunkModel.document_id == document.id)).all()
            for chunk in chunks:
                db.delete(chunk)
            db.delete(document)

        knowledge_base = db.get(KnowledgeBaseModel, knowledge_base_id)
        if knowledge_base is not None:
            knowledge_base.document_count = 0

        db.commit()

    def _upsert_document(
        self,
        db: Session,
        knowledge_base_id: str,
        content: WebsiteContent,
        chunk_size: int,
        chunk_overlap: int,
    ):
        existing_document = db.scalar(
            select(DocumentModel).where(
                DocumentModel.knowledge_base_id == knowledge_base_id,
                DocumentModel.source_uri == content.url,
            )
        )

        if existing_document is None:
            document = document_service.create_document(
                db,
                knowledge_base_id,
                DocumentCreate(
                    name=content.title,
                    source_type="url",
                    source_uri=content.url,
                    mime_type="text/html",
                    status="draft",
                    content=content.text,
                ),
            )
            document_id = str(document.id)
        else:
            existing_document.name = content.title
            existing_document.mime_type = "text/html"
            existing_document.status = "draft"
            existing_document.content = content.text
            db.commit()
            db.refresh(existing_document)
            document_id = str(existing_document.id)

        return document_service.parse_document(
            db,
            knowledge_base_id,
            document_id,
            DocumentParseRequest(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                target_status="parsed",
            ),
        )

    def _get_or_create_knowledge_base(self, db: Session, name: str):
        existing = db.scalar(select(KnowledgeBaseModel).where(KnowledgeBaseModel.name == name))
        if existing is not None:
            return knowledge_service.get_knowledge_base(db, existing.id)

        return knowledge_service.create_knowledge_base(
            db,
            KnowledgeBaseCreate(name=name, description=f"Website knowledge base for {name}"),
        )

    def _default_knowledge_base_name(self, url: str) -> str:
        host = urlparse(url).netloc.replace("www.", "").strip()
        return (host or "website")[:100]


rag_service = RagService()
