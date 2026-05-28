from fastapi import APIRouter, HTTPException

from app.schemas.application import ApplicationCreate, ApplicationRead
from app.services.application_service import application_service


router = APIRouter()


@router.get("", response_model=list[ApplicationRead])
def list_applications() -> list[ApplicationRead]:
    return application_service.list_applications()


@router.post("", response_model=ApplicationRead, status_code=201)
def create_application(payload: ApplicationCreate) -> ApplicationRead:
    try:
        return application_service.create_application(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

