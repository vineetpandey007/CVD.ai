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
from app.static_analysis.cppcheck_runner import run_cppcheck
from app.static_analysis.flawfinder_runner import run_flawfinder
from app.static_analysis.njsscan_runner import run_njsscan
from app.static_analysis.result_aggregator import merge_findings
from app.static_analysis.ruff_runner import run_ruff
from app.static_analysis.semgrep_runner import run_semgrep

router = APIRouter()
logger = logging.getLogger(__name__)


async def _predict_safely(code: str) -> dict[str, Any]:
    try:
        return await run_in_threadpool(predict, code)
    except Exception:
        logger.exception("Model prediction failed; continuing with static analysis")
        return {"vulnerable": False, "confidence": 0.0, "cwe": None}


async def _run_tool_safely(
    source: str,
    display_name: str,
    runner: Any,
    code: str,
    language: str | None = None,
) -> tuple[list[Finding], str | None]:
    try:
        args = (code,) if language is None else (code, language)
        return await run_in_threadpool(runner, *args), None
    except TimeoutError:
        logger.warning("%s analysis timed out", display_name)
        return [], f"{display_name} analysis timed out."
    except FileNotFoundError:
        logger.warning("%s is not installed", display_name)
        warning = "cppcheck not installed" if source == "cppcheck" else f"{display_name} not installed."
        return [], warning
    except Exception:
        logger.exception("%s analysis failed; continuing without its findings", display_name)
        return [], f"{display_name} analysis failed."


@router.post("/api/analyze", response_model=AnalyzeResponse)
@limiter.limit("10/minute")
async def analyze(
    request: Request,
    payload: AnalyzeRequest,
    session: Annotated[Session, Depends(get_db)],
) -> AnalyzeResponse:
    tools: list[tuple[str, str, Any, str | None]] = []
    if payload.language == "python":
        tools.extend(
            [
                ("bandit", "Bandit", run_bandit, None),
                ("ruff", "Ruff", run_ruff, payload.language),
            ]
        )
    elif payload.language == "javascript":
        tools.append(("njsscan", "njsscan", run_njsscan, payload.language))
    elif payload.language in {"c", "cpp"}:
        tools.extend(
            [
                ("flawfinder", "Flawfinder", run_flawfinder, payload.language),
                ("cppcheck", "Cppcheck", run_cppcheck, payload.language),
            ]
        )
    tools.append(("semgrep", "Semgrep", run_semgrep, payload.language))

    model_result, *tool_results = await asyncio.gather(
        _predict_safely(payload.code),
        *(
            _run_tool_safely(source, display, runner, payload.code, language)
            for source, display, runner, language in tools
        ),
    )
    tool_findings = [findings for findings, _ in tool_results]
    analysis_warnings = [warning for _, warning in tool_results if warning]
    findings = merge_findings(model_result, *tool_findings)
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
