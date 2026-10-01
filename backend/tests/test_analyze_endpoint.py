from pathlib import Path

from fastapi.testclient import TestClient

from app import main
from app.routes import analyze as analyze_route

REPO_ROOT = Path(__file__).resolve().parents[2]
VULNERABLE_SQL = REPO_ROOT / "examples" / "vulnerable_samples" / "sql_injection.py"
SAFE_SQL = REPO_ROOT / "examples" / "safe_samples" / "sql_injection.py"


def test_analyze_sql_fixtures_use_static_findings_for_verdict(monkeypatch) -> None:
    monkeypatch.setattr(main, "warm_model", lambda: None)
    monkeypatch.setattr(main, "run_semgrep", lambda code, language: [])
    monkeypatch.setattr(analyze_route, "run_semgrep", lambda code, language: [])
    monkeypatch.setattr(
        analyze_route,
        "predict",
        lambda code: {
            "vulnerable": True,
            "confidence": 0.999,
            "cwe": None,
        },
    )

    with TestClient(main.app) as client:
        vulnerable_response = client.post(
            "/api/analyze",
            json={
                "code": VULNERABLE_SQL.read_text(encoding="utf-8"),
                "language": "python",
            },
        )
        safe_response = client.post(
            "/api/analyze",
            json={
                "code": SAFE_SQL.read_text(encoding="utf-8"),
                "language": "python",
            },
        )

    assert vulnerable_response.status_code == 200
    vulnerable = vulnerable_response.json()
    assert vulnerable["vulnerable"] is True
    assert any(
        finding["source"] == "bandit"
        and finding["cwe"] == "CWE-89"
        and finding["line"] == 2
        for finding in vulnerable["findings"]
    )

    assert safe_response.status_code == 200
    safe = safe_response.json()
    assert safe["vulnerable"] is False
    assert safe["overall_confidence"] == 0.0


def test_analyze_reports_static_analysis_timeouts_and_failures(monkeypatch) -> None:
    monkeypatch.setattr(main, "warm_model", lambda: None)
    monkeypatch.setattr(main, "run_semgrep", lambda code, language: [])
    monkeypatch.setattr(
        analyze_route,
        "predict",
        lambda code: {"vulnerable": False, "confidence": 0.5, "cwe": None},
    )

    def bandit_timeout(code: str):
        raise TimeoutError("Bandit timed out")

    def semgrep_failure(code: str, language: str):
        raise RuntimeError("Semgrep failed")

    monkeypatch.setattr(analyze_route, "run_bandit", bandit_timeout)
    monkeypatch.setattr(analyze_route, "run_semgrep", semgrep_failure)

    with TestClient(main.app) as client:
        response = client.post(
            "/api/analyze",
            json={"code": "print('hello')", "language": "python"},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["vulnerable"] is False
    assert result["analysis_warnings"] == [
        "Bandit analysis timed out.",
        "Semgrep analysis failed.",
    ]
