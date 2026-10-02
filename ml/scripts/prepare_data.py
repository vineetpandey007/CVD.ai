from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from transformers import AutoTokenizer

from ml.src.common import SEED, set_seed
from ml.src.data import (
    TOKENIZER_NAME,
    compute_cross_split_duplicates,
    compute_within_split_duplicates,
    load_devign_dataset,
    normalize_code,
    remove_cross_split_duplicates,
    save_jsonl,
    summarize_split,
    token_length_stats,
)

DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR = ROOT / "results"


def _record_rows(rows: list[dict[str, object]]) -> list[dict[str, int | str]]:
    return [{
        "id": int(row["id"]),
        "code": normalize_code(str(row["func"])),
        "label": int(bool(row["target"])),
    } for row in rows]


def main() -> None:
    set_seed(SEED)
    dataset = load_devign_dataset()
    split_names = ["train", "validation", "test"]
    print("Source:", "datasets.load_dataset('code_x_glue_cc_defect_detection')")
    print("Columns:", dataset["train"].column_names)

    for split_name in split_names:
        rows = dataset[split_name]
        summary = summarize_split(rows, split_name)
        print(f"{split_name}: rows={summary['rows']}, label_counts={summary['label_counts']}, positive_rate={summary['positive_rate']:.4f}")

    within_duplicates = {
        split_name: compute_within_split_duplicates(dataset[split_name])
        for split_name in split_names
    }
    across_duplicates = compute_cross_split_duplicates({split_name: list(dataset[split_name]) for split_name in split_names})
    print("Within-split duplicate counts:", within_duplicates)
    print("Across-split duplicate counts:", across_duplicates)

    cleaned, removed = remove_cross_split_duplicates({split_name: list(dataset[split_name]) for split_name in split_names})
    print("Cross-split duplicates removed:", removed)

    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)
    all_rows = [row for split_name in split_names for row in dataset[split_name]]
    sample_rows = random.Random(SEED).sample(all_rows, 2000)
    raw_codes = [normalize_code(str(row["func"])) for row in sample_rows]
    comment_stripped_codes = [normalize_code(str(row["func"]), remove_comments=True) for row in sample_rows]
    raw_stats = token_length_stats(tokenizer, raw_codes)
    stripped_stats = token_length_stats(tokenizer, comment_stripped_codes)
    print("Token length stats (raw):", raw_stats)
    print("Token length stats (without comments):", stripped_stats)
    print("Percent over 512 tokens (raw):", f"{raw_stats['pct_over_512']:.2f}%")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for split_name in ["train", "validation", "test"]:
        target_name = "valid" if split_name == "validation" else split_name
        rows = _record_rows(cleaned[split_name])
        save_jsonl(PROCESSED_DIR / f"{target_name}.jsonl", rows)

    results = {
        "source": "datasets.load_dataset('code_x_glue_cc_defect_detection')",
        "columns": dataset["train"].column_names,
        "split_summary": {split_name: summarize_split(dataset[split_name], split_name) for split_name in split_names},
        "within_split_duplicates": within_duplicates,
        "across_split_duplicates": across_duplicates,
        "cross_split_duplicates_removed": removed,
        "token_length_stats": {
            "raw": raw_stats,
            "without_comments": stripped_stats,
        },
        "pct_over_512_tokens": raw_stats["pct_over_512"],
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "data_stats.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("Saved processed splits:", sorted(str(path.name) for path in PROCESSED_DIR.glob("*.jsonl")))
    print("Saved data stats:", RESULTS_DIR / "data_stats.json")


if __name__ == "__main__":
    main()
