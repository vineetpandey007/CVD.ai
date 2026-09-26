import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

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


@router.post("/api/analyze", response_model=AnalyzeResponse)
@limiter.limit("10/minute")
async def analyze(
    request: Request,
    payload: AnalyzeRequest,
    session: Annotated[Session, Depends(get_db)],
) -> AnalyzeResponse:
    try:
        model_result = predict(payload.code)
    except Exception:
        logger.exception("Model prediction failed; continuing with static analysis")
        model_result = {"vulnerable": False, "confidence": 0.0, "cwe": None}

    bandit_findings: list[Finding] = []
    if payload.language == "python":
        try:
            bandit_findings = run_bandit(payload.code)
        except Exception:
            logger.exception("Bandit analysis failed; continuing without Bandit findings")

    semgrep_findings: list[Finding] = []
    try:
        semgrep_findings = run_semgrep(payload.code, payload.language)
    except Exception:
        logger.exception("Semgrep analysis failed; continuing without Semgrep findings")

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
    )