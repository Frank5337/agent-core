from fastapi import APIRouter, HTTPException

from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseRead
from app.services.knowledge_service import knowledge_service


router = APIRouter()


@router.get("", response_model=list[KnowledgeBaseRead])
def list_knowledge_bases() -> list[KnowledgeBaseRead]:
    return knowledge_service.list_knowledge_bases()


@router.post("", response_model=KnowledgeBaseRead, status_code=201)
def create_knowledge_base(payload: KnowledgeBaseCreate) -> KnowledgeBaseRead:
    try:
        return knowledge_service.create_knowledge_base(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

