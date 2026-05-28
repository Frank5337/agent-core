from fastapi import APIRouter

from app.api.routes import applications, chat, knowledge_bases, providers


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(knowledge_bases.router, prefix="/knowledge-bases", tags=["knowledge-bases"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

