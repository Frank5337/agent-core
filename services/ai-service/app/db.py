from collections.abc import Generator
from urllib.parse import parse_qs, urlsplit

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _sqlite_connect_args(database_url: str) -> dict[str, object]:
    if not database_url.startswith("sqlite"):
        return {}

    connect_args: dict[str, object] = {"check_same_thread": False}
    query = parse_qs(urlsplit(database_url).query)
    if query.get("uri", ["false"])[0].lower() == "true":
        connect_args["uri"] = True
    return connect_args


engine = create_engine(
    settings.database_url,
    future=True,
    connect_args=_sqlite_connect_args(settings.database_url),
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
