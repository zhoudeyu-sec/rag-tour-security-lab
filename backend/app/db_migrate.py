import logging

from sqlalchemy import inspect, text

from app.database import engine

logger = logging.getLogger(__name__)

_LOG_COLUMNS = [
    ("retrieved_poison", "BOOLEAN"),
    ("refused", "BOOLEAN"),
    ("case_id", "VARCHAR(64)"),
    ("source", "VARCHAR(32) DEFAULT 'chat'"),
]


def migrate_conversation_logs() -> None:
    insp = inspect(engine)
    if "conversation_logs" not in insp.get_table_names():
        return
    existing = {c["name"] for c in insp.get_columns("conversation_logs")}
    with engine.begin() as conn:
        for name, col_type in _LOG_COLUMNS:
            if name in existing:
                continue
            try:
                conn.execute(text(f"ALTER TABLE conversation_logs ADD COLUMN {name} {col_type}"))
                logger.info("Added column conversation_logs.%s", name)
            except Exception as exc:
                logger.warning("Migration skip %s: %s", name, exc)
