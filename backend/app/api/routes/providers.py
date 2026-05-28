from fastapi import APIRouter, HTTPException

from app.schemas.provider import ModelProviderCreate, ModelProviderRead
from app.services.provider_service import provider_service


router = APIRouter()


@router.get("", response_model=list[ModelProviderRead])
def list_providers() -> list[ModelProviderRead]:
    return provider_service.list_providers()


@router.post("", response_model=ModelProviderRead, status_code=201)
def create_provider(payload: ModelProviderCreate) -> ModelProviderRead:
    try:
        return provider_service.create_provider(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

