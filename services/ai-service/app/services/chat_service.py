import re
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse
from app.services.knowledge_service import knowledge_service
from app.services.provider_service import provider_service
from app.services.retrieval_service import RetrievalResult


class ChatService:
    def complete(self, db: Session, payload: ChatCompletionRequest) -> ChatCompletionResponse:
        provider = None

        # 对话前先确认知识库存在，避免平台侧把错误上下文透传进来。
        if payload.knowledge_base_id is not None and not knowledge_service.exists(db, str(payload.knowledge_base_id)):
            raise ValueError("knowledge_base_id does not exist")

        if payload.provider_id is not None:
            provider = provider_service.get_provider(db, payload.provider_id)
            if provider is None:
                raise ValueError("provider_id does not exist")
        else:
            # 平台没有显式指定 provider 时，回落到当前默认 provider。
            provider = provider_service.get_default_provider(db)

        if provider is None:
            provider_name = settings.default_model_provider
            model_name = "gpt-4o-mini"
        else:
            provider_name = provider.name
            model_name = provider.model_name

        # 当前先保留一个可观察的 mock 回复，便于平台联调时确认上下文是否透传成功。
        user_message = payload.messages[-1].content
        prompt_hint = f" system_prompt={payload.system_prompt[:24]}" if payload.system_prompt else ""
        reply = f"[MVP mock reply]{prompt_hint} Received your message: {user_message}"

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

    def generate_rag_answer(self, question: str, contexts: list[RetrievalResult]) -> str:
        if not contexts:
            return "没有检索到可用于回答的问题上下文。你可以换个问法，或者先重新抓取网站内容。"

        top_contexts = contexts[:3]
        evidence_lines = self._extract_evidence_lines(question, top_contexts)
        related_pages = self._related_pages(top_contexts)
        lead = self._lead_answer(question, top_contexts[0], evidence_lines)

        answer_parts = [
            "下面的回答来自检索到的站内上下文，而不是直接回退到整站正文。",
            lead,
            f"最相关的页面有：{related_pages}。",
        ]

        if evidence_lines:
            answer_parts.append("结合这些上下文，可以先得到：")
            answer_parts.extend(f"{index + 1}. {line}" for index, line in enumerate(evidence_lines[:3]))
        else:
            answer_parts.append("已经检索到相关页面，但还没有从片段里抽出足够明确的结论。你可以把问题问得更具体一些。")

        answer_parts.append("如果你愿意，我可以继续基于这些页面做更具体的追问回答。")
        return "\n\n".join(answer_parts)

    def _lead_answer(self, question: str, top_context: RetrievalResult, evidence_lines: list[str]) -> str:
        top_page = self._clean_title(top_context.document_name)
        if "吗" in question or "是否" in question or "有没有" in question:
            return f"从检索结果看，答案是有，最直接的证据来自页面《{top_page}》。"
        if "什么" in question or "哪些" in question:
            return f"从检索结果看，最直接相关的页面是《{top_page}》，我先基于它和相邻页面来回答。"
        if evidence_lines:
            return f"我先基于页面《{top_page}》及其相邻检索结果来回答。"
        return f"我先基于页面《{top_page}》的检索结果来回答。"

    def _extract_evidence_lines(self, question: str, contexts: list[RetrievalResult]) -> list[str]:
        query_tokens = self._tokenize(question)
        ranked_lines: list[tuple[float, str]] = []

        for context in contexts:
            for sentence in re.split(r"(?<=[。！？.!?])\s+|\n+", context.content):
                line = re.sub(r"\s+", " ", sentence).strip()
                if len(line) < 10:
                    continue
                score = self._sentence_score(line, query_tokens)
                if score <= 0 and query_tokens:
                    continue
                ranked_lines.append((score + context.score, line))

        ranked_lines.sort(key=lambda item: item[0], reverse=True)

        results: list[str] = []
        for _, line in ranked_lines:
            if line not in results:
                results.append(line)
            if len(results) >= 3:
                break

        if results:
            return results

        fallback: list[str] = []
        for context in contexts:
            line = re.sub(r"\s+", " ", context.snippet).strip()
            if line and line not in fallback:
                fallback.append(line)
            if len(fallback) >= 3:
                break
        return fallback

    def _related_pages(self, contexts: list[RetrievalResult]) -> str:
        names: list[str] = []
        for context in contexts:
            name = self._clean_title(context.document_name)
            if name and name not in names:
                names.append(name)
        return "、".join(names[:4]) or "站点首页"

    def _clean_title(self, title: str) -> str:
        compact = re.sub(r"\s+", " ", title).strip()
        compact = re.sub(r"\s+\|\s+.*$", "", compact)
        return compact.strip(" -|")

    def _tokenize(self, text: str) -> list[str]:
        text_lower = text.lower()
        ascii_words = re.findall(r"[a-z0-9]+", text_lower)
        chinese_parts = re.findall(r"[\u4e00-\u9fff]{2,}", text_lower)
        tokens = ascii_words + chinese_parts
        return [token for token in tokens if token]

    def _sentence_score(self, sentence: str, query_tokens: list[str]) -> float:
        if not query_tokens:
            return 0.2
        sentence_lower = sentence.lower()
        hits = sum(1 for token in query_tokens if token in sentence_lower)
        return hits / max(len(query_tokens), 1)


chat_service = ChatService()
