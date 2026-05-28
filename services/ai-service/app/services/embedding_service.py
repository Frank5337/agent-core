import json
import math
import urllib.error
import urllib.request
from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.chunk import ChunkModel


class EmbeddingService:
    def active_model_name(self) -> str:
        if self.supports_remote_embeddings():
            return settings.rag_embedding_model
        return "local-hash-v1"

    def is_openai_enabled(self) -> bool:
        return settings.openai_enabled

    def supports_remote_embeddings(self) -> bool:
        return self.is_openai_enabled() and "deepseek.com" not in settings.openai_base_url.lower()

    def ensure_chunk_embeddings(
        self,
        db: Session,
        knowledge_base_id: str,
        document_id: str | None = None,
    ) -> None:
        expected_model = self.active_model_name()
        query = select(ChunkModel).where(ChunkModel.knowledge_base_id == knowledge_base_id)
        if document_id is not None:
            query = query.where(ChunkModel.document_id == document_id)

        chunks = db.scalars(query.order_by(ChunkModel.chunk_index.asc())).all()
        pending = [
            chunk
            for chunk in chunks
            if chunk.embedding_status != "ready"
            or not chunk.embedding_json
            or chunk.embedding_model != expected_model
        ]
        if not pending:
            return

        texts = [chunk.content for chunk in pending]
        embeddings = self.embed_texts(texts)
        for chunk, embedding in zip(pending, embeddings, strict=True):
            chunk.embedding_json = json.dumps(embedding)
            chunk.embedding_model = expected_model
            chunk.embedding_status = "ready"

        db.commit()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if self.supports_remote_embeddings():
            return self._embed_openai(texts)
        return [self._embed_local(text) for text in texts]

    def decode_embedding(self, chunk: ChunkModel) -> list[float]:
        if not chunk.embedding_json:
            return []
        try:
            return json.loads(chunk.embedding_json)
        except json.JSONDecodeError:
            return []

    def cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        numerator = sum(a * b for a, b in zip(left, right, strict=True))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    def _embed_openai(self, texts: list[str]) -> list[list[float]]:
        url = self._join_url(settings.openai_base_url, "/embeddings")
        request = urllib.request.Request(
            url,
            data=json.dumps(
                {
                    "model": settings.rag_embedding_model,
                    "input": texts,
                    "encoding_format": "float",
                }
            ).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {settings.resolved_openai_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ValueError(f"embedding request failed: HTTP {exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise ValueError("embedding request failed") from exc

        return [item["embedding"] for item in payload.get("data", [])]

    def _embed_local(self, text: str) -> list[float]:
        dimension = 256
        values = [0.0] * dimension
        tokens = self._tokenize(text)
        counts = Counter(tokens)
        if not counts:
            return values

        for token, count in counts.items():
            slot = hash(token) % dimension
            values[slot] += 1.0 + math.log(count)

        norm = math.sqrt(sum(value * value for value in values))
        if norm == 0:
            return values
        return [value / norm for value in values]

    def _tokenize(self, text: str) -> list[str]:
        import re

        lowered = text.lower()
        ascii_words = re.findall(r"[a-z0-9]+", lowered)
        chinese_parts = re.findall(r"[\u4e00-\u9fff]{2,}", lowered)
        return ascii_words + chinese_parts

    def _join_url(self, base: str, path: str) -> str:
        return base.rstrip("/") + path


embedding_service = EmbeddingService()
