from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    code: str
    language: Literal["python", "javascript", "java", "c", "cpp"]

    @field_validator("code")
    @classmethod
    def validate_code_size(cls, value: str) -> str:
        line_count = len(value.splitlines())
        if line_count > 500:
            raise ValueError("Code must be 500 lines or fewer.")
        return value


class Finding(BaseModel):
    line: int | None = None
    severity: Literal["vulnerable", "clear"]
    label: str
    cwe: str | None = None
    confidence: float | None = None
    source: Literal["model", "bandit", "semgrep"]


class AnalyzeResponse(BaseModel):
    vulnerable: bool
    overall_confidence: float = Field(ge=0.0, le=1.0)
    findings: list[Finding]
    scan_id: str
