from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

ROOT = Path(__file__).resolve().parents[1]
MODEL_NAME = "microsoft/codebert-base"
EMBED_DIR = ROOT / "data" / "embeddings"
PROCESSED_DIR = ROOT / "data" / "processed"


def mean_pool(last_hidden_state: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    masked = last_hidden_state * attention_mask.unsqueeze(-1)
    summed = masked.sum(dim=1)
    counts = attention_mask.sum(dim=1, keepdim=True).clamp(min=1)
    return summed / counts


def encode_texts(
    texts: list[str],
    tokenizer: AutoTokenizer,
    model: AutoModel,
    device: torch.device,
) -> torch.Tensor:
    encoded = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt",
    ).to(device)
    with torch.no_grad():
        outputs = model(**encoded)
        return mean_pool(outputs.last_hidden_state, encoded["attention_mask"])


def embed_split(
    split_name: str,
    tokenizer: AutoTokenizer,
    model: AutoModel,
    device: torch.device,
    batch_size: int,
    max_samples: int | None,
) -> tuple[np.ndarray, list[int], float]:
    rows = []
    with (PROCESSED_DIR / f"{split_name}.jsonl").open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    if max_samples is not None:
        rows = rows[:max_samples]
    all_ids = [int(row["id"]) for row in rows]
    embeddings = []
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    start = time.perf_counter()
    for i in range(0, len(rows), batch_size):
        batch_rows = rows[i:i + batch_size]
        texts = [str(row["code"]) for row in batch_rows]
        pooled = encode_texts(texts, tokenizer, model, device)
        embeddings.append(pooled.cpu().numpy())
    elapsed = time.perf_counter() - start
    embedding_matrix = np.concatenate(embeddings, axis=0) if embeddings else np.empty((0, 768), dtype=np.float32)
    return embedding_matrix.astype(np.float32), all_ids, elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--max_samples", type=int, default=None)
    args = parser.parse_args()

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but not available")
    device = torch.device(args.device)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME).to(device)
    model.eval()

    EMBED_DIR.mkdir(parents=True, exist_ok=True)
    for split_name in ["train", "valid", "test"]:
        emb, ids, elapsed = embed_split(
            split_name, tokenizer, model, device, args.batch_size, args.max_samples
        )
        np.save(EMBED_DIR / f"{split_name}.npy", emb)
        (EMBED_DIR / f"{split_name}_ids.json").write_text(json.dumps(ids), encoding="utf-8")
        print(f"{split_name}: {emb.shape[0]} rows, elapsed={elapsed:.3f}s")

        if args.max_samples is not None:
            raw_total = 0
            with (PROCESSED_DIR / f"{split_name}.jsonl").open("r", encoding="utf-8") as handle:
                raw_total = sum(1 for line in handle if line.strip())
            if raw_total > 0:
                scale = raw_total / max(len(ids), 1)
                estimate = elapsed * scale
                throughput = len(ids) / elapsed if elapsed > 0 else 0.0
                print(f"{split_name}: runtime for {args.max_samples} samples: {elapsed:.3f}s")
                print(f"{split_name}: batch throughput: {throughput:.2f} functions/s")
                print(f"{split_name}: extrapolated full-dataset CPU time estimate: {estimate:.3f}s")


if __name__ == "__main__":
    main()
