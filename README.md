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

Then open `http://localhost:8000` to use the website RAG demo page, which now supports multi-page crawl and website Q&A.

Then start `platform-service`:

```bash
cd services/platform-service
mvn spring-boot:run
```

## Test Commands

```bash
cd services/ai-service
pytest
```

```bash
cd services/platform-service
mvn test
```
