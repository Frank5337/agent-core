from fastapi import APIRouter

from app.core.config import settings
from app.services.embedding_service import embedding_service


router = APIRouter()


@router.get("/rag-status")
def rag_status() -> dict[str, object]:
    provider = "deepseek" if "deepseek.com" in settings.openai_base_url.lower() else "openai-compatible"
    llm_mode = provider if settings.openai_enabled else "template-fallback"
    embedding_mode = "openai" if embedding_service.supports_remote_embeddings() else "local-hash"
    return {
        "provider": provider if settings.openai_enabled else "local",
        "llm_mode": llm_mode,
        "embedding_mode": embedding_mode,
        "openai_enabled": settings.openai_enabled,
        "embedding_model": settings.rag_embedding_model if embedding_service.supports_remote_embeddings() else "local-hash-v1",
        "generation_model": settings.rag_generation_model if settings.openai_enabled else "template-fallback",
    }
