from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.provider import ModelProviderCreate, ModelProviderRead
from app.services.provider_service import provider_service


router = APIRouter()


# provider 路由负责平台可引用的模型配置资源。
@router.get("", response_model=list[ModelProviderRead])
def list_providers(db: Session = Depends(get_db)) -> list[ModelProviderRead]:
    return provider_service.list_providers(db)


@router.get("/{provider_id}", response_model=ModelProviderRead)
def get_provider(provider_id: str, db: Session = Depends(get_db)) -> ModelProviderRead:
    try:
        return provider_service.get_provider_or_raise(db, provider_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=ModelProviderRead, status_code=201)
def create_provider(payload: ModelProviderCreate, db: Session = Depends(get_db)) -> ModelProviderRead:
    try:
        return provider_service.create_provider(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
