from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse
from app.services.chat_service import chat_service


router = APIRouter()


@router.post("/completions", response_model=ChatCompletionResponse)
def create_chat_completion(payload: ChatCompletionRequest) -> ChatCompletionResponse:
    try:
        return chat_service.complete(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

