from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.models.provider import ProviderModel
from app.schemas.provider import ModelProviderCreate
from app.services.provider_service import provider_service


def build_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = session_factory()
    session.add(
        ProviderModel(
            name="default-provider",
            provider_type="openai",
            model_name="gpt-4o-mini",
            endpoint="https://example.com",
            api_key_masked="sk-***",
            is_default=True,
        )
    )
    session.commit()
    return session


def test_create_provider_clears_previous_default() -> None:
    session = build_session()
    created = provider_service.create_provider(
        session,
        ModelProviderCreate(
            name="backup-provider",
            provider_type="openai",
            model_name="gpt-4.1-mini",
            endpoint="https://example.com/v2",
            api_key_masked="sk-***",
            is_default=True,
        ),
    )

    providers = provider_service.list_providers(session)

    assert created.is_default is True
    assert len(providers) == 2
    assert sum(1 for item in providers if item.is_default) == 1


def test_create_provider_rejects_duplicate_name() -> None:
    session = build_session()

    try:
        provider_service.create_provider(
            session,
            ModelProviderCreate(
                name="default-provider",
                provider_type="openai",
                model_name="gpt-4.1-mini",
                endpoint="https://example.com/v2",
                api_key_masked="sk-***",
                is_default=False,
            ),
        )
    except ValueError as exc:
        assert str(exc) == "provider name already exists"
    else:
        raise AssertionError("expected duplicate provider name error")

