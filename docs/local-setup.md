# Local Setup

This repository contains two services:

- `services/ai-service`: Python AI service
- `services/platform-service`: Java platform service

Start `ai-service` first, then start `platform-service`.

## Prerequisites

### Shared

- Git
- A terminal with UTF-8 enabled

### ai-service

- Python `3.13+`
- `pip`
- Optional: `venv`

### platform-service

- Java `17`
- Maven `3.9+`

## Start ai-service

```bash
cd services/ai-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8002
```

Default local values:

- Base URL: `http://localhost:8002`
- Database: `sqlite:///./ai-service.db`
- Frontend demo: `http://localhost:8002`

Run tests:

```bash
pytest
```

## Start platform-service

Open a second terminal:

```bash
cd services/platform-service
mvn spring-boot:run
```

Default local values:

- Base URL: `http://localhost:8080`
- Database: in-memory `H2`
- Downstream AI service default: `http://localhost:8002`
- Web console: `http://localhost:8080`

Run tests:

```bash
mvn test
```

## Smoke Test Flow

1. Start `ai-service`.
2. Start `platform-service`.
3. Create a tenant in `platform-service`.
4. Create a platform user in `platform-service`.
5. Create a provider in `ai-service`.
6. Create a knowledge base in `ai-service`.
7. Create an application in `platform-service`.
8. Publish the application if you want to test release flow.
9. Call `POST /api/v1/applications/{applicationId}/chat`.

## Website RAG Demo

Open `http://localhost:8002` after starting `ai-service`.

1. Paste a website URL.
2. Optionally set the knowledge base name and max page count.
3. Click `抓取并入库`.
4. Wait for page crawl and chunk generation to finish.
5. Ask questions in the right-side panel.

## Troubleshooting

### `mvn` not found

Install Maven and ensure `mvn` is available in `PATH`.

### Python modules not found

Activate the virtual environment and reinstall:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### platform-service cannot call ai-service

Make sure `ai-service` is running on `8002` or update:

- [application.yml](/d:/Users/hzito02/IdeaProjects/codex/agent-core/services/platform-service/src/main/resources/application.yml:1)

### website crawl fails

Check these items first:

- Whether your local proxy is configured correctly
- Whether `ai-service` can access external websites
- Whether the target website blocks automated requests
