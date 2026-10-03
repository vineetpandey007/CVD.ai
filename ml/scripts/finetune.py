from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from ml.src.common import SEED, load_config, set_seed
from ml.src.metrics import compute_metrics

PROCESSED_DIR = ROOT / "data" / "processed"
CHECKPOINT_DIR = ROOT / "checkpoints" / "best_codebert"


def load_rows(path: Path, max_samples: int | None = None) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows.append(json.loads(line))
            if max_samples is not None and len(rows) >= max_samples:
                break
    return rows


def tokenize_batch(texts: list[str], tokenizer: AutoTokenizer, max_length: int) -> dict[str, torch.Tensor]:
    encoded = tokenizer(texts, add_special_tokens=False, truncation=False)
    input_ids = []
    for ids in encoded["input_ids"]:
        if len(ids) > max_length - 2:
            content_length = max_length - 2
            head_length = 384 if content_length >= 510 else max(1, round(content_length * 0.75))
            tail_length = content_length - head_length
            tail_ids = ids[-tail_length:] if tail_length else []
            ids = ids[:head_length] + tail_ids
        input_ids.append(
            [tokenizer.cls_token_id, *ids[: max_length - 2], tokenizer.sep_token_id]
        )

    padded_length = max(map(len, input_ids))
    padded_ids = []
    attention_masks = []
    for ids in input_ids:
        padding_length = padded_length - len(ids)
        padded_ids.append(ids + [tokenizer.pad_token_id] * padding_length)
        attention_masks.append([1] * len(ids) + [0] * padding_length)
    return {
        "input_ids": torch.tensor(padded_ids, dtype=torch.long),
        "attention_mask": torch.tensor(attention_masks, dtype=torch.long),
    }


def predict_probabilities(model: AutoModelForSequenceClassification, rows: list[dict], tokenizer: AutoTokenizer, max_length: int, device: torch.device, batch_size: int = 32) -> np.ndarray:
    model.eval()
    probabilities: list[float] = []
    with torch.no_grad():
        for start in range(0, len(rows), batch_size):
            batch_rows = rows[start:start + batch_size]
            batch = tokenize_batch([str(row["code"]) for row in batch_rows], tokenizer, max_length)
            batch = {k: v.to(device) for k, v in batch.items()}
            logits = model(**batch).logits
            probabilities.extend(torch.softmax(logits, dim=-1)[:, 1].cpu().tolist())
    return np.asarray(probabilities, dtype=float)


def train_overfit_smoke_test(model_name: str, tokenizer: AutoTokenizer, device: torch.device, max_length: int) -> None:
    rows = load_rows(PROCESSED_DIR / "train.jsonl")[:8]
    if len(rows) != 8:
        raise RuntimeError(f"Expected 8 smoke-test rows, found {len(rows)}")

    if device.type == "cpu":
        torch.set_num_threads(1)
        max_length = min(max_length, 128)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    losses: list[float] = []

    preview_tokens = tokenize_batch([str(rows[0]["code"])], tokenizer, max_length)
    preview = tokenizer.decode(
        preview_tokens["input_ids"][0],
        clean_up_tokenization_spaces=False,
    )
    print("decoded_sample_0:")
    print(preview)
    print("---")

    batch = tokenize_batch([str(row["code"]) for row in rows], tokenizer, max_length)
    batch = {k: v.to(device) for k, v in batch.items()}
    batch["labels"] = torch.tensor(
        [int(row["label"]) for row in rows], dtype=torch.long, device=device
    )

    for step in range(3):
        model.train()
        optimizer.zero_grad()
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        losses.append(float(loss.item()))
        print(f"step={step} loss={losses[-1]:.6f}")

    print("optimizer_steps=3")
    print(f"loss_decreased={losses[-1] < losses[0]}")
    if losses[-1] >= losses[0]:
        raise RuntimeError("Smoke-test loss did not decrease over 3 optimizer steps")
    print("SMOKE_TEST_PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default=str(ROOT / "configs" / "codebert.yaml"))
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--max_train_samples", type=int, default=None)
    parser.add_argument("--max_eval_samples", type=int, default=None)
    parser.add_argument("--overfit_smoke_test", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    set_seed(int(config.get("seed", SEED)))

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but not available")
    device = torch.device(args.device)
    max_length = int(config["max_length"])

    if args.overfit_smoke_test:
        tokenizer = AutoTokenizer.from_pretrained(config["model_name_or_path"])
        train_overfit_smoke_test(config["model_name_or_path"], tokenizer, device, max_length)
        return

    tokenizer = AutoTokenizer.from_pretrained(config["model_name_or_path"])
    model = AutoModelForSequenceClassification.from_pretrained(config["model_name_or_path"], num_labels=2)
    model.to(device)

    train_rows = load_rows(PROCESSED_DIR / "train.jsonl", args.max_train_samples)
    valid_rows = load_rows(PROCESSED_DIR / "valid.jsonl", args.max_eval_samples)

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    for entry in CHECKPOINT_DIR.iterdir():
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()

    optimizer = torch.optim.AdamW(model.parameters(), lr=float(config["learning_rate"]), weight_decay=float(config["weight_decay"]))
    total_steps = max(1, (len(train_rows) // int(config["per_device_train_batch_size"])) * int(config["num_train_epochs"]))
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=max(1, int(total_steps * float(config["warmup_ratio"]))),
        num_training_steps=total_steps,
    )

    best_f1 = -1.0
    best_path: Path | None = None
    for epoch in range(int(config["num_train_epochs"])):
        model.train()
        epoch_loss = 0.0
        epoch_steps = 0
        for start in range(0, len(train_rows), int(config["per_device_train_batch_size"])):
            batch_rows = train_rows[start:start + int(config["per_device_train_batch_size"])]
            batch = tokenize_batch([str(row["code"]) for row in batch_rows], tokenizer, max_length)
            batch = {k: v.to(device) for k, v in batch.items()}
            batch["labels"] = torch.tensor([int(row["label"]) for row in batch_rows], dtype=torch.long, device=device)
            optimizer.zero_grad()
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            scheduler.step()
            epoch_loss += float(loss.item())
            epoch_steps += 1

        valid_probs = predict_probabilities(model, valid_rows, tokenizer, max_length, device, batch_size=int(config["per_device_eval_batch_size"]))
        valid_labels = np.asarray([int(row["label"]) for row in valid_rows], dtype=int)
        valid_metrics = compute_metrics(valid_labels, valid_probs, threshold=0.5)
        print(f"epoch={epoch + 1} train_loss={epoch_loss / max(epoch_steps, 1):.4f} valid_f1={valid_metrics['f1']:.4f} valid_mcc={valid_metrics['mcc']:.4f} valid_pr_auc={valid_metrics['pr_auc']}")

        if float(valid_metrics["f1"]) > best_f1:
            best_f1 = float(valid_metrics["f1"])
            checkpoint_dir = CHECKPOINT_DIR / f"epoch_{epoch + 1}_f1_{best_f1:.4f}"
            if checkpoint_dir.exists():
                shutil.rmtree(checkpoint_dir)
            model.save_pretrained(checkpoint_dir)
            tokenizer.save_pretrained(checkpoint_dir)
            best_path = checkpoint_dir
            print(f"saved_best_checkpoint={checkpoint_dir}")

    if best_path is not None:
        print(f"best_checkpoint={best_path}")


if __name__ == "__main__":
    main()
