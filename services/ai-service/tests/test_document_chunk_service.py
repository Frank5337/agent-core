from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.models.knowledge_base import KnowledgeBaseModel
from app.schemas.document import DocumentParseRequest, DocumentStatusUpdate
from app.schemas.chunk import ChunkCreate
from app.schemas.document import DocumentCreate
from app.services.chunk_service import chunk_service
from app.services.document_service import document_service


def build_session() -> Session:
    # 每个测试都用独立内存库，保证状态隔离。
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = session_factory()
    knowledge_base = KnowledgeBaseModel(
        name="team-handbook",
        description="knowledge",
        embedding_provider_id=None,
    )
    session.add(knowledge_base)
    session.commit()
    session.refresh(knowledge_base)
    session.info["knowledge_base_id"] = knowledge_base.id
    return session


def test_create_document_increments_knowledge_base_count() -> None:
    session = build_session()

    document = document_service.create_document(
        session,
        session.info["knowledge_base_id"],
        DocumentCreate(
            name="oncall-runbook",
            source_type="text",
            mime_type="text/plain",
            status="draft",
            content="runbook content",
        ),
    )

    knowledge_base = session.get(KnowledgeBaseModel, session.info["knowledge_base_id"])

    assert document.name == "oncall-runbook"
    assert document.chunk_count == 0
    assert knowledge_base is not None
    assert knowledge_base.document_count == 1


def test_create_chunk_increments_document_count_and_rejects_duplicate_index() -> None:
    session = build_session()
    document = document_service.create_document(
        session,
        session.info["knowledge_base_id"],
        DocumentCreate(
            name="oncall-runbook",
            source_type="text",
            mime_type="text/plain",
            status="draft",
            content="runbook content",
        ),
    )

    chunk = chunk_service.create_chunk(
        session,
        session.info["knowledge_base_id"],
        str(document.id),
        ChunkCreate(chunk_index=0, content="chunk-0", token_count=12),
    )

    stored_document = document_service.get_document_model(
        session, session.info["knowledge_base_id"], str(document.id)
    )

    assert chunk.chunk_index == 0
    assert stored_document is not None
    assert stored_document.chunk_count == 1

    try:
        chunk_service.create_chunk(
            session,
            session.info["knowledge_base_id"],
            str(document.id),
            ChunkCreate(chunk_index=0, content="chunk-0-dup", token_count=13),
        )
    except ValueError as exc:
        assert str(exc) == "chunk_index already exists for this document"
    else:
        raise AssertionError("expected duplicate chunk index error")


def test_parse_document_generates_chunks_and_updates_status() -> None:
    session = build_session()
    document = document_service.create_document(
        session,
        session.info["knowledge_base_id"],
        DocumentCreate(
            name="incident-postmortem",
            source_type="text",
            mime_type="text/plain",
            status="draft",
            content="abcdefghij" * 120,
        ),
    )

    parsed = document_service.parse_document(
        session,
        session.info["knowledge_base_id"],
        str(document.id),
        DocumentParseRequest(chunk_size=100, chunk_overlap=20, target_status="parsed"),
    )

    # 这里只验证切块和状态流转，不绑定具体的切块实现细节。
    chunks = chunk_service.list_chunks(session, session.info["knowledge_base_id"], str(document.id))

    assert parsed.status == "parsed"
    assert parsed.chunk_count > 1
    assert len(chunks) == parsed.chunk_count


def test_update_document_status_changes_status() -> None:
    session = build_session()
    document = document_service.create_document(
        session,
        session.info["knowledge_base_id"],
        DocumentCreate(
            name="incident-postmortem",
            source_type="text",
            mime_type="text/plain",
            status="draft",
            content="abc",
        ),
    )

    updated = document_service.update_status(
        session,
        session.info["knowledge_base_id"],
        str(document.id),
        DocumentStatusUpdate(status="indexed").status,
    )

    assert updated.status == "indexed"
