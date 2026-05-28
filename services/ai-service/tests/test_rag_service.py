from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.models.chunk import ChunkModel
from app.models.document import DocumentModel
from app.models.knowledge_base import KnowledgeBaseModel
from app.schemas.rag import RagAskRequest, WebsiteIngestRequest
from app.services.rag_service import rag_service
from app.services.website_service import WebsiteContent


def build_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = session_factory()

    knowledge_base = KnowledgeBaseModel(
        name="sample-site",
        description="sample kb",
        embedding_provider_id=None,
        document_count=2,
    )
    session.add(knowledge_base)
    session.commit()
    session.refresh(knowledge_base)

    guide_document = DocumentModel(
        knowledge_base_id=knowledge_base.id,
        name="Travel Guide",
        source_type="url",
        source_uri="https://example.com/guide",
        mime_type="text/html",
        status="parsed",
        content="This guide covers travel tips, packing notes, and route planning.",
        chunk_count=1,
    )
    food_document = DocumentModel(
        knowledge_base_id=knowledge_base.id,
        name="Food Notes",
        source_type="url",
        source_uri="https://example.com/food",
        mime_type="text/html",
        status="parsed",
        content="This page focuses on local food, coffee shops, and desserts.",
        chunk_count=1,
    )
    session.add(guide_document)
    session.add(food_document)
    session.commit()
    session.refresh(guide_document)
    session.refresh(food_document)

    session.add(
        ChunkModel(
            knowledge_base_id=knowledge_base.id,
            document_id=guide_document.id,
            chunk_index=0,
            content="This guide covers travel tips, packing notes, and route planning.",
            token_count=14,
        )
    )
    session.add(
        ChunkModel(
            knowledge_base_id=knowledge_base.id,
            document_id=food_document.id,
            chunk_index=0,
            content="This page focuses on local food, coffee shops, and desserts.",
            token_count=13,
        )
    )
    session.commit()
    session.info["knowledge_base_id"] = knowledge_base.id
    return session


def test_ask_returns_retrieved_context_answer() -> None:
    session = build_session()

    response = rag_service.ask(
        session,
        RagAskRequest(
            knowledge_base_id=session.info["knowledge_base_id"],
            question="Which page talks about coffee?",
            top_k=2,
        ),
    )

    assert len(response.citations) >= 1
    assert response.citations[0].document_name == "Food Notes"
    assert "retrieved" in response.answer.lower() or "相关" in response.answer


def test_ingest_website_rebuilds_knowledge_base(monkeypatch) -> None:
    session = build_session()

    monkeypatch.setattr(
        "app.services.rag_service.website_service.crawl",
        lambda url, max_pages, same_domain_only: [
            WebsiteContent(
                url="https://example.com/new",
                title="Fresh Page",
                text="Fresh content about onboarding and release workflow. " * 10,
                links=[],
            )
        ],
    )

    response = rag_service.ingest_website(
        session,
        WebsiteIngestRequest(
            url="https://example.com/new",
            knowledge_base_name="sample-site",
            chunk_size=120,
            chunk_overlap=20,
            max_pages=1,
            same_domain_only=True,
        ),
    )

    documents = session.query(DocumentModel).all()
    chunks = session.query(ChunkModel).all()

    assert response.document_count == 1
    assert len(documents) == 1
    assert len(chunks) >= 1
    assert documents[0].name == "Fresh Page"
    assert all(chunk.embedding_status == "ready" for chunk in chunks)


def test_ingest_website_accepts_url_without_scheme(monkeypatch) -> None:
    session = build_session()

    captured: dict[str, str] = {}

    def fake_crawl(url, max_pages, same_domain_only):
        captured["url"] = url
        return [
            WebsiteContent(
                url="https://frank5337.github.io/",
                title="Franklin's World",
                text="Personal notes about shows and Java. " * 12,
                links=[],
            )
        ]

    monkeypatch.setattr("app.services.rag_service.website_service.crawl", fake_crawl)

    response = rag_service.ingest_website(
        session,
        WebsiteIngestRequest(
            url="frank5337.github.io",
            knowledge_base_name=None,
            chunk_size=120,
            chunk_overlap=20,
            max_pages=1,
            same_domain_only=True,
        ),
    )

    assert captured["url"] == "https://frank5337.github.io/"
    assert response.knowledge_base_name == "frank5337.github.io"
