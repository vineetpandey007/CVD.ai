import json
import os
import subprocess
import tempfile

from ..schemas import Finding
from .cwe_lookup import get_cwe
from .subprocess_utils import run_command

SUBPROCESS_TIMEOUT_SECONDS = 15


def run_ruff(code: str, language: str = "python") -> list[Finding]:
    if language != "python":
        raise ValueError(f"Ruff supports Python only, not {language}")
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as temp_file:
        temp_file.write(code)
        temp_path = temp_file.name
    try:
        completed = run_command(
            ["ruff", "check", "--select", "S", "--output-format", "json", temp_path],
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
        if completed.returncode not in (0, 1):
            raise RuntimeError(f"Ruff failed: {completed.stderr.strip()}")
        try:
            report = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Ruff returned invalid JSON") from exc
        return [
            Finding(
                line=item.get("location", {}).get("row"),
                severity="vulnerable",
                label=f"{item.get('code', 'Ruff')}: {item.get('message', 'finding')}",
                cwe=get_cwe("ruff", item.get("code")),
                confidence=None,
                source="ruff",
            )
            for item in report
        ]
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("Ruff analysis timed out") from exc
    except UnicodeDecodeError as exc:
        raise RuntimeError("Ruff output was not valid UTF-8") from exc
    finally:
        os.unlink(temp_path)
