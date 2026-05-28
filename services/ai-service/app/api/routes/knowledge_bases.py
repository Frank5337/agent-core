from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseRead
from app.services.knowledge_service import knowledge_service


router = APIRouter()


# 知识库列表是知识管理页的主入口。
@router.get("", response_model=list[KnowledgeBaseRead])
def list_knowledge_bases(db: Session = Depends(get_db)) -> list[KnowledgeBaseRead]:
    return knowledge_service.list_knowledge_bases(db)


# 详情接口给平台侧和管理台补全单个知识库元数据。
@router.get("/{knowledge_base_id}", response_model=KnowledgeBaseRead)
def get_knowledge_base(knowledge_base_id: str, db: Session = Depends(get_db)) -> KnowledgeBaseRead:
    knowledge_base = knowledge_service.get_knowledge_base(db, knowledge_base_id)
    if knowledge_base is None:
        raise HTTPException(status_code=404, detail="knowledge base not found")
    return knowledge_base


@router.post("", response_model=KnowledgeBaseRead, status_code=201)
def create_knowledge_base(
    payload: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
) -> KnowledgeBaseRead:
    try:
        return knowledge_service.create_knowledge_base(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
