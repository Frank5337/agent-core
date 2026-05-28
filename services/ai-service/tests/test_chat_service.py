from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.models.knowledge_base import KnowledgeBaseModel
from app.models.provider import ProviderModel
from app.schemas.chat import ChatCompletionRequest, ChatMessage
from app.services.chat_service import chat_service


def build_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = session_factory()
    provider = ProviderModel(
        name="default-provider",
        provider_type="openai",
        model_name="gpt-4o-mini",
        endpoint="https://example.com",
        api_key_masked="sk-***",
        is_default=True,
    )
    knowledge_base = KnowledgeBaseModel(
        name="team-handbook",
        description="knowledge",
        embedding_provider_id=None,
    )
    session.add(provider)
    session.add(knowledge_base)
    session.commit()
    session.refresh(provider)
    session.refresh(knowledge_base)
    session.info["provider_id"] = provider.id
    session.info["knowledge_base_id"] = knowledge_base.id
    return session


def test_complete_uses_default_provider_and_system_prompt() -> None:
    session = build_session()

    response = chat_service.complete(
        session,
        ChatCompletionRequest(
            provider_id=None,
            knowledge_base_id=UUID(session.info["knowledge_base_id"]),
            system_prompt="be concise",
            messages=[ChatMessage(role="user", content="hello")],
            metadata={},
        ),
    )

    assert response.provider == "default-provider"
    assert response.model == "gpt-4o-mini"
    assert "Received your message: hello" in response.reply
    assert "system_prompt=be concise" in response.reply


def test_complete_rejects_missing_knowledge_base() -> None:
    session = build_session()

    try:
        chat_service.complete(
            session,
            ChatCompletionRequest(
                provider_id=session.info["provider_id"],
                knowledge_base_id=UUID("00000000-0000-0000-0000-000000000001"),
                system_prompt="",
                messages=[ChatMessage(role="user", content="hello")],
                metadata={},
            ),
        )
    except ValueError as exc:
        assert str(exc) == "knowledge_base_id does not exist"
    else:
        raise AssertionError("expected knowledge_base_id error")

