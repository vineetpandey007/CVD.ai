import json
import os
import subprocess
import tempfile

from ..schemas import Finding


SUBPROCESS_TIMEOUT_SECONDS = 15


def run_bandit(code: str) -> list[Finding]:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as temp_file:
        temp_file.write(code)
        temp_path = temp_file.name
    try:
        completed = subprocess.run(
            ["bandit", "-f", "json", temp_path],
            capture_output=True, text=True,
            encoding="utf-8",
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
            shell=False,
        )
        try:
            report = json.loads(completed.stdout or "{}")
        except json.JSONDecodeError:
            return []

        findings: list[Finding] = []
        for result in report.get("results", []):
            cwe = result.get("issue_cwe")
            cwe_id = cwe.get("id") if isinstance(cwe, dict) else cwe
            findings.append(
                Finding(
                    line=result.get("line_number"),
                    severity="vulnerable",
                    label=result.get("issue_text", "Bandit finding"),
                    cwe=f"CWE-{cwe_id}" if cwe_id and str(cwe_id).isdigit() else cwe_id,
                    confidence=None,
                    source="bandit",
                )
            )
        return findings
    except subprocess.TimeoutExpired:
        return []
    except UnicodeDecodeError as exc:
        raise RuntimeError("Bandit output was not valid UTF-8") from exc
    finally:
        os.unlink(temp_path)