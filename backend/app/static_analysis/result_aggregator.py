from collections.abc import Iterable

from ..schemas import Finding


def merge_findings(
    model_result: dict,
    *tool_findings: Iterable[Finding],
) -> list[Finding]:
    model_finding = Finding(
        line=None,
        severity="vulnerable" if model_result.get("vulnerable", False) else "clear",
        label="Model prediction",
        cwe=model_result.get("cwe"),
        confidence=model_result.get("confidence"),
        source="model",
    )
    return [model_finding, *(finding for findings in tool_findings for finding in findings)]