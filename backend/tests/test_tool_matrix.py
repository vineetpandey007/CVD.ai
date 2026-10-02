import json
import os
import time
from pathlib import Path

import pytest

from app.static_analysis.bandit_runner import run_bandit
from app.static_analysis.cppcheck_runner import run_cppcheck
from app.static_analysis.flawfinder_runner import run_flawfinder
from app.static_analysis.njsscan_runner import run_njsscan
from app.static_analysis.ruff_runner import run_ruff
from app.static_analysis.semgrep_runner import run_semgrep, run_semgrep_batch
from app.schemas import Finding

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = Path(__file__).with_name("tool_matrix_baseline.json")
BASELINE = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
TOOLS = ("bandit", "ruff", "semgrep", "flawfinder", "cppcheck", "njsscan")
RUNNERS = {
    "bandit": run_bandit,
    "ruff": run_ruff,
    "flawfinder": run_flawfinder,
    "cppcheck": run_cppcheck,
    "njsscan": run_njsscan,
}
LANGUAGE_BY_SUFFIX = {
    ".py": "python",
    ".js": "javascript",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
}
SUPPORTED_LANGUAGES = {
    "bandit": {"python"},
    "ruff": {"python"},
    "semgrep": set(LANGUAGE_BY_SUFFIX.values()),
    "flawfinder": {"c", "cpp"},
    "cppcheck": {"c", "cpp"},
    "njsscan": {"javascript"},
}
CASES = [record for record in BASELINE if record["found"] != "N/A"]
def _fixture_path(record: dict) -> Path:
    return REPO_ROOT / "examples" / record["fixture"]


def _record_result(
    tool: str,
    fixture: str,
    language: str,
    expected: bool,
    findings: int | str,
    cwes: list[str],
    elapsed: float,
    warning: str | None,
) -> dict:
    return {
        "tool": tool,
        "fixture": fixture,
        "language": language,
        "expected": expected,
        "found": findings,
        "found_cwes": cwes,
        "elapsed_seconds": round(elapsed, 3),
        "warning": warning,
    }


@pytest.fixture(scope="module")
def matrix_observations() -> dict[tuple[str, str], dict]:
    observations: dict[tuple[str, str], dict] = {}
    fixtures = {record["fixture"]: record for record in BASELINE}

    for language in LANGUAGE_BY_SUFFIX.values():
        group = [
            record
            for record in fixtures.values()
            if record["language"] == language
        ]
        if not group:
            continue
        code_by_name = {
            record["fixture"].replace("/", "_"): _fixture_path(record).read_text(
                encoding="utf-8"
            )
            for record in group
        }
        started = time.perf_counter()
        warning = None
        try:
            batch_findings = run_semgrep_batch(code_by_name, language)
        except TimeoutError as exc:
            batch_findings = {}
            warning = f"TimeoutError: {exc}"
        except Exception as exc:
            batch_findings = {}
            warning = f"{type(exc).__name__}: {exc}"
        elapsed = time.perf_counter() - started
        for record in group:
            key = record["fixture"].replace("/", "_")
            fixture_findings = batch_findings.get(key, [])
            observations[("semgrep", record["fixture"])] = _record_result(
                "semgrep",
                record["fixture"],
                language,
                record["expected"],
                len(fixture_findings)
                if warning is None
                else "TIMEOUT"
                if warning.startswith("TimeoutError")
                else "ERROR",
                sorted({finding.cwe for finding in fixture_findings if finding.cwe}),
                elapsed,
                warning,
            )

    for record in CASES:
        fixture = _fixture_path(record)
        code = fixture.read_text(encoding="utf-8")
        language = record["language"]
        for tool, runner in RUNNERS.items():
            if language not in SUPPORTED_LANGUAGES[tool]:
                continue
            started = time.perf_counter()
            warning = None
            try:
                findings = (
                    runner(code)
                    if tool == "bandit"
                    else runner(code, language)
                )
                count: int | str = len(findings)
                cwes = sorted({finding.cwe for finding in findings if finding.cwe})
            except TimeoutError as exc:
                count = "TIMEOUT"
                cwes = []
                warning = f"TimeoutError: {exc}"
            except Exception as exc:
                count = "ERROR"
                cwes = []
                warning = f"{type(exc).__name__}: {exc}"
            elapsed = time.perf_counter() - started
            observations[(tool, record["fixture"])] = _record_result(
                tool,
                record["fixture"],
                language,
                record["expected"],
                count,
                cwes,
                elapsed,
                warning,
            )
    return observations


def _case_parameter(record: dict):
    found = record["found"]
    if not record["expected"] and isinstance(found, int) and found > 0:
        mark = pytest.mark.xfail(
            strict=True,
            reason=f"Measured false positive: {record['tool']} on {record['fixture']}",
        )
    elif record["expected"] and record["expected_cwe"] not in record["found_cwes"]:
        mark = pytest.mark.xfail(
            strict=True,
            reason=f"Measured miss: {record['tool']} on {record['fixture']}",
        )
    else:
        mark = ()
    return pytest.param(
        record,
        id=f"{record['tool']}-{record['fixture']}",
        marks=mark,
    )


@pytest.mark.parametrize(
    "record",
    [
        _case_parameter(record)
        for record in CASES
    ],
)
def test_tool_matrix_asserts_measured_detection(
    record: dict,
    matrix_observations: dict[tuple[str, str], dict],
    record_property,
) -> None:
    observed = matrix_observations[(record["tool"], record["fixture"])]
    record_property("tool_matrix_record", json.dumps(observed, sort_keys=True))
    if observed["warning"]:
        pytest.skip(f"Runner warning: {observed['warning']}")
    assert observed["warning"] == record["warning"]
    if record["expected"]:
        assert record["expected_cwe"] in observed["found_cwes"]
    else:
        assert observed["found"] == 0


@pytest.mark.parametrize(
    "language",
    ("python", "javascript", "java", "c", "cpp"),
)
def test_2000_line_inputs_record_direct_runner_timings(
    language: str,
    record_property,
) -> None:
    suffix = next(
        suffix
        for suffix, mapped_language in LANGUAGE_BY_SUFFIX.items()
        if mapped_language == language
    )
    if language == "python":
        code = "\n".join(f"value_{line} = {line}" for line in range(2000))
    elif language == "javascript":
        code = "\n".join(f"const value_{line} = {line};" for line in range(2000))
    elif language == "java":
        code = (
            "class Generated {\n"
            + "\n".join(
                f"  int value_{line} = {line};" for line in range(1998)
            )
            + "\n}\n"
        )
    else:
        code = "\n".join(f"int value_{line} = {line};" for line in range(2000))
    assert len(code.splitlines()) == 2000
    tools = [tool for tool in TOOLS if language in SUPPORTED_LANGUAGES[tool]]

    for tool in tools:
        if tool == "semgrep":
            runner = lambda: run_semgrep_batch(
                {f"generated_{language}{suffix}": code}, language
            )
        else:
            runner = (
                (lambda: RUNNERS[tool](code))
                if tool == "bandit"
                else (lambda: RUNNERS[tool](code, language))
            )
        started = time.perf_counter()
        warning = None
        try:
            findings = runner()
            count: int | str = (
                sum(map(len, findings.values()))
                if tool == "semgrep"
                else len(findings)
            )
        except NotImplementedError as exc:
            count = "UNSUPPORTED"
            warning = str(exc)
        except TimeoutError as exc:
            count = "TIMEOUT"
            warning = str(exc)
        except Exception as exc:
            count = "ERROR"
            warning = f"{type(exc).__name__}: {exc}"
        elapsed = time.perf_counter() - started
        evidence = {
            "tool": tool,
            "language": language,
            "lines": 2000,
            "found": count,
            "elapsed_seconds": round(elapsed, 3),
            "warning": warning,
        }
        record_property(f"large_input_{language}_{tool}", json.dumps(evidence))
        print(f"LARGE INPUT {json.dumps(evidence, sort_keys=True)}")


@pytest.mark.parametrize(
    ("fixture", "language", "expected_cwe"),
    (
        ("78_javascript.js", "javascript", "CWE-78"),
        ("89_java.java", "java", "CWE-89"),
    ),
)
def test_semgrep_single_fixture_confirmed_findings(
    fixture: str,
    language: str,
    expected_cwe: str,
) -> None:
    code = (
        REPO_ROOT / "examples" / "vulnerable_samples" / fixture
    ).read_text(encoding="utf-8")
    findings = run_semgrep(code, language)
    assert any(finding.cwe == expected_cwe for finding in findings)


@pytest.mark.parametrize(
    "language",
    ("python", "javascript", "java", "c", "cpp"),
)
def test_analyze_api_fixture_pair_per_language(
    language: str,
    monkeypatch,
) -> None:
    from fastapi.testclient import TestClient

    from app import main
    from app.routes import analyze as analyze_route

    fixtures = {
        record["fixture"]: record
        for record in BASELINE
        if record["language"] == language
    }
    codes = {
        fixture: _fixture_path(record).read_text(encoding="utf-8")
        for fixture, record in fixtures.items()
    }
    detections = {
        fixture: {
            record["tool"]
            for record in BASELINE
            if record["fixture"] == fixture
            and isinstance(record["found"], int)
            and record["found"] > 0
        }
        for fixture in fixtures
    }
    fixture_by_code = {code: fixture for fixture, code in codes.items()}
    monkeypatch.setattr(main, "warm_model", lambda: None)
    monkeypatch.setattr(main, "run_semgrep", lambda code, language: [])
    monkeypatch.setattr(main.limiter, "enabled", False)
    monkeypatch.setattr(
        analyze_route,
        "predict",
        lambda code: {"vulnerable": False, "confidence": 0.0, "cwe": None},
    )

    def fake_runner(tool_source: str):
        def run(code: str, language: str | None = None) -> list[Finding]:
            fixture = fixture_by_code.get(code)
            if fixture and tool_source in detections[fixture]:
                return [
                    Finding(
                        line=1,
                        severity="vulnerable",
                        label=f"Measured fixture evidence from {tool_source}",
                        cwe=fixtures[fixture]["expected_cwe"],
                        confidence=None,
                        source=tool_source,
                    )
                ]
            return []

        return run

    for tool_source in ("bandit", "ruff", "semgrep", "flawfinder", "cppcheck", "njsscan"):
        monkeypatch.setattr(
            analyze_route,
            f"run_{tool_source}",
            fake_runner(tool_source),
        )

    with TestClient(main.app) as client:
        for fixture, code in codes.items():
            response = client.post(
                "/api/analyze",
                json={"code": code, "language": language},
            )
            expected_vulnerable = bool(detections[fixture])
            assert response.status_code == 200, fixture
            assert response.json()["vulnerable"] is expected_vulnerable, fixture
            assert response.json()["analysis_warnings"] == [], fixture


def test_missing_cppcheck_is_reported_without_failing_api(monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app import main
    from app.routes import analyze as analyze_route

    code = "int value = 1;"
    monkeypatch.setattr(main, "warm_model", lambda: None)
    monkeypatch.setattr(main, "run_semgrep", lambda code, language: [])
    monkeypatch.setattr(main.limiter, "enabled", False)
    monkeypatch.setattr(
        analyze_route,
        "predict",
        lambda code: {"vulnerable": False, "confidence": 0.0, "cwe": None},
    )
    monkeypatch.setattr(analyze_route, "run_flawfinder", lambda code, language: [])
    monkeypatch.setattr(analyze_route, "run_semgrep", lambda code, language: [])

    def missing_cppcheck(code: str, language: str) -> list[Finding]:
        raise FileNotFoundError("cppcheck not installed")

    monkeypatch.setattr(analyze_route, "run_cppcheck", missing_cppcheck)

    with TestClient(main.app) as client:
        response = client.post("/api/analyze", json={"code": code, "language": "c"})

    assert response.status_code == 200
    assert response.json()["analysis_warnings"] == ["cppcheck not installed"]


@pytest.mark.skipif(
    os.name != "nt",
    reason="njsscan's libsast semantic scanner limitation is Windows-specific",
)
def test_njsscan_windows_limitation_is_reported_by_api(monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app import main
    from app.routes import analyze as analyze_route

    monkeypatch.setattr(main, "warm_model", lambda: None)
    monkeypatch.setattr(main, "run_semgrep", lambda code, language: [])
    monkeypatch.setattr(main.limiter, "enabled", False)
    monkeypatch.setattr(
        analyze_route,
        "predict",
        lambda code: {"vulnerable": False, "confidence": 0.0, "cwe": None},
    )

    with TestClient(main.app) as client:
        response = client.post(
            "/api/analyze",
            json={"code": "function render(input) {}", "language": "javascript"},
        )

    assert response.status_code == 200
    assert response.json()["analysis_warnings"] == [
        "njsscan semantic analysis is unavailable on Windows because "
        "libsast disables its Semgrep engine."
    ]
