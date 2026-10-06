from __future__ import annotations

import argparse
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

from ml.scripts.evaluate import find_latest_checkpoint, load_rows
from ml.src.explain import CodeExplainer, predict_probability, prepare_code

TEST_PATH = ROOT / "data" / "processed" / "test.jsonl"
PREDICTIONS_PATH = ROOT / "results" / "codebert_test_predictions.jsonl"
OUTPUT_PATH = ROOT / "results" / "explanations.json"


def read_predictions(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def delete_offsets(code: str, offsets: list[tuple[int, int]]) -> str:
    chars = list(code)
    for start, end in offsets:
        for index in range(max(0, start), min(len(chars), end)):
            chars[index] = " "
    return "".join(chars)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_steps", type=int, default=50)
    parser.add_argument("--max_length", type=int, default=512)
    parser.add_argument("--faithfulness_samples", type=int, default=50)
    parser.add_argument("--cpu_max_length", type=int, default=128)
    args = parser.parse_args()
    if args.n_steps < 1 or args.faithfulness_samples < 1:
        raise ValueError("n_steps and faithfulness_samples must be positive")

    device = torch.device("cpu")
    torch.set_num_threads(1)
    checkpoint = find_latest_checkpoint(ROOT / "checkpoints" / "best_codebert")
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint).to(device)
    model.eval()
    requested_length = args.cpu_max_length if device.type == "cpu" else args.max_length
    max_length = min(requested_length, int(model.config.max_position_embeddings) - 2)
    explainer = CodeExplainer(model, tokenizer, device, args.n_steps, max_length)

    rows = load_rows(TEST_PATH)
    predictions = read_predictions(PREDICTIONS_PATH)
    if len(rows) != len(predictions):
        raise ValueError("Saved test predictions do not align with processed test set")
    for row, prediction in zip(rows, predictions):
        if row.get("id") != prediction.get("id"):
            raise ValueError(f"Prediction ID mismatch at {row.get('id')}")
        if int(row["label"]) != int(prediction["label"]):
            raise ValueError(f"Prediction label mismatch at {row.get('id')}")

    correct = []
    incorrect = []
    for row, prediction in zip(rows, predictions):
        is_correct = int(prediction["prediction"]) == int(row["label"])
        (correct if is_correct else incorrect).append((row, prediction))
    if len(correct) < 5 or len(incorrect) < 5:
        raise ValueError(
            f"Need five correct and five incorrect predictions; got "
            f"{len(correct)} correct and {len(incorrect)} incorrect"
        )
    selected = [
        (row, prediction, "correct") for row, prediction in correct[:5]
    ] + [
        (row, prediction, "error") for row, prediction in incorrect[:5]
    ]

    explanations = []
    attribution_cache: dict[Any, dict[str, Any]] = {}
    for row, prediction, status in tqdm(selected, desc="Explaining examples"):
        result = explainer.explain(str(row["code"]))
        attribution_cache[row.get("id")] = result
        explanations.append(
            {
                "id": row.get("id"),
                "label": int(row["label"]),
                "predicted": int(prediction["prediction"]),
                "probability_vulnerable": float(prediction["probability"]),
                "status": status,
                **result,
            }
        )

    sample_size = min(args.faithfulness_samples, len(rows))
    faithfulness_rows = rows[:sample_size]
    rng = np.random.default_rng(42)
    drops: dict[str, dict[str, list[float]]] = {
        "top_attributed": {"5": [], "10": []},
        "random": {"5": [], "10": []},
    }
    faithfulness_delta = []
    for row in tqdm(faithfulness_rows, desc="Faithfulness test"):
        code = str(row["code"])
        explanation = attribution_cache.get(row.get("id"))
        if explanation is None:
            explanation = explainer.explain(code)
            attribution_cache[row.get("id")] = explanation
        faithfulness_delta.append(explanation["completeness_delta"])
        attribution_rows = explanation["token_attributions"]
        eligible = [
            item
            for item in attribution_rows
            if int(item["offset"][1]) > int(item["offset"][0])
        ]
        ranked = sorted(
            eligible, key=lambda item: abs(float(item["score"])), reverse=True
        )
        base_probability = predict_probability(code, model, tokenizer, device, max_length)
        for k in (5, 10):
            top_items = ranked[: min(k, len(ranked))]
            top_offsets = [
                (int(item["offset"][0]), int(item["offset"][1]))
                for item in top_items
            ]
            top_modified = delete_offsets(code, top_offsets)
            top_probability = predict_probability(
                top_modified, model, tokenizer, device, max_length
            )
            drops["top_attributed"][str(k)].append(base_probability - top_probability)

            chosen = (
                rng.choice(len(eligible), size=min(k, len(eligible)), replace=False)
                if eligible
                else []
            )
            random_offsets = [
                (
                    int(eligible[int(index)]["offset"][0]),
                    int(eligible[int(index)]["offset"][1]),
                )
                for index in chosen
            ]
            random_modified = delete_offsets(code, random_offsets)
            random_probability = predict_probability(
                random_modified, model, tokenizer, device, max_length
            )
            drops["random"][str(k)].append(base_probability - random_probability)

    faithfulness = {
        "samples": sample_size,
        "seed": 42,
        "mean_probability_drop": {
            condition: {
                k: float(np.mean(values)) if values else 0.0
                for k, values in per_k.items()
            }
            for condition, per_k in drops.items()
        },
    }
    output = {
        "checkpoint": str(checkpoint.relative_to(ROOT.parent)),
        "device": str(device),
        "n_steps": args.n_steps,
        "explanations": explanations,
        "mean_completeness_delta": float(np.mean(faithfulness_delta)),
        "faithfulness": faithfulness,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"Saved {OUTPUT_PATH}")
    print(f"mean_completeness_delta={output['mean_completeness_delta']:.8f}")
    print(
        "mean_probability_drop="
        + json.dumps(faithfulness["mean_probability_drop"], sort_keys=True)
    )
    print("example_explanation=")
    print(json.dumps(explanations[0], indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
