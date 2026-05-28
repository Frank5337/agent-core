from app.core.config import settings
from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse
from app.services.application_service import application_service
from app.services.provider_service import provider_service


class ChatService:
    def complete(self, payload: ChatCompletionRequest) -> ChatCompletionResponse:
        provider = None

        if payload.provider_id is not None:
            provider = provider_service.get_provider(payload.provider_id)
            if provider is None:
                raise ValueError("provider_id does not exist")
        elif payload.application_id is not None:
            application = application_service.get_application(payload.application_id)
            if application is None:
                raise ValueError("application_id does not exist")
            if application.provider_id is not None:
                provider = provider_service.get_provider(application.provider_id)
        else:
            provider = provider_service.get_default_provider()

        if provider is None:
            provider_name = settings.default_model_provider
            model_name = "gpt-4o-mini"
        else:
            provider_name = provider.name
            model_name = provider.model_name

        user_message = payload.messages[-1].content
        reply = f"[MVP mock reply] 已接收你的问题：{user_message}"

        return ChatCompletionResponse(
            provider=provider_name,
            model=model_name,
            reply=reply,
            usage={
                "prompt_tokens": len(user_message) // 2 + 10,
                "completion_tokens": len(reply) // 2 + 10,
                "total_tokens": (len(user_message) + len(reply)) // 2 + 20,
            },
        )


chat_service = ChatService()

