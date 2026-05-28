from datetime import datetime, UTC
from uuid import UUID, uuid4

from app.schemas.application import ApplicationCreate, ApplicationRead
from app.services.provider_service import provider_service


class ApplicationService:
    def __init__(self) -> None:
        self._applications: list[ApplicationRead] = []

    def list_applications(self) -> list[ApplicationRead]:
        return self._applications

    def get_application(self, application_id: UUID) -> ApplicationRead | None:
        return next((item for item in self._applications if item.id == application_id), None)

    def create_application(self, payload: ApplicationCreate) -> ApplicationRead:
        if payload.provider_id is not None and provider_service.get_provider(payload.provider_id) is None:
            raise ValueError("provider_id does not exist")

        application = ApplicationRead(
            id=uuid4(),
            created_at=datetime.now(UTC),
            **payload.model_dump(),
        )
        self._applications.append(application)
        return application


application_service = ApplicationService()
