from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.src.common import SEED, set_seed
from ml.src.data import read_jsonl
from ml.src.metrics import compute_metrics, find_optimal_threshold

PROCESSED_DIR = ROOT / "data" / "processed"
RESULTS_PATH = ROOT / "results" / "tfidf_metrics.json"
TOKEN_PATTERN = re.compile(r"[a-zA-Z_]\w+|[^\s\w]")
VECTORIZER_PARAMS = {
    "token_pattern": r"[a-zA-Z_]\w+|[^\s\w]",
    "ngram_range": [1, 2],
    "min_df": 2,
    "max_features": 200000,
    "sublinear_tf": True,
}
CLASSIFIER_PARAMS = {
    "class_weight": "balanced",
    "max_iter": 1000,
    "solver": "lbfgs",
    "random_state": SEED,
}


def tokenize_code(code: str) -> list[str]:
    return TOKEN_PATTERN.findall(code)


def _load_split(name: str) -> tuple[list[str], np.ndarray]:
    path = PROCESSED_DIR / f"{name}.jsonl"
    rows = read_jsonl(path)
    if not rows:
        raise FileNotFoundError(f"No rows found in {path}")
    return (
        [str(row["code"]) for row in rows],
        np.asarray([int(row["label"]) for row in rows], dtype=int),
    )


def _score(labels: np.ndarray, probabilities: np.ndarray, threshold: float) -> dict[str, Any]:
    return {
        "threshold": threshold,
        **compute_metrics(labels, probabilities, threshold=threshold),
    }


def main() -> None:
    set_seed(SEED)
    train_codes, y_train = _load_split("train")
    valid_codes, y_valid = _load_split("valid")
    test_codes, y_test = _load_split("test")

    vectorizer = TfidfVectorizer(
        tokenizer=tokenize_code,
        token_pattern=None,
        ngram_range=(1, 2),
        min_df=2,
        max_features=200000,
        sublinear_tf=True,
    )
    started = time.perf_counter()
    x_train = vectorizer.fit_transform(train_codes)
    x_valid = vectorizer.transform(valid_codes)
    x_test = vectorizer.transform(test_codes)
    classifier = LogisticRegression(**CLASSIFIER_PARAMS)
    classifier.fit(x_train, y_train)
    train_seconds = time.perf_counter() - started

    validation_probabilities = classifier.predict_proba(x_valid)[:, 1]
    test_probabilities = classifier.predict_proba(x_test)[:, 1]
    optimal_threshold = find_optimal_threshold(y_valid, validation_probabilities)

    majority = DummyClassifier(strategy="most_frequent")
    majority.fit(x_train, y_train)
    majority_valid = majority.predict_proba(x_valid)[:, 1]
    majority_test = majority.predict_proba(x_test)[:, 1]

    rng = np.random.RandomState(SEED)
    random_valid = rng.random_sample(len(y_valid))
    random_test = rng.random_sample(len(y_test))

    results = {
        "dataset": "CodeXGLUE Devign",
        "seed": SEED,
        "train_time_seconds": train_seconds,
        "train_rows": len(y_train),
        "validation_rows": len(y_valid),
        "test_rows": len(y_test),
        "vocabulary_size": len(vectorizer.vocabulary_),
        "vectorizer_params": VECTORIZER_PARAMS,
        "classifier_params": CLASSIFIER_PARAMS,
        "optimal_validation_threshold": optimal_threshold,
        "validation": {
            "at_0_5": _score(y_valid, validation_probabilities, 0.5),
            "at_optimal_threshold": _score(y_valid, validation_probabilities, optimal_threshold),
        },
        "test": {
            "at_0_5": _score(y_test, test_probabilities, 0.5),
            "at_optimal_validation_threshold": _score(y_test, test_probabilities, optimal_threshold),
        },
        "dummy_baselines": {
            "majority_class": {
                "validation_at_0_5": _score(y_valid, majority_valid, 0.5),
                "test_at_0_5": _score(y_test, majority_test, 0.5),
            },
            "random_chance": {
                "seed": SEED,
                "validation_at_0_5": _score(y_valid, random_valid, 0.5),
                "test_at_0_5": _score(y_test, random_test, 0.5),
            },
        },
    }
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Train time: {train_seconds:.3f}s")
    print(f"Optimal validation threshold: {optimal_threshold:.2f}")
    print(f"Saved metrics: {RESULTS_PATH}")
    print(json.dumps(results, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
