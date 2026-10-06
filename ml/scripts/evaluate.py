from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
from tqdm import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from ml.src.metrics import compute_metrics

CHECKPOINT_ROOT = ROOT / "checkpoints" / "best_codebert"
TEST_PATH = ROOT / "data" / "processed" / "test.jsonl"
OUTPUT_PATH = ROOT / "results" / "codebert_test_metrics.json"
PREDICTIONS_PATH = ROOT / "results" / "codebert_test_predictions.jsonl"
BASELINE_PATH = ROOT / "results" / "tfidf_metrics.json"
BATCH_SIZE = 16


def find_latest_checkpoint(root: Path) -> Path:
    checkpoints = [
        path
        for path in root.iterdir()
        if path.is_dir()
        and (path / "config.json").is_file()
        and any((path / name).is_file() for name in ("model.safetensors", "pytorch_model.bin"))
    ] if root.exists() else []
    if not checkpoints:
        raise FileNotFoundError(f"No fine-tuned model checkpoint found under {root}")
    return max(
        checkpoints,
        key=lambda path: max(
            (path / name).stat().st_mtime_ns
            for name in ("model.safetensors", "pytorch_model.bin")
            if (path / name).is_file()
        ),
    )


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                row = json.loads(line)
                if "code" not in row or "label" not in row:
                    raise ValueError(f"Missing code or label in {path} at line {line_number}")
                rows.append(row)
    if not rows:
        raise ValueError(f"No test samples found in {path}")
    return rows


def tokenize_batch(
    texts: list[str], tokenizer: AutoTokenizer, max_length: int
) -> dict[str, torch.Tensor]:
    tokenized = tokenizer.backend_tokenizer.encode_batch(
        texts, add_special_tokens=False
    )
    sequences: list[list[int]] = []
    for encoding in tokenized:
        token_ids = encoding.ids
        content_length = max_length - 2
        if len(token_ids) > content_length:
            head_length = 384 if content_length >= 510 else max(1, round(content_length * 0.75))
            tail_length = content_length - head_length
            tail_ids = token_ids[-tail_length:] if tail_length else []
            token_ids = token_ids[:head_length] + tail_ids
        sequences.append(
            [tokenizer.cls_token_id, *token_ids[:content_length], tokenizer.sep_token_id]
        )

    padded_length = max(map(len, sequences))
    input_ids = []
    attention_masks = []
    for sequence in sequences:
        padding_length = padded_length - len(sequence)
        input_ids.append(sequence + [tokenizer.pad_token_id] * padding_length)
        attention_masks.append([1] * len(sequence) + [0] * padding_length)
    return {
        "input_ids": torch.tensor(input_ids, dtype=torch.long),
        "attention_mask": torch.tensor(attention_masks, dtype=torch.long),
    }


def compare_baseline(codebert_metrics: dict[str, Any]) -> None:
    if not BASELINE_PATH.is_file():
        print(f"TF-IDF baseline not found: {BASELINE_PATH}")
        return

    with BASELINE_PATH.open("r", encoding="utf-8") as handle:
        baseline = json.load(handle)
    baseline_test = baseline.get("test", {}).get("at_0_5", {})
    print("\nTest-set comparison (threshold 0.5)")
    print(f"{'Model':<24} {'F1':>10} {'MCC':>10} {'PR-AUC':>10}")
    print(
        f"{'TF-IDF':<24} "
        f"{baseline_test.get('f1', float('nan')):>10.4f} "
        f"{baseline_test.get('mcc', float('nan')):>10.4f} "
        f"{baseline_test.get('pr_auc', float('nan')):>10.4f}"
    )
    print(
        f"{'Fine-tuned CodeBERT':<24} "
        f"{codebert_metrics['f1']:>10.4f} "
        f"{codebert_metrics['mcc']:>10.4f} "
        f"{codebert_metrics['pr_auc']:>10.4f}"
    )


def main() -> None:
    checkpoint = find_latest_checkpoint(CHECKPOINT_ROOT)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cpu":
        torch.set_num_threads(1)
    rows = load_rows(TEST_PATH)

    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint)
    model.to(device)
    model.eval()
    max_length = min(
        int(tokenizer.model_max_length),
        int(model.config.max_position_embeddings) - 2,
    )
    if max_length < 3:
        raise ValueError(f"Invalid model/tokenizer maximum length: {max_length}")

    y_true = np.asarray([int(row["label"]) for row in rows], dtype=int)
    y_prob: list[float] = []
    token_lengths: list[int] = []
    with torch.no_grad():
        for start in tqdm(range(0, len(rows), BATCH_SIZE), desc="Evaluating test set"):
            batch_rows = rows[start : start + BATCH_SIZE]
            texts = [str(row["code"]) for row in batch_rows]
            batch = tokenize_batch(texts, tokenizer, max_length)
            batch = {name: tensor.to(device) for name, tensor in batch.items()}
            logits = model(**batch).logits
            y_prob.extend(torch.softmax(logits, dim=-1)[:, 1].cpu().tolist())
            token_lengths.extend(
                len(encoding.ids)
                for encoding in tokenizer.backend_tokenizer.encode_batch(
                    texts, add_special_tokens=False
                )
            )

    metrics = compute_metrics(y_true, y_prob)
    result = {
        "checkpoint": str(checkpoint.relative_to(ROOT.parent)),
        "device": str(device),
        "test_rows": len(rows),
        "threshold": 0.5,
        **metrics,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    with PREDICTIONS_PATH.open("w", encoding="utf-8") as handle:
        for row, probability, token_length in zip(rows, y_prob, token_lengths):
            handle.write(
                json.dumps(
                    {
                        "id": row.get("id"),
                        "label": int(row["label"]),
                        "probability": float(probability),
                        "token_length": token_length,
                        "prediction": int(probability >= 0.5),
                    },
                    allow_nan=False,
                )
                + "\n"
            )

    print(f"checkpoint={checkpoint}")
    print(f"device={device}")
    print(f"test_rows={len(rows)}")
    print(f"accuracy={metrics['accuracy']:.4f}")
    print(f"f1={metrics['f1']:.4f}")
    print(f"mcc={metrics['mcc']:.4f}")
    print(f"roc_auc={metrics['roc_auc']}")
    print(f"pr_auc={metrics['pr_auc']}")
    print(f"confusion_matrix={metrics['confusion_matrix']}")
    print(f"saved={OUTPUT_PATH}")
    print(f"saved_predictions={PREDICTIONS_PATH}")
    compare_baseline(metrics)


if __name__ == "__main__":
    main()
