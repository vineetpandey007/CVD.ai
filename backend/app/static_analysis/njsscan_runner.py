import json
import os
import subprocess
import tempfile

from ..schemas import Finding
from .cwe_lookup import get_cwe
from .subprocess_utils import run_command

SUBPROCESS_TIMEOUT_SECONDS = 20


def run_njsscan(code: str, language: str = "javascript") -> list[Finding]:
    if language != "javascript":
        raise ValueError(f"njsscan supports JavaScript only, not {language}")
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", delete=False, encoding="utf-8"
    ) as temp_file:
        temp_file.write(code)
        temp_path = temp_file.name
    try:
        completed = run_command(
            ["njsscan", "--json", temp_path],
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"njsscan failed: {completed.stderr.strip()}")
        try:
            report = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("njsscan returned invalid JSON") from exc
        if report.get("errors"):
            raise RuntimeError("njsscan reported scan errors")

        findings: list[Finding] = []
        for section in ("nodejs", "templates"):
            for rule_id, details in report.get(section, {}).items():
                metadata = details.get("metadata") or {}
                for match in details.get("files", []):
                    lines = match.get("match_lines") or []
                    findings.append(
                        Finding(
                            line=int(lines[0]) if lines else None,
                            severity="vulnerable",
                            label=metadata.get("description")
                            or match.get("match_string")
                            or rule_id,
                            cwe=get_cwe("njsscan", rule_id, metadata.get("cwe")),
                            confidence=None,
                            source="njsscan",
                        )
                    )
        return findings
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("njsscan analysis timed out") from exc
    except UnicodeDecodeError as exc:
        raise RuntimeError("njsscan output was not valid UTF-8") from exc
    finally:
        os.unlink(temp_path)
