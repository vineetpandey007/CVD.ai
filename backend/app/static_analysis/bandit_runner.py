import json
import os
import subprocess
import tempfile

from ..schemas import Finding
from .cwe_lookup import get_cwe
from .subprocess_utils import run_command

SUBPROCESS_TIMEOUT_SECONDS = 15


def run_bandit(code: str) -> list[Finding]:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as temp_file:
        temp_file.write(code)
        temp_path = temp_file.name
    try:
        completed = run_command(
            ["bandit", "-f", "json", temp_path],
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
        if not completed.stdout.strip():
            raise RuntimeError("Bandit returned empty output")
        try:
            report = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Bandit returned invalid JSON") from exc

        if report.get("errors"):
            raise RuntimeError("Bandit reported analysis errors")
        findings: list[Finding] = []
        for result in report.get("results", []):
            cwe = result.get("issue_cwe")
            cwe_id = cwe.get("id") if isinstance(cwe, dict) else cwe
            supplied_cwe = (
                f"CWE-{cwe_id}" if cwe_id and str(cwe_id).isdigit() else cwe_id
            )
            findings.append(
                Finding(
                    line=result.get("line_number"),
                    severity="vulnerable",
                    label=result.get("issue_text", "Bandit finding"),
                    cwe=get_cwe("bandit", result.get("test_id"), supplied_cwe),
                    confidence=None,
                    source="bandit",
                )
            )
        return findings
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("Bandit analysis timed out") from exc
    except UnicodeDecodeError as exc:
        raise RuntimeError("Bandit output was not valid UTF-8") from exc
    finally:
        os.unlink(temp_path)