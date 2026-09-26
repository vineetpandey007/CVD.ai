from fastapi import APIRouter

from app import models

router = APIRouter()


@router.get("/api/history/cwe-breakdown")
async def history_cwe_breakdown() -> list[dict]:
    return models.cwe_breakdown()


@router.get("/api/history/timeline")
async def history_timeline() -> list[dict]:
    return models.scans_over_time()