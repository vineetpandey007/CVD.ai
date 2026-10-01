import asyncio
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app import models
from app.db import get_db
from app.inference.bug_detector import predict
from app.main import limiter
from app.schemas import AnalyzeRequest, AnalyzeResponse, Finding
from app.static_analysis.bandit_runner import run_bandit
from app.static_analysis.result_aggregator import merge_findings
from app.static_analysis.semgrep_runner import run_semgrep

router = APIRouter()
logger = logging.getLogger(__name__)


async def _predict_safely(code: str) -> dict[str, Any]:
    try:
        return await run_in_threadpool(predict, code)
    except Exception:
        logger.exception("Model prediction failed; continuing with static analysis")
        return {"vulnerable": False, "confidence": 0.0, "cwe": None}


async def _run_bandit_safely(code: str) -> tuple[list[Finding], str | None]:
    try:
        return await run_in_threadpool(run_bandit, code), None
    except TimeoutError:
        logger.warning("Bandit analysis timed out")
        return [], "Bandit analysis timed out."
    except Exception:
        logger.exception("Bandit analysis failed; continuing without Bandit findings")
        return [], "Bandit analysis failed."


async def _run_semgrep_safely(
    code: str, language: str
) -> tuple[list[Finding], str | None]:
    try:
        return await run_in_threadpool(run_semgrep, code, language), None
    except TimeoutError:
        logger.warning("Semgrep analysis timed out")
        return [], "Semgrep analysis timed out."
    except Exception:
        logger.exception("Semgrep analysis failed; continuing without Semgrep findings")
        return [], "Semgrep analysis failed."


@router.post("/api/analyze", response_model=AnalyzeResponse)
@limiter.limit("10/minute")
async def analyze(
    request: Request,
    payload: AnalyzeRequest,
    session: Annotated[Session, Depends(get_db)],
) -> AnalyzeResponse:
    model_task = _predict_safely(payload.code)
    bandit_task = (
        _run_bandit_safely(payload.code)
        if payload.language == "python"
        else _empty_bandit_result()
    )
    semgrep_task = _run_semgrep_safely(payload.code, payload.language)
    model_result, (bandit_findings, bandit_warning), (
        semgrep_findings,
        semgrep_warning,
    ) = await asyncio.gather(
        model_task,
        bandit_task,
        semgrep_task,
    )
    analysis_warnings = [
        warning for warning in (bandit_warning, semgrep_warning) if warning
    ]

    findings = merge_findings(model_result, bandit_findings, semgrep_findings)
    static_findings = [finding for finding in findings if finding.source != "model"]
    vulnerable = bool(static_findings)
    overall_confidence = 0.99 if vulnerable else 0.0
    record = models.create_scan(
        session,
        payload.language,
        vulnerable,
        overall_confidence,
        findings,
    )
    return AnalyzeResponse(
        vulnerable=vulnerable,
        overall_confidence=overall_confidence,
        findings=findings,
        scan_id=record.id,
        analysis_warnings=analysis_warnings,
    )


async def _empty_bandit_result() -> tuple[list[Finding], None]:
    return [], None