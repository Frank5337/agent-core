from datetime import datetime, UTC
from uuid import UUID, uuid4

from app.schemas.provider import ModelProviderCreate, ModelProviderRead


class ProviderService:
    def __init__(self) -> None:
        self._providers: list[ModelProviderRead] = [
            ModelProviderRead(
                id=uuid4(),
                name="mock-openai",
                provider_type="openai",
                model_name="gpt-4o-mini",
                endpoint="https://api.openai.com/v1",
                api_key_masked="sk-***",
                is_default=True,
                created_at=datetime.now(UTC),
            )
        ]

    def list_providers(self) -> list[ModelProviderRead]:
        return self._providers

    def create_provider(self, payload: ModelProviderCreate) -> ModelProviderRead:
        if payload.is_default:
            self._clear_default()

        provider = ModelProviderRead(
            id=uuid4(),
            created_at=datetime.now(UTC),
            **payload.model_dump(),
        )
        self._providers.append(provider)
        return provider

    def get_provider(self, provider_id: UUID) -> ModelProviderRead | None:
        return next((item for item in self._providers if item.id == provider_id), None)

    def get_default_provider(self) -> ModelProviderRead | None:
        return next((item for item in self._providers if item.is_default), None)

    def _clear_default(self) -> None:
        for provider in self._providers:
            provider.is_default = False


provider_service = ProviderService()

