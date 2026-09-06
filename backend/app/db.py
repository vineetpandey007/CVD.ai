"""DuckDB is intentionally used in single-process mode only.

This project deliberately avoids multiple uvicorn workers because DuckDB permits only one
active read/write connection to a database file at a time across OS processes. Running a
multi-worker backend would create lock contention and inconsistent writes even though the
app logic itself is small. This is a deliberate design choice for the current scale.
"""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine

from app.models import Base


def get_db_path() -> Path:
    configured = os.getenv("DUCKDB_PATH")
    if configured:
        target = Path(configured).expanduser()
    else:
        target = Path(__file__).resolve().parents[1] / "data" / "app.duckdb"

    if not target.is_absolute():
        target = (Path.cwd() / target).resolve()
    return target


def init_db() -> None:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(f"duckdb:///{db_path.as_posix()}", future=True)
    Base.metadata.create_all(bind=engine)
    engine.dispose()
