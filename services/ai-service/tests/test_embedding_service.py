from app.services.embedding_service import EmbeddingService


def test_supports_remote_embeddings_with_independent_embedding_config(monkeypatch) -> None:
    monkeypatch.setattr("app.services.embedding_service.settings.embedding_api_key", "embed-key")
    monkeypatch.setattr(
        "app.services.embedding_service.settings.embedding_base_url",
        "https://api.openai.com/v1",
    )
    monkeypatch.setattr("app.services.embedding_service.settings.openai_api_key", "")
    monkeypatch.setattr("app.services.embedding_service.settings.openai_base_url", "https://api.deepseek.com")

    service = EmbeddingService()

    assert service.supports_remote_embeddings() is True
    assert service.active_model_name() != "local-hash-v1"


def test_supports_remote_embeddings_disabled_for_deepseek_embedding_base(monkeypatch) -> None:
    monkeypatch.setattr("app.services.embedding_service.settings.embedding_api_key", "embed-key")
    monkeypatch.setattr(
        "app.services.embedding_service.settings.embedding_base_url",
        "https://api.deepseek.com",
    )

    service = EmbeddingService()

    assert service.supports_remote_embeddings() is False
