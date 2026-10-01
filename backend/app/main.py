import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app import db
from app.static_analysis.semgrep_runner import run_semgrep

limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)

app = FastAPI(title="Code Vulnerability Detector")
app.state.limiter = limiter

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def warm_model() -> None:
    from app.inference.model_loader import get_model, get_tokenizer

    get_tokenizer()
    get_model()


@app.on_event("startup")
async def startup_event() -> None:
    db.init_db()
    try:
        warm_model()
    except Exception:
        logger.exception("Model warm-up failed; continuing startup")
    try:
        run_semgrep("value = 1\n", "python")
    except TimeoutError:
        logger.warning("Semgrep warm-up timed out; continuing startup")
    except Exception:
        logger.exception("Semgrep warm-up failed; continuing startup")


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred."})


from app.routes.analyze import router as analyze_router
from app.routes.health import router as health_router
from app.routes.history import router as history_router

app.include_router(health_router)
app.include_router(analyze_router)
app.include_router(history_router)

# TODO: mount future routers here when the analyze/history endpoints are implemented.
