import pytest
from pydantic import ValidationError

from app.schemas import MAX_CODE_BYTES, MAX_CODE_LINES, AnalyzeRequest


def test_analyze_request_code_line_limit() -> None:
    max_lines = "\n".join(["code"] * MAX_CODE_LINES)
    over_limit = "\n".join(["code"] * (MAX_CODE_LINES + 1))

    AnalyzeRequest(code=max_lines, language="python")
    with pytest.raises(ValidationError, match=f"{MAX_CODE_LINES} lines or fewer"):
        AnalyzeRequest(code=over_limit, language="python")


def test_analyze_request_code_byte_limit() -> None:
    max_bytes = "x" * MAX_CODE_BYTES
    over_limit = "x" * (MAX_CODE_BYTES + 1)

    AnalyzeRequest(code=max_bytes, language="python")
    with pytest.raises(ValidationError, match=f"{MAX_CODE_BYTES} bytes or fewer"):
        AnalyzeRequest(code=over_limit, language="python")
