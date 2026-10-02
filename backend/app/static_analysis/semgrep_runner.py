import json
import os
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path

from ..schemas import Finding
from .cwe_lookup import get_cwe
from .subprocess_utils import run_command

SUBPROCESS_TIMEOUT_SECONDS = 62
SEMGREP_TIMEOUT_SECONDS = 10
ALLOWED_LANGUAGES = {"python", "javascript", "java", "c", "cpp"}
LANGUAGE_SUFFIX = {
    "python": ".py",
    "javascript": ".js",
    "java": ".java",
    "c": ".c",
    "cpp": ".cpp",
}
RULE_DIR = Path(__file__).resolve().parent / "rules"
RULE_CONFIGS = {
    "python": "python.yaml",
    "javascript": "javascript.yaml",
    "java": "java.yaml",
    "c": "c.yaml",
    "cpp": "cpp.yaml",
}


def _command(language: str, targets: Sequence[str]) -> tuple[list[str], dict[str, str]]:
    if language not in ALLOWED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
    env = os.environ.copy()
    env["SEMGREP_ENABLE_VERSION_CHECK"] = "0"
    env["PYTHONUTF8"] = "1"
    command = ["semgrep", "--metrics=off", "--disable-version-check"]
    command.extend(["--timeout", str(SEMGREP_TIMEOUT_SECONDS)])
    command.extend(["--config", str(RULE_DIR / RULE_CONFIGS[language])])
    command.extend(["--json", *targets])
    return command, env


def _parse_report(report: dict) -> list[Finding]:
    if report.get("errors"):
        raise RuntimeError("Semgrep reported analysis errors")
    findings: list[Finding] = []
    for result in report.get("results", []):
        extra = result.get("extra", {})
        metadata = extra.get("metadata", {})
        rule_id = result.get("check_id")
        findings.append(
            Finding(
                line=result.get("start", {}).get("line"),
                severity="vulnerable",
                label=extra.get("message") or rule_id or "Semgrep finding",
                cwe=get_cwe("semgrep", rule_id, metadata.get("cwe")),
                confidence=None,
                source="semgrep",
            )
        )
    return findings


def _run_targets(targets: Sequence[str], language: str) -> dict:
    command, env = _command(language, targets)
    completed = run_command(
        command,
        timeout=SUBPROCESS_TIMEOUT_SECONDS,
        env=env,
    )
    if not completed.stdout.strip():
        raise RuntimeError("Semgrep returned empty output")
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Semgrep returned invalid JSON") from exc
    return report


def run_semgrep(code: str, language: str) -> list[Finding]:
    suffix = LANGUAGE_SUFFIX.get(language)
    if suffix is None:
        raise ValueError(f"Unsupported language: {language}")
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, delete=False, encoding="utf-8"
    ) as temp_file:
        temp_file.write(code)
        temp_path = temp_file.name
    try:
        report = _run_targets([temp_path], language)
        return _parse_report(report)
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("Semgrep analysis timed out") from exc
    except UnicodeDecodeError as exc:
        raise RuntimeError("Semgrep output was not valid UTF-8") from exc
    finally:
        os.unlink(temp_path)


def run_semgrep_batch(
    code_by_name: Mapping[str, str], language: str
) -> dict[str, list[Finding]]:
    suffix = LANGUAGE_SUFFIX.get(language)
    if suffix is None:
        raise ValueError(f"Unsupported language: {language}")
    with tempfile.TemporaryDirectory(prefix="semgrep-matrix-") as directory:
        targets: dict[str, str] = {}
        for name, code in code_by_name.items():
            filename = f"{Path(name).stem}{suffix}"
            path = Path(directory) / filename
            path.write_text(code, encoding="utf-8")
            targets[filename] = str(path)
        try:
            report = _run_targets(list(targets.values()), language)
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError("Semgrep analysis timed out") from exc
        except UnicodeDecodeError as exc:
            raise RuntimeError("Semgrep output was not valid UTF-8") from exc

        results = {name: [] for name in targets}
        for result in report.get("results", []):
            path = Path(result.get("path", "")).name
            if path in results:
                results[path].extend(_parse_report({"results": [result]}))
        if report.get("errors"):
            raise RuntimeError("Semgrep reported analysis errors")
        return results