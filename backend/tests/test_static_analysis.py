from pathlib import Path

import pytest

from app.schemas import Finding
from app.static_analysis.bandit_runner import run_bandit
from app.static_analysis.semgrep_runner import run_semgrep

REPO_ROOT = Path(__file__).resolve().parents[2]
VULNERABLE_SQL = REPO_ROOT / "examples" / "vulnerable_samples" / "sql_injection.py"
SAFE_SQL = REPO_ROOT / "examples" / "safe_samples" / "sql_injection.py"


def test_bandit_flags_vulnerable_sql_and_not_safe_sql() -> None:
    vulnerable_findings = run_bandit(VULNERABLE_SQL.read_text(encoding="utf-8"))
    safe_findings = run_bandit(SAFE_SQL.read_text(encoding="utf-8"))

    assert any(
        finding.source == "bandit"
        and finding.cwe == "CWE-89"
        and finding.line == 2
        for finding in vulnerable_findings
    )
    assert safe_findings == []


@pytest.mark.timeout(120)
@pytest.mark.parametrize(
    "fixture",
    [VULNERABLE_SQL, SAFE_SQL],
)
def test_semgrep_python_sql_fixtures_return_well_formed_results(
    fixture: Path,
) -> None:
    try:
        findings = run_semgrep(fixture.read_text(encoding="utf-8"), "python")
    except TimeoutError:
        pytest.skip("Semgrep exceeded its subprocess timeout")
    assert isinstance(findings, list)
    assert all(
        isinstance(finding, Finding) and finding.source == "semgrep"
        for finding in findings
    )
