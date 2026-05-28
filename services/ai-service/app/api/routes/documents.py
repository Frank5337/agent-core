from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.chunk import ChunkCreate, ChunkRead
from app.schemas.document import DocumentCreate, DocumentParseRequest, DocumentRead, DocumentStatusUpdate
from app.services.chunk_service import chunk_service
from app.services.document_service import document_service


router = APIRouter()


@router.get("/{knowledge_base_id}/documents", response_model=list[DocumentRead])
def list_documents(knowledge_base_id: UUID, db: Session = Depends(get_db)) -> list[DocumentRead]:
    return document_service.list_documents(db, str(knowledge_base_id))


@router.post("/{knowledge_base_id}/documents", response_model=DocumentRead, status_code=201)
def create_document(
    knowledge_base_id: UUID,
    payload: DocumentCreate,
    db: Session = Depends(get_db),
) -> DocumentRead:
    try:
        return document_service.create_document(db, str(knowledge_base_id), payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{knowledge_base_id}/documents/{document_id}", response_model=DocumentRead)
def get_document(knowledge_base_id: UUID, document_id: UUID, db: Session = Depends(get_db)) -> DocumentRead:
    document = document_service.get_document(db, str(knowledge_base_id), str(document_id))
    if document is None:
        raise HTTPException(status_code=404, detail="document not found")
    return document


@router.patch("/{knowledge_base_id}/documents/{document_id}/status", response_model=DocumentRead)
def update_document_status(
    knowledge_base_id: UUID,
    document_id: UUID,
    payload: DocumentStatusUpdate,
    db: Session = Depends(get_db),
) -> DocumentRead:
    try:
        return document_service.update_status(db, str(knowledge_base_id), str(document_id), payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{knowledge_base_id}/documents/{document_id}/parse", response_model=DocumentRead)
def parse_document(
    knowledge_base_id: UUID,
    document_id: UUID,
    payload: DocumentParseRequest,
    db: Session = Depends(get_db),
) -> DocumentRead:
    try:
        # 先保留一个显式解析入口，便于后面替换成任务触发或重试操作。
        return document_service.parse_document(db, str(knowledge_base_id), str(document_id), payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{knowledge_base_id}/documents/{document_id}/chunks", response_model=list[ChunkRead])
def list_chunks(knowledge_base_id: UUID, document_id: UUID, db: Session = Depends(get_db)) -> list[ChunkRead]:
    return chunk_service.list_chunks(db, str(knowledge_base_id), str(document_id))


@router.post("/{knowledge_base_id}/documents/{document_id}/chunks", response_model=ChunkRead, status_code=201)
def create_chunk(
    knowledge_base_id: UUID,
    document_id: UUID,
    payload: ChunkCreate,
    db: Session = Depends(get_db),
) -> ChunkRead:
    try:
        return chunk_service.create_chunk(db, str(knowledge_base_id), str(document_id), payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
