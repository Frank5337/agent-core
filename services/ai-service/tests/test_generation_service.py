from app.schemas.rag import RagMessage
from app.services.generation_service import GenerationService
from app.services.retrieval_service import RetrievalResult


def build_context() -> list[RetrievalResult]:
    return [
        RetrievalResult(
            document_id="doc-1",
            document_name="Travel Guide",
            source_url="https://example.com/guide",
            chunk_id="chunk-1",
            chunk_index=0,
            snippet="travel tips and route planning",
            score=0.91,
            content="This guide covers travel tips, packing notes, and route planning.",
        )
    ]


def test_build_prompt_includes_recent_history() -> None:
    service = GenerationService()
    prompt = service._build_prompt(
        "它提到了什么路线规划建议？",
        build_context(),
        [
            RagMessage(role="user", content="先总结一下这个页面。"),
            RagMessage(role="assistant", content="这个页面主要讲旅行准备和路线规划。"),
        ],
    )

    assert "Conversation history" in prompt
    assert "User: 先总结一下这个页面。" in prompt
    assert "Assistant: 这个页面主要讲旅行准备和路线规划。" in prompt
    assert "User question: 它提到了什么路线规划建议？" in prompt


def test_build_prompt_without_history_marks_none() -> None:
    service = GenerationService()
    prompt = service._build_prompt("这个页面主要讲什么？", build_context(), [])

    assert "Conversation history: (none)" in prompt
