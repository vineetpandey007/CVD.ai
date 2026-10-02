import json
import re
from pathlib import Path

_LOOKUP_PATH = Path(__file__).with_name("cwe_lookup.json")
_LOOKUP: dict[str, dict[str, str]] = json.loads(
    _LOOKUP_PATH.read_text(encoding="utf-8")
)
_CWE_PATTERN = re.compile(r"\bCWE-\d+\b", re.IGNORECASE)


def get_cwe(
    source: str,
    rule_id: str | None,
    supplied: object = None,
) -> str | None:
    candidates = supplied if isinstance(supplied, list) else [supplied]
    for candidate in candidates:
        match = _CWE_PATTERN.search(str(candidate or ""))
        if match:
            return match.group(0).upper()

    if rule_id is None:
        return None
    return _LOOKUP.get(source, {}).get(rule_id)
