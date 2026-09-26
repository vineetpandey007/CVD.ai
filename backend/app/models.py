from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, Float, String, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ScanRecord(Base):
    __tablename__ = "scan_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    language: Mapped[str] = mapped_column(String, nullable=False)
    vulnerable: Mapped[bool] = mapped_column(nullable=False, default=False)
    overall_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class ScanFinding(Base):
    __tablename__ = "scan_findings"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    scan_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    cwe: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=False)


def _engine():
    from sqlalchemy import create_engine

    from app.db import get_db_path

    return create_engine(f"duckdb:///{get_db_path().as_posix()}", future=True)


def create_scan(
    language: str,
    vulnerable: bool,
    overall_confidence: float,
    findings: list[Any] | None = None,
) -> ScanRecord:
    record = ScanRecord(
        id=str(uuid4()),
        language=language,
        vulnerable=vulnerable,
        overall_confidence=overall_confidence,
        created_at=datetime.now(timezone.utc),
    )
    engine = _engine()
    try:
        with engine.begin() as connection:
            connection.execute(ScanRecord.__table__.insert().values(
                id=record.id,
                language=record.language,
                vulnerable=record.vulnerable,
                overall_confidence=record.overall_confidence,
                created_at=record.created_at,
            ))
            for finding in findings or []:
                cwe = finding.get("cwe") if isinstance(finding, dict) else finding.cwe
                if cwe:
                    connection.execute(ScanFinding.__table__.insert().values(
                        id=str(uuid4()),
                        scan_id=record.id,
                        cwe=cwe,
                        source=finding.get("source") if isinstance(finding, dict) else finding.source,
                    ))
    finally:
        engine.dispose()
    return record


def cwe_breakdown() -> list[dict[str, Any]]:
    engine = _engine()
    try:
        with engine.connect() as connection:
            rows = connection.execute(
                select(
                    ScanFinding.cwe,
                    ScanFinding.source,
                    func.count(ScanFinding.id).label("count"),
                ).group_by(ScanFinding.cwe, ScanFinding.source)
            ).all()
        return [
            {"cwe": row.cwe, "source": row.source, "count": row.count}
            for row in rows
        ]
    finally:
        engine.dispose()


def scans_over_time() -> list[dict[str, Any]]:
    engine = _engine()
    try:
        with engine.connect() as connection:
            rows = connection.execute(
                select(
                    ScanRecord.id,
                    ScanRecord.language,
                    ScanRecord.vulnerable,
                    ScanRecord.overall_confidence,
                    ScanRecord.created_at,
                ).order_by(ScanRecord.created_at)
            ).all()
        return [
            {
                "scan_id": row.id,
                "language": row.language,
                "vulnerable": row.vulnerable,
                "overall_confidence": row.overall_confidence,
                "created_at": row.created_at,
            }
            for row in rows
        ]
    finally:
        engine.dispose()
