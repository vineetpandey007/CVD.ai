from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from ml.src.metrics import compute_metrics, find_optimal_threshold


def test_compute_metrics_perfect_predictions() -> None:
    metrics = compute_metrics([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9])
    assert metrics["accuracy"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0
    assert metrics["mcc"] == 1.0
    assert metrics["roc_auc"] == 1.0
    assert metrics["pr_auc"] == 1.0
    assert metrics["confusion_matrix"] == [[2, 0], [0, 2]]


def test_compute_metrics_inverted_predictions() -> None:
    metrics = compute_metrics([0, 0, 1, 1], [0.9, 0.8, 0.2, 0.1])
    assert metrics["accuracy"] == 0.0
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0
    assert metrics["f1"] == 0.0
    assert metrics["mcc"] == -1.0
    assert metrics["roc_auc"] == 0.0
    assert metrics["confusion_matrix"] == [[0, 2], [2, 0]]


def test_compute_metrics_all_zero_predictions_handles_zero_division() -> None:
    metrics = compute_metrics([0, 0, 1, 1], [0.1, 0.2, 0.3, 0.4])
    assert metrics["confusion_matrix"] == [[2, 0], [2, 0]]
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0
    assert metrics["f1"] == 0.0
    assert metrics["mcc"] == 0.0


def test_compute_metrics_known_confusion_matrix() -> None:
    metrics = compute_metrics([0, 0, 1, 1], [0.8, 0.2, 0.7, 0.1])
    assert metrics["confusion_matrix"] == [[1, 1], [1, 1]]
    assert metrics["accuracy"] == 0.5
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5
    assert metrics["f1"] == 0.5
    assert metrics["mcc"] == 0.0


def test_compute_metrics_single_class_has_undefined_auc() -> None:
    metrics = compute_metrics([0, 0, 0], [0.1, 0.4, 0.8])
    assert metrics["roc_auc"] is None
    assert metrics["pr_auc"] is None
    assert metrics["confusion_matrix"] == [[2, 1], [0, 0]]


def test_find_optimal_threshold_on_toy_arrays() -> None:
    assert find_optimal_threshold([0, 0, 1, 1], [0.1, 0.4, 0.6, 0.9]) == 0.41
