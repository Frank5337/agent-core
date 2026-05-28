from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.router import api_router
from app.bootstrap import init_db
from app.core.config import settings

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise AI service for model gateway, knowledge base, and chat.",
)
app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(INDEX_FILE)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
