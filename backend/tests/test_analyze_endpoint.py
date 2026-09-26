from pathlib import Path

from app import main
from app.routes import analyze as analyze_route
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
VULNERABLE_SQL = REPO_ROOT / "examples" / "vulnerable_samples" / "sql_injection.py"
SAFE_SQL = REPO_ROOT / "examples" / "safe_samples" / "sql_injection.py"


def test_analyze_sql_fixtures_use_static_findings_for_verdict(monkeypatch) -> None:
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
