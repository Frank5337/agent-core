from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse
from app.services.chat_service import chat_service


router = APIRouter()


# 对话路由先保持极简，专注承接平台侧转发来的补全请求。
@router.post("/completions", response_model=ChatCompletionResponse)
def create_chat_completion(
    payload: ChatCompletionRequest,
    db: Session = Depends(get_db),
) -> ChatCompletionResponse:
    try:
        return chat_service.complete(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
