import re
from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import ChunkModel
from app.models.document import DocumentModel
from app.services.embedding_service import embedding_service


STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "for",
    "of",
    "in",
    "on",
    "with",
    "by",
    "is",
    "are",
    "this",
    "that",
    "what",
    "which",
    "how",
    "about",
    "website",
    "site",
    "page",
    "pages",
    "内容",
    "网站",
    "这个",
    "那个",
    "什么",
    "哪些",
    "怎么",
    "如何",
    "介绍",
    "总结",
    "概括",
    "主要",
}


class RetrievalResult:
    def __init__(
        self,
        *,
        document_id: str,
        document_name: str,
        source_url: str,
        chunk_id: str,
        chunk_index: int,
        snippet: str,
        score: float,
        content: str,
    ) -> None:
        self.document_id = document_id
        self.document_name = document_name
        self.source_url = source_url
        self.chunk_id = chunk_id
        self.chunk_index = chunk_index
        self.snippet = snippet
        self.score = score
        self.content = content


class RetrievalService:
    def search(self, db: Session, knowledge_base_id: str, query: str, top_k: int) -> list[RetrievalResult]:
        embedding_service.ensure_chunk_embeddings(db, knowledge_base_id)
        query_embedding = embedding_service.embed_query(query)
        query_tokens = self._dedupe_tokens(self._tokenize(query))

        rows = db.execute(
            select(ChunkModel, DocumentModel)
            .join(DocumentModel, DocumentModel.id == ChunkModel.document_id)
            .where(ChunkModel.knowledge_base_id == knowledge_base_id)
            .order_by(DocumentModel.created_at.asc(), ChunkModel.chunk_index.asc())
        ).all()

        ranked: list[RetrievalResult] = []
        for chunk, document in rows:
            chunk_embedding = embedding_service.decode_embedding(chunk)
            vector_score = embedding_service.cosine_similarity(query_embedding, chunk_embedding)
            lexical_score = self._lexical_score(query_tokens, document.name, chunk.content)
            title_score = self._title_score(query_tokens, document.name)
            final_score = vector_score * 0.8 + lexical_score * 0.15 + title_score * 0.05

            ranked.append(
                RetrievalResult(
                    document_id=document.id,
                    document_name=document.name,
                    source_url=document.source_uri,
                    chunk_id=chunk.id,
                    chunk_index=chunk.chunk_index,
                    snippet=self._best_snippet(chunk.content, query_tokens, 220),
                    score=round(final_score, 4),
                    content=chunk.content,
                )
            )

        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:top_k]

    def _tokenize(self, text: str) -> list[str]:
        lowered = text.lower()
        ascii_words = re.findall(r"[a-z0-9]+", lowered)
        chinese_parts = re.findall(r"[\u4e00-\u9fff]{2,}", lowered)
        tokens = ascii_words + chinese_parts
        return [token for token in tokens if token and token not in STOPWORDS]

    def _dedupe_tokens(self, tokens: list[str]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for token in tokens:
            if token in seen:
                continue
            seen.add(token)
            result.append(token)
        return result

    def _lexical_score(self, query_tokens: list[str], title: str, content: str) -> float:
        if not query_tokens:
            return 0.0
        text = f"{title}\n{content}".lower()
        score = 0.0
        for token in query_tokens:
            if token in text:
                score += self._token_weight(token)
        return score

    def _title_score(self, query_tokens: list[str], title: str) -> float:
        if not query_tokens:
            return 0.0
        title_lower = title.lower()
        score = 0.0
        for token in query_tokens:
            if token in title_lower:
                score += self._token_weight(token) * 1.1
        return score

    def _token_weight(self, token: str) -> float:
        if re.fullmatch(r"[a-z0-9]+", token):
            return min(len(token) / 3, 2.0)
        return min(len(token), 3.0)

    def _best_snippet(self, content: str, query_tokens: list[str], limit: int) -> str:
        compact = re.sub(r"\s+", " ", content).strip()
        if not compact:
            return ""

        sentences = re.split(r"(?<=[。！？.!?])\s+|\n+", compact)
        best = compact[:limit]
        best_score = -1.0

        for sentence in sentences:
            sentence_compact = sentence.strip()
            if not sentence_compact:
                continue
            score = self._lexical_score(query_tokens, "", sentence_compact)
            if score > best_score:
                best_score = score
                best = sentence_compact

        return best[:limit] + ("..." if len(best) > limit else "")


retrieval_service = RetrievalService()
