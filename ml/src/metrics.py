from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)


def _validated_arrays(
    y_true: Sequence[int], y_prob: Sequence[float]
) -> tuple[np.ndarray, np.ndarray]:
    actual = np.asarray(y_true, dtype=int)
    probabilities = np.asarray(y_prob, dtype=float)
    if actual.ndim != 1 or probabilities.ndim != 1:
        raise ValueError("y_true and y_prob must be one-dimensional")
    if actual.size == 0:
        raise ValueError("y_true and y_prob must not be empty")
    if actual.size != probabilities.size:
        raise ValueError("y_true and y_prob must have the same length")
    if not np.isin(actual, (0, 1)).all():
        raise ValueError("y_true labels must be 0 or 1")
    if not np.isfinite(probabilities).all():
        raise ValueError("y_prob must contain only finite values")
    if ((probabilities < 0) | (probabilities > 1)).any():
        raise ValueError("y_prob values must be between 0 and 1")
    return actual, probabilities


def compute_metrics(
    y_true: Sequence[int], y_prob: Sequence[float], threshold: float = 0.5
) -> dict[str, Any]:
    actual, probabilities = _validated_arrays(y_true, y_prob)
    if not np.isfinite(threshold):
        raise ValueError("threshold must be finite")
    predicted = (probabilities >= threshold).astype(int)
    matrix = confusion_matrix(actual, predicted, labels=[0, 1])
    auc_defined = np.unique(actual).size == 2

    return {
        "accuracy": float(accuracy_score(actual, predicted)),
        "precision": float(precision_score(actual, predicted, zero_division=0)),
        "recall": float(recall_score(actual, predicted, zero_division=0)),
        "f1": float(f1_score(actual, predicted, zero_division=0)),
        "mcc": float(matthews_corrcoef(actual, predicted)),
        "roc_auc": float(roc_auc_score(actual, probabilities)) if auc_defined else None,
        "pr_auc": float(average_precision_score(actual, probabilities)) if auc_defined else None,
        "confusion_matrix": matrix.tolist(),
    }


def find_optimal_threshold(
    y_true: Sequence[int], y_prob: Sequence[float]
) -> float:
    actual, probabilities = _validated_arrays(y_true, y_prob)
    best_threshold = 0.01
    best_f1 = -1.0
    for step in range(1, 100):
        threshold = step / 100
        score = f1_score(actual, probabilities >= threshold, zero_division=0)
        if score > best_f1:
            best_f1 = score
            best_threshold = threshold
    return best_threshold
