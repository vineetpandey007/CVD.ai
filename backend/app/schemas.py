from typing import Literal

from pydantic import BaseModel, Field, field_validator

MAX_CODE_LINES = 10000
MAX_CODE_BYTES = 500000


class AnalyzeRequest(BaseModel):
    code: str
    language: Literal["python", "javascript", "java", "c", "cpp"]

    @field_validator("code")
    @classmethod
    def validate_code_size(cls, value: str) -> str:
        byte_count = len(value.encode("utf-8"))
        if byte_count > MAX_CODE_BYTES:
            raise ValueError(f"Code must be {MAX_CODE_BYTES} bytes or fewer.")
        line_count = len(value.splitlines())
        if line_count > MAX_CODE_LINES:
            raise ValueError(f"Code must be {MAX_CODE_LINES} lines or fewer.")
        return value


class Finding(BaseModel):
    line: int | None = None
    severity: Literal["vulnerable", "clear"]
    label: str
    cwe: str | None = None
    confidence: float | None = None
    source: Literal[
        "model",
        "bandit",
        "semgrep",
        "ruff",
        "flawfinder",
        "cppcheck",
        "njsscan",
    ]


class AnalyzeResponse(BaseModel):
    vulnerable: bool
    overall_confidence: float = Field(ge=0.0, le=1.0)
    findings: list[Finding]
    scan_id: str
    analysis_warnings: list[str] = Field(default_factory=list)
