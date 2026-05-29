import json
import urllib.error
import urllib.request

from app.core.config import settings
from app.schemas.rag import RagMessage
from app.services.chat_service import chat_service
from app.services.retrieval_service import RetrievalResult


class GenerationService:
    def answer_question(
        self,
        question: str,
        contexts: list[RetrievalResult],
        history: list[RagMessage] | None = None,
    ) -> str:
        if not contexts:
            return "没有检索到可用于回答的上下文。你可以换个问法，或者先重新抓取网站内容。"

        messages = history or []
        if settings.generation_enabled:
            return self._answer_with_remote_model(question, contexts, messages)

        return chat_service.generate_rag_answer(question, contexts)

    def _answer_with_remote_model(
        self,
        question: str,
        contexts: list[RetrievalResult],
        history: list[RagMessage],
    ) -> str:
        if self._is_deepseek():
            return self._answer_with_chat_completions(question, contexts, history)
        return self._answer_with_responses(question, contexts, history)

    def _answer_with_responses(
        self,
        question: str,
        contexts: list[RetrievalResult],
        history: list[RagMessage],
    ) -> str:
        prompt = self._build_prompt(question, contexts, history)
        url = self._join_url(settings.resolved_generation_base_url, "/responses")
        request = urllib.request.Request(
            url,
            data=json.dumps(
                {
                    "model": settings.rag_generation_model,
                    "input": prompt,
                    "text": {"format": {"type": "text"}},
                }
            ).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )

        payload = self._send_request(request, "generation request failed")
        text = self._extract_responses_output_text(payload)
        if text:
            return text

        return chat_service.generate_rag_answer(question, contexts)

    def _answer_with_chat_completions(
        self,
        question: str,
        contexts: list[RetrievalResult],
        history: list[RagMessage],
    ) -> str:
        prompt = self._build_prompt(question, contexts, history)
        url = self._join_url(settings.resolved_generation_base_url, "/chat/completions")
        request = urllib.request.Request(
            url,
            data=json.dumps(
                {
                    "model": settings.rag_generation_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a retrieval-augmented answering assistant. "
                                "Answer only from the provided contexts. "
                                "If the contexts are insufficient, say what is missing. "
                                "Respond in concise Chinese and mention the supporting page titles."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    "temperature": 0.2,
                }
            ).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )

        payload = self._send_request(request, "generation request failed")
        text = self._extract_chat_completions_text(payload)
        if text:
            return text

        return chat_service.generate_rag_answer(question, contexts)

    def _build_prompt(
        self,
        question: str,
        contexts: list[RetrievalResult],
        history: list[RagMessage],
    ) -> str:
        context_blocks: list[str] = []
        for index, item in enumerate(contexts[: settings.rag_retrieval_top_k], start=1):
            context_blocks.append(
                "\n".join(
                    [
                        f"[Context {index}]",
                        f"Page: {item.document_name}",
                        f"URL: {item.source_url}",
                        f"Score: {item.score}",
                        f"Content: {item.content}",
                    ]
                )
            )

        history_blocks: list[str] = []
        for item in history[-settings.rag_history_messages :]:
            role = "User" if item.role == "user" else "Assistant"
            history_blocks.append(f"{role}: {item.content}")

        return "\n\n".join(
            [
                "Use the retrieved contexts below to answer the user question.",
                "If the previous conversation is relevant, keep the answer consistent with it.",
                "\n".join(history_blocks) if history_blocks else "Conversation history: (none)",
                "\n\n".join(context_blocks),
                f"User question: {question}",
            ]
        )

    def _send_request(self, request: urllib.request.Request, prefix: str) -> dict:
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ValueError(f"{prefix}: HTTP {exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise ValueError(prefix) from exc

    def _extract_responses_output_text(self, payload: dict) -> str:
        output = payload.get("output", [])
        texts: list[str] = []
        for item in output:
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    text = content.get("text", "").strip()
                    if text:
                        texts.append(text)
        return "\n".join(texts).strip()

    def _extract_chat_completions_text(self, payload: dict) -> str:
        choices = payload.get("choices", [])
        if not choices:
            return ""
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, str):
            return content.strip()
        return ""

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.resolved_generation_api_key}",
            "Content-Type": "application/json",
        }

    def _is_deepseek(self) -> bool:
        return "deepseek.com" in settings.resolved_generation_base_url.lower()

    def _join_url(self, base: str, path: str) -> str:
        return base.rstrip("/") + path


generation_service = GenerationService()
