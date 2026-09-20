import json
import os
import subprocess
import tempfile

from ..schemas import Finding


SUBPROCESS_TIMEOUT_SECONDS = 30
ALLOWED_LANGUAGES = {"python", "javascript", "java", "c", "cpp"}
LANGUAGE_SUFFIX = {
    "python": ".py",
    "javascript": ".js",
    "java": ".java",
    "c": ".c",
    "cpp": ".cpp",
}


def run_semgrep(code: str, language: str) -> list[Finding]:
    if language not in ALLOWED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
    suffix = LANGUAGE_SUFFIX[language]
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, delete=False
    ) as temp_file:
        temp_file.write(code)
        temp_path = temp_file.name
    try:
        completed = subprocess.run(
            [
                "semgrep",
                "--config",
                "p/ci",
                "--config",
                "p/owasp-top-ten",
                "--json",
                temp_path,
            ],
            capture_output=True,
            text=True,
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
            extra = result.get("extra", {})
            metadata = extra.get("metadata", {})
            cwe = metadata.get("cwe")
            if isinstance(cwe, list):
                cwe = cwe[0] if cwe else None
            findings.append(
                Finding(
                    line=result.get("start", {}).get("line"),
                    severity="vulnerable",
                    label=extra.get("message") or result.get("check_id", "Semgrep finding"),
                    cwe=cwe,
                    confidence=None,
                    source="semgrep",
                )
            )
        return findings
    except subprocess.TimeoutExpired:
        return []
    except UnicodeDecodeError as exc:
        raise RuntimeError("Semgrep output was not valid UTF-8") from exc
    finally:
        os.unlink(temp_path)