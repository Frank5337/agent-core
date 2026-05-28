# AI Service

`ai-service` is the Python service for AI capabilities:

- provider management
- knowledge base management
- chat completion

The service currently uses `FastAPI + SQLAlchemy + SQLite`.

## Prerequisites

- Python `3.13+`
- `pip`

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

After startup, open `http://localhost:8000` to use the website-to-RAG demo page.
The page supports:

- entering a website URL
- crawling multiple pages from the same domain
- ingesting page content into a knowledge base
- asking questions against the imported content

## Environment

The default local environment file is:

```bash
AIMP_DATABASE_URL=sqlite:///./ai-service.db
AIMP_OPENAI_API_KEY=
AIMP_OPENAI_BASE_URL=https://api.openai.com/v1
AIMP_RAG_EMBEDDING_MODEL=text-embedding-3-small
AIMP_RAG_GENERATION_MODEL=gpt-4.1-mini
```

If `AIMP_OPENAI_API_KEY` or `OPENAI_API_KEY` is set, website Q&A uses:

- vector retrieval via OpenAI embeddings
- answer generation via an OpenAI text model

If the key is not set, the service falls back to local hash embeddings and template-based generation so the demo still runs.

## Test

```bash
pytest
```

## API

- `GET /health`
- `GET /api/v1/providers`
- `POST /api/v1/providers`
- `GET /api/v1/knowledge-bases`
- `POST /api/v1/knowledge-bases`
- `GET /api/v1/knowledge-bases/{knowledgeBaseId}/documents`
- `POST /api/v1/knowledge-bases/{knowledgeBaseId}/documents`
- `GET /api/v1/knowledge-bases/{knowledgeBaseId}/documents/{documentId}`
- `PATCH /api/v1/knowledge-bases/{knowledgeBaseId}/documents/{documentId}/status`
- `POST /api/v1/knowledge-bases/{knowledgeBaseId}/documents/{documentId}/parse`
- `GET /api/v1/knowledge-bases/{knowledgeBaseId}/documents/{documentId}/chunks`
- `POST /api/v1/knowledge-bases/{knowledgeBaseId}/documents/{documentId}/chunks`
- `POST /api/v1/chat/completions`
- `GET /api/v1/system/rag-status`
- `POST /api/v1/rag/ingest-website`
- `POST /api/v1/rag/ask`
