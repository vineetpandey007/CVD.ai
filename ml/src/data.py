from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

from datasets import load_dataset
from transformers import AutoTokenizer

DATASET_NAME = "code_x_glue_cc_defect_detection"
TOKENIZER_NAME = "microsoft/codebert-base"
SEED = 42


def normalize_code(text: str | None, remove_comments: bool = False) -> str:
    if text is None:
        return ""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").rstrip()
    if remove_comments:
        normalized = re.sub(r"//.*?$", "", normalized, flags=re.MULTILINE)
        normalized = re.sub(r"/\*.*?\*/", "", normalized, flags=re.DOTALL)
        normalized = re.sub(r"(?m)^#.*$", "", normalized)
    return normalized


def hash_code(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_devign_dataset() -> dict[str, Any]:
    return load_dataset(DATASET_NAME)


def summarize_split(rows: Iterable[dict[str, Any]], split_name: str) -> dict[str, Any]:
    counts = Counter(int(row["target"]) for row in rows)
    return {
        "split": split_name,
        "rows": len(rows),
        "label_counts": {"0": counts.get(0, 0), "1": counts.get(1, 0)},
        "positive_rate": (counts.get(1, 0) / max(len(rows), 1)) if rows else 0.0,
    }


def compute_within_split_duplicates(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    hashes = [hash_code(normalize_code(row["func"])) for row in rows]
    counts = Counter(hashes)
    duplicate_hashes = {h: n for h, n in counts.items() if n > 1}
    return {
        "unique_functions": len(counts),
        "duplicate_groups": len(duplicate_hashes),
        "duplicate_rows": sum(n - 1 for n in duplicate_hashes.values()),
    }


def compute_cross_split_duplicates(splits: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    split_hashes = {
        split_name: {hash_code(normalize_code(row["func"])) for row in rows}
        for split_name, rows in splits.items()
    }
    results: dict[str, Any] = {}
    for left_name in ["train", "validation", "test"]:
        for right_name in ["train", "validation", "test"]:
            if left_name >= right_name:
                continue
            overlap = split_hashes[left_name] & split_hashes[right_name]
            results[f"{left_name}_vs_{right_name}"] = len(overlap)
    return results


def remove_cross_split_duplicates(splits: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, int]]:
    train_hashes = {hash_code(normalize_code(row["func"])) for row in splits["train"]}
    validation_hashes = {hash_code(normalize_code(row["func"])) for row in splits["validation"]}
    test_hashes = {hash_code(normalize_code(row["func"])) for row in splits["test"]}

    valid_clean = [
        row for row in splits["validation"]
        if hash_code(normalize_code(row["func"])) not in train_hashes and hash_code(normalize_code(row["func"])) not in test_hashes
    ]
    test_clean = [
        row for row in splits["test"]
        if hash_code(normalize_code(row["func"])) not in train_hashes and hash_code(normalize_code(row["func"])) not in validation_hashes
    ]

    cleaned = {
        "train": list(splits["train"]),
        "validation": valid_clean,
        "test": test_clean,
    }
    removed = {
        "validation": len(splits["validation"]) - len(valid_clean),
        "test": len(splits["test"]) - len(test_clean),
    }
    return cleaned, removed


def token_length_stats(tokenizer: Any, codes: list[str], over_limit: int = 512) -> dict[str, Any]:
    lengths = [len(tokenizer.encode(code, add_special_tokens=False)) for code in codes]
    return {
        "count": len(lengths),
        "min": min(lengths) if lengths else 0,
        "max": max(lengths) if lengths else 0,
        "mean": mean(lengths) if lengths else 0.0,
        "over_512": sum(1 for length in lengths if length > over_limit),
        "pct_over_512": (sum(1 for length in lengths if length > over_limit) / len(lengths)) * 100 if lengths else 0.0,
    }


def save_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_tokenizer(model_name: str = TOKENIZER_NAME):
    return AutoTokenizer.from_pretrained(model_name)
