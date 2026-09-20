from ..schemas import Finding


def merge_findings(
    model_result: dict,
    bandit_findings: list[Finding],
    semgrep_findings: list[Finding],
) -> list[Finding]:
    model_finding = Finding(
        line=None,
        severity="vulnerable" if model_result.get("vulnerable", False) else "clear",
        label="Model prediction",
        cwe=model_result.get("cwe"),
        confidence=model_result.get("confidence"),
        source="model",
    )
    return [model_finding, *bandit_findings, *semgrep_findings]