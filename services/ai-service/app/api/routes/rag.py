from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.rag import RagAskRequest, RagAskResponse, WebsiteIngestRequest, WebsiteIngestResponse
from app.services.rag_service import rag_service


router = APIRouter()


# 输入网站地址后，抓取正文并自动入库到知识库和文档切片。
@router.post("/ingest-website", response_model=WebsiteIngestResponse)
def ingest_website(payload: WebsiteIngestRequest, db: Session = Depends(get_db)) -> WebsiteIngestResponse:
    try:
        return rag_service.ingest_website(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# 基于指定知识库做一个轻量检索式问答，不依赖外部大模型。
@router.post("/ask", response_model=RagAskResponse)
def ask(payload: RagAskRequest, db: Session = Depends(get_db)) -> RagAskResponse:
    try:
        return rag_service.ask(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
