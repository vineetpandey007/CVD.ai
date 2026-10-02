from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from ml.src.data import hash_code, normalize_code

PROCESSED = ROOT / "data" / "processed"


def _read_jsonl(split_name: str) -> list[dict[str, object]]:
    path = PROCESSED / f"{split_name}.jsonl"
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _hashes(rows: list[dict[str, object]]) -> set[str]:
    return {hash_code(normalize_code(str(row["code"]))) for row in rows}


def test_no_id_overlap_across_splits() -> None:
    seen: set[int] = set()
    for split in ["train", "valid", "test"]:
        rows = _read_jsonl(split)
        ids = {int(row["id"]) for row in rows}
        assert ids.isdisjoint(seen), f"overlap in {split}: {sorted(ids & seen)[:10]}"
        seen |= ids


def test_labels_are_binary() -> None:
    for split in ["train", "valid", "test"]:
        rows = _read_jsonl(split)
        assert rows, f"{split} split is empty"
        assert all(int(row["label"]) in {0, 1} for row in rows), f"invalid labels in {split}"


def test_no_cross_split_hash_overlap_after_cleaning() -> None:
    train_hashes = _hashes(_read_jsonl("train"))
    valid_hashes = _hashes(_read_jsonl("valid"))
    test_hashes = _hashes(_read_jsonl("test"))

    assert not (train_hashes & valid_hashes)
    assert not (train_hashes & test_hashes)
    assert not (valid_hashes & test_hashes)
