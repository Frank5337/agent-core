from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.provider import ProviderModel
from app.schemas.provider import ModelProviderCreate, ModelProviderRead


class ProviderService:
    def list_providers(self, db: Session) -> list[ModelProviderRead]:
        providers = db.scalars(select(ProviderModel).order_by(ProviderModel.created_at.desc())).all()
        return [ModelProviderRead.model_validate(provider) for provider in providers]

    def create_provider(self, db: Session, payload: ModelProviderCreate) -> ModelProviderRead:
        # provider 名称先作为业务唯一键，方便平台侧用可读名称排查配置问题。
        existing = db.scalar(select(ProviderModel).where(ProviderModel.name == payload.name))
        if existing is not None:
            raise ValueError("provider name already exists")

        if payload.is_default:
            self._clear_default(db)

        provider = ProviderModel(
            **payload.model_dump(),
        )
        db.add(provider)
        db.commit()
        db.refresh(provider)
        return ModelProviderRead.model_validate(provider)

    def get_provider(self, db: Session, provider_id: str) -> ModelProviderRead | None:
        provider = db.get(ProviderModel, provider_id)
        return None if provider is None else ModelProviderRead.model_validate(provider)

    def get_provider_or_raise(self, db: Session, provider_id: str) -> ModelProviderRead:
        provider = self.get_provider(db, provider_id)
        if provider is None:
            raise ValueError("provider not found")
        return provider

    def get_provider_model(self, db: Session, provider_id: str) -> ProviderModel | None:
        return db.get(ProviderModel, provider_id)

    def get_default_provider(self, db: Session) -> ModelProviderRead | None:
        provider = db.scalar(select(ProviderModel).where(ProviderModel.is_default.is_(True)))
        return None if provider is None else ModelProviderRead.model_validate(provider)

    def _clear_default(self, db: Session) -> None:
        # 默认 provider 只保留一个，方便平台侧不传 provider_id 时有稳定兜底。
        providers = db.scalars(select(ProviderModel).where(ProviderModel.is_default.is_(True))).all()
        for provider in providers:
            provider.is_default = False
        db.flush()


provider_service = ProviderService()
