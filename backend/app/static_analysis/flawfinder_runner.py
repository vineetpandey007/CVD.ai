import json
import os
import subprocess
import tempfile

from ..schemas import Finding
from .cwe_lookup import get_cwe
from .subprocess_utils import run_command

SUBPROCESS_TIMEOUT_SECONDS = 15
LANGUAGE_SUFFIX = {"c": ".c", "cpp": ".cpp"}


def run_flawfinder(code: str, language: str) -> list[Finding]:
    if language not in LANGUAGE_SUFFIX:
        raise ValueError(f"Flawfinder supports C/C++ only, not {language}")
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=LANGUAGE_SUFFIX[language], delete=False, encoding="utf-8"
    ) as temp_file:
        temp_file.write(code)
        temp_path = temp_file.name
    try:
        completed = run_command(
            ["flawfinder", "--sarif", temp_path],
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"Flawfinder failed: {completed.stderr.strip()}")
        try:
            report = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Flawfinder returned invalid SARIF") from exc

        findings: list[Finding] = []
        for run in report.get("runs", []):
            rules = {
                rule.get("id"): rule
                for rule in run.get("tool", {}).get("driver", {}).get("rules", [])
            }
            for result in run.get("results", []):
                rule_id = result.get("ruleId")
                rule = rules.get(rule_id, {})
                relationships = rule.get("relationships", [])
                supplied_cwes = [
                    relation.get("target", {}).get("id")
                    for relation in relationships
                    if "relevant" in relation.get("kinds", [])
                    and relation.get("target", {}).get("toolComponent", {}).get("name")
                    == "CWE"
                ]
                locations = result.get("locations", [])
                region = (
                    locations[0]
                    .get("physicalLocation", {})
                    .get("region", {})
                    if locations
                    else {}
                )
                findings.append(
                    Finding(
                        line=region.get("startLine"),
                        severity="vulnerable",
                        label=result.get("message", {}).get("text")
                        or rule.get("name")
                        or "Flawfinder finding",
                        cwe=get_cwe("flawfinder", rule_id, supplied_cwes),
                        confidence=None,
                        source="flawfinder",
                    )
                )
        return findings
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("Flawfinder analysis timed out") from exc
    except UnicodeDecodeError as exc:
        raise RuntimeError("Flawfinder output was not valid UTF-8") from exc
    finally:
        os.unlink(temp_path)
