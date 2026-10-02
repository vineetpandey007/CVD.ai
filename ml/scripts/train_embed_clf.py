from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from ml.src.common import SEED, set_seed
from ml.src.metrics import compute_metrics, find_optimal_threshold

EMBED_DIR = ROOT / "data" / "embeddings"
RESULTS_PATH = ROOT / "results" / "frozen_codebert_metrics.json"


def load_split(split_name: str) -> tuple[np.ndarray, np.ndarray]:
    emb = np.load(EMBED_DIR / f"{split_name}.npy")
    with (EMBED_DIR / f"{split_name}_ids.json").open("r", encoding="utf-8") as handle:
        embedding_ids = json.load(handle)
    rows = []
    with (ROOT / "data" / "processed" / f"{split_name}.jsonl").open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    labels = np.asarray([int(row["label"]) for row in rows], dtype=int)
    processed_ids = [int(row["id"]) for row in rows]
    if embedding_ids != processed_ids or len(emb) != len(labels):
        raise ValueError(
            f"Cached {split_name} embeddings do not match the complete processed split"
        )
    return emb, labels


def main() -> None:
    set_seed(SEED)
    X_train, y_train = load_split("train")
    X_valid, y_valid = load_split("valid")
    X_test, y_test = load_split("test")

    clf = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    clf.fit(X_train, y_train)
    valid_prob = clf.predict_proba(X_valid)[:, 1]
    test_prob = clf.predict_proba(X_test)[:, 1]
    optimal = find_optimal_threshold(y_valid, valid_prob)

    results = {
        "seed": SEED,
        "optimal_validation_threshold": optimal,
        "validation": {
            "at_0_5": compute_metrics(y_valid, valid_prob, threshold=0.5),
            "at_optimal_threshold": compute_metrics(y_valid, valid_prob, threshold=optimal),
        },
        "test": {
            "at_0_5": compute_metrics(y_test, test_prob, threshold=0.5),
            "at_optimal_validation_threshold": compute_metrics(y_test, test_prob, threshold=optimal),
        },
    }
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(results, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
