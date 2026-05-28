from fastapi import APIRouter

from app.api.routes import chat, documents, knowledge_bases, providers, rag, system


api_router = APIRouter(prefix="/api/v1")
# 按能力拆路由，后面继续扩工作流、RAG 或模型管理时边界会更清晰。
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
api_router.include_router(knowledge_bases.router, prefix="/knowledge-bases", tags=["knowledge-bases"])
api_router.include_router(documents.router, prefix="/knowledge-bases", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
