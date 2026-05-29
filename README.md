# AI Middle Platform

This repository contains a hybrid AI platform:

- `services/platform-service`: Java platform service
- `services/ai-service`: Python AI service

Current implementation:

- Java uses `Spring Boot + Spring Data JPA + H2`
- Python uses `FastAPI + SQLAlchemy + SQLite`
- `platform-service` calls `ai-service` over internal HTTP
- `ai-service` already includes `knowledge_bases`, `documents`, and `chunks` tables

## Docs

- Architecture: [docs/ai-middle-platform-mvp.md](/d:/Users/hzito02/IdeaProjects/codex/agent-core/docs/ai-middle-platform-mvp.md)
- Local setup: [docs/local-setup.md](/d:/Users/hzito02/IdeaProjects/codex/agent-core/docs/local-setup.md)
- Feature list: [docs/feature-list.md](/d:/Users/hzito02/IdeaProjects/codex/agent-core/docs/feature-list.md)
- Current status: [docs/current-status.md](/d:/Users/hzito02/IdeaProjects/codex/agent-core/docs/current-status.md)
- API overview: [docs/api-overview.md](/d:/Users/hzito02/IdeaProjects/codex/agent-core/docs/api-overview.md)
- Platform console guide: [docs/platform-console-guide.md](/d:/Users/hzito02/IdeaProjects/codex/agent-core/docs/platform-console-guide.md)

## Repository Layout

```text
docs/
services/
  ai-service/
  platform-service/
backend/  legacy directory kept temporarily
```

## Quick Start

Start `ai-service` first:

```bash
cd services/ai-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

For the current standalone website RAG demo, we recommend running `ai-service` on `8002` instead:

```bash
uvicorn app.main:app --reload --port 8002
```

Then open `http://localhost:8002` to use the website RAG demo page, which supports multi-page crawl, website Q&A, and multi-turn follow-up questions.

Then start `platform-service`:

```bash
cd services/platform-service
mvn spring-boot:run
```

After that, open `http://localhost:8080` to use the Java platform console.

## Test Commands

```bash
cd services/ai-service
pytest
```

```bash
cd services/platform-service
mvn test
```
