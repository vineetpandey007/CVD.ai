import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from ..schemas import Finding
from .cwe_lookup import get_cwe
from .subprocess_utils import command_exists, run_command

SUBPROCESS_TIMEOUT_SECONDS = 15
LANGUAGE_SUFFIX = {"c": ".c", "cpp": ".cpp"}


def run_cppcheck(code: str, language: str) -> list[Finding]:
    if language not in LANGUAGE_SUFFIX:
        raise ValueError(f"Cppcheck supports C/C++ only, not {language}")
    if not command_exists("cppcheck"):
        raise FileNotFoundError("cppcheck not installed")
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=LANGUAGE_SUFFIX[language], delete=False, encoding="utf-8"
    ) as temp_file:
        temp_file.write(code)
        temp_path = temp_file.name
    try:
        completed = run_command(
            [
                "cppcheck",
                "--enable=warning,style",
                "--xml",
                "--xml-version=2",
                temp_path,
            ],
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
        try:
            xml_start = completed.stderr.find("<?xml")
            if xml_start < 0:
                xml_start = completed.stderr.find("<results")
            if xml_start < 0:
                raise ET.ParseError("Cppcheck output did not contain XML")
            report = ET.fromstring(completed.stderr[xml_start:])
        except ET.ParseError as exc:
            raise RuntimeError("Cppcheck returned invalid XML") from exc
        findings: list[Finding] = []
        for error in report.findall("./errors/error"):
            if error.get("severity") not in {"error", "warning", "style"}:
                continue
            location = error.find("location")
            raw_cwe = error.get("cwe")
            supplied_cwe = f"CWE-{raw_cwe}" if raw_cwe and raw_cwe.isdigit() else raw_cwe
            findings.append(
                Finding(
                    line=int(location.get("line")) if location is not None and location.get("line") else None,
                    severity="vulnerable",
                    label=error.get("msg") or error.get("id") or "Cppcheck finding",
                    cwe=get_cwe("cppcheck", error.get("id"), supplied_cwe),
                    confidence=None,
                    source="cppcheck",
                )
            )
        return findings
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("Cppcheck analysis timed out") from exc
    except UnicodeDecodeError as exc:
        raise RuntimeError("Cppcheck output was not valid UTF-8") from exc
    finally:
        os.unlink(temp_path)
