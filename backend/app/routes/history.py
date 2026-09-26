from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.db import get_db

router = APIRouter()


@router.get("/api/history/cwe-breakdown")
async def history_cwe_breakdown(
    session: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    return models.cwe_breakdown(session)


@router.get("/api/history/timeline")
async def history_timeline(
    session: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    return models.scans_over_time(session)