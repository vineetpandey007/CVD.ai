from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase


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
