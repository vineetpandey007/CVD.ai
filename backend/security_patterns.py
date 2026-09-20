"""
backend/app/db.py — DuckDB engine + session setup via SQLAlchemy.

Key operational rule: DuckDB permits only one read-write connection to a
given database file at a time, enforced across OS processes. Run this
backend as a SINGLE process (uvicorn without --workers, or --workers 1).

SECTION 1 — App-level rate limiting (add to app/main.py)
Requires: pip install slowapi

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In routes: @limiter.limit("10/minute") above the route function.

SECTION 2 — Safe subprocess execution for Bandit/Semgrep
Rules: NEVER shell=True. NEVER build the command as a joined string —
always pass a list of argv tokens. NEVER derive a file path/filename from
user input — always generate it (tempfile does this safely). ALWAYS set a
timeout. ALWAYS clean up the temp file, including on failure/timeout.

import json, os, subprocess, tempfile

ALLOWED_LANGUAGES = {"python", "javascript", "java", "c", "cpp"}
LANGUAGE_SUFFIX = {"python": ".py", "javascript": ".js", "java": ".java",
                   "c": ".c", "cpp": ".cpp"}
SUBPROCESS_TIMEOUT_SECONDS = 15

def run_semgrep(code: str, language: str) -> dict:
    if language not in ALLOWED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
    suffix = LANGUAGE_SUFFIX[language]
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            ["semgrep", "--config", "p/ci", "--json", tmp_path],
            capture_output=True, text=True,
            timeout=SUBPROCESS_TIMEOUT_SECONDS, shell=False,
        )
        return json.loads(result.stdout or "{}")
    except subprocess.TimeoutExpired:
        return {"error": "analysis timed out"}
    except json.JSONDecodeError:
        return {"error": "analysis tool returned unexpected output"}
    finally:
        os.unlink(tmp_path)

SECTION 3 — SQL-injection-safe DB access
Rule: never build a query by formatting user input into a string. Use the
ORM (or bound parameters) so the driver handles escaping, not you.

# WRONG: query = f"SELECT * FROM scans WHERE id = '{scan_id}'"
# RIGHT:
from sqlalchemy import select
from app.models import Scan

async def get_scan(db, scan_id: str):
    stmt = select(Scan).where(Scan.id == scan_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
"""