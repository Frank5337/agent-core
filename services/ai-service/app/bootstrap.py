from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from app.db import Base, engine
from app.models import ProviderModel


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_chunk_embedding_columns()

    with Session(engine) as session:
        default_provider = session.scalar(select(ProviderModel).where(ProviderModel.is_default.is_(True)))
        if default_provider is None:
            session.add(
                ProviderModel(
                    name="mock-openai",
                    provider_type="openai",
                    model_name="gpt-4o-mini",
                    endpoint="https://api.openai.com/v1",
                    api_key_masked="sk-***",
                    is_default=True,
                )
            )
            session.commit()


def _ensure_chunk_embedding_columns() -> None:
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("chunks")}
    statements: list[str] = []

    if "embedding_json" not in columns:
        statements.append("ALTER TABLE chunks ADD COLUMN embedding_json TEXT NOT NULL DEFAULT ''")
    if "embedding_model" not in columns:
        statements.append("ALTER TABLE chunks ADD COLUMN embedding_model VARCHAR(100) NOT NULL DEFAULT ''")
    if "embedding_status" not in columns:
        statements.append("ALTER TABLE chunks ADD COLUMN embedding_status VARCHAR(32) NOT NULL DEFAULT 'pending'")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
