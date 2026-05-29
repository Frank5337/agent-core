from fastapi import APIRouter

from app.core.config import settings
from app.services.embedding_service import embedding_service


router = APIRouter()


@router.get("/rag-status")
def rag_status() -> dict[str, object]:
    generation_provider = (
        "deepseek" if "deepseek.com" in settings.resolved_generation_base_url.lower() else "openai-compatible"
    )
    embedding_provider = (
        "local-hash"
        if not embedding_service.supports_remote_embeddings()
        else (
            "openai-compatible"
            if "deepseek.com" not in settings.resolved_embedding_base_url.lower()
            else "deepseek"
        )
    )
    llm_mode = generation_provider if settings.generation_enabled else "template-fallback"
    embedding_mode = "openai" if embedding_service.supports_remote_embeddings() else "local-hash"
    return {
        "provider": generation_provider if settings.generation_enabled else "local",
        "generation_provider": generation_provider if settings.generation_enabled else "local",
        "embedding_provider": embedding_provider,
        "llm_mode": llm_mode,
        "embedding_mode": embedding_mode,
        "openai_enabled": settings.generation_enabled,
        "generation_enabled": settings.generation_enabled,
        "embedding_enabled": embedding_service.supports_remote_embeddings(),
        "embedding_model": settings.rag_embedding_model if embedding_service.supports_remote_embeddings() else "local-hash-v1",
        "generation_model": settings.rag_generation_model if settings.generation_enabled else "template-fallback",
    }
