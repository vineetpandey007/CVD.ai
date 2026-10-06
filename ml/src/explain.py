from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch
from captum.attr import LayerIntegratedGradients
from transformers import AutoModelForSequenceClassification, AutoTokenizer


@dataclass
class PreparedCode:
    input_ids: torch.Tensor
    attention_mask: torch.Tensor
    offsets: list[tuple[int, int]]
    tokens: list[str]


def prepare_code(
    code: str, tokenizer: AutoTokenizer, max_length: int = 512
) -> PreparedCode:
    """Tokenize using fine-tuning's CLS + head/tail + SEP policy."""
    encoding = tokenizer(
        code,
        add_special_tokens=False,
        return_offsets_mapping=True,
        truncation=False,
    )
    ids = list(encoding["input_ids"])
    offsets = [tuple(offset) for offset in encoding["offset_mapping"]]
    if len(ids) > max_length - 2:
        content_length = max_length - 2
        head_length = 384 if content_length >= 510 else max(1, round(content_length * 0.75))
        tail_length = content_length - head_length
        if tail_length:
            ids = ids[:head_length] + ids[-tail_length:]
            offsets = offsets[:head_length] + offsets[-tail_length:]
        else:
            ids = ids[:head_length]
            offsets = offsets[:head_length]

    ids = [tokenizer.cls_token_id, *ids, tokenizer.sep_token_id]
    offsets = [(0, 0), *offsets, (0, 0)]
    tokens = tokenizer.convert_ids_to_tokens(ids)
    return PreparedCode(
        input_ids=torch.tensor([ids], dtype=torch.long),
        attention_mask=torch.ones((1, len(ids)), dtype=torch.long),
        offsets=offsets,
        tokens=list(tokens),
    )


def aggregate_line_scores(
    code: str,
    offsets: list[tuple[int, int]],
    token_scores: list[float],
    tokens: list[str],
) -> list[dict[str, Any]]:
    """Aggregate absolute token attribution by source line and scale to [0, 1]."""
    if not (len(offsets) == len(token_scores) == len(tokens)):
        raise ValueError("offsets, token_scores, and tokens must have equal lengths")

    lines = code.splitlines(keepends=True)
    if not lines and code == "":
        return []
    line_starts = [0]
    for line in lines:
        line_starts.append(line_starts[-1] + len(line))

    totals = [0.0 for _ in lines]
    token_records: list[list[tuple[float, str]]] = [[] for _ in lines]
    for (start, end), score, token in zip(offsets, token_scores, tokens):
        if start == end:
            continue
        if not code[start:end].strip():
            continue
        first_line = max(0, min(len(lines) - 1, _offset_line(line_starts, start)))
        last_line = max(first_line, min(len(lines) - 1, _offset_line(line_starts, end - 1)))
        share = abs(float(score)) / (last_line - first_line + 1)
        for line_index in range(first_line, last_line + 1):
            totals[line_index] += share
            token_records[line_index].append((abs(float(score)), token))

    minimum = min(totals, default=0.0)
    maximum = max(totals, default=0.0)
    scale = maximum - minimum
    result = []
    for index, total in enumerate(totals, start=1):
        normalized = (total - minimum) / scale if scale > 0 else 0.0
        ranked = sorted(token_records[index - 1], reverse=True)
        result.append(
            {
                "line": index,
                "score": float(normalized),
                "top_tokens": [token for _, token in ranked[:5]],
            }
        )
    return result


def _offset_line(line_starts: list[int], offset: int) -> int:
    low = 0
    high = len(line_starts) - 1
    while low < high:
        middle = (low + high + 1) // 2
        if line_starts[middle] <= offset:
            low = middle
        else:
            high = middle - 1
    return low


class CodeExplainer:
    def __init__(
        self,
        model: AutoModelForSequenceClassification,
        tokenizer: AutoTokenizer,
        device: torch.device | str = "cpu",
        n_steps: int = 50,
        max_length: int = 512,
    ) -> None:
        if n_steps < 1:
            raise ValueError("n_steps must be positive")
        self.model = model.to(device).eval()
        self.tokenizer = tokenizer
        self.device = torch.device(device)
        self.n_steps = n_steps
        self.max_length = max_length
        self.layer = self.model.roberta.embeddings
        self.lig = LayerIntegratedGradients(self._forward, self.layer)

    def _forward(
        self, input_ids: torch.Tensor, attention_mask: torch.Tensor
    ) -> torch.Tensor:
        output = self.model(input_ids=input_ids, attention_mask=attention_mask)
        return output.logits[:, 1]

    def explain(self, code: str, n_steps: int | None = None) -> dict[str, Any]:
        prepared = prepare_code(code, self.tokenizer, self.max_length)
        inputs = prepared.input_ids.to(self.device)
        attention_mask = prepared.attention_mask.to(self.device)
        baseline = torch.full_like(inputs, self.tokenizer.pad_token_id)
        special_ids = set(self.tokenizer.all_special_ids)
        for position, token_id in enumerate(inputs[0].tolist()):
            if token_id in special_ids:
                baseline[0, position] = token_id

        attributions, delta = self.lig.attribute(
            inputs=inputs,
            baselines=baseline,
            additional_forward_args=(attention_mask,),
            target=None,
            n_steps=n_steps or self.n_steps,
            internal_batch_size=8 if self.device.type == "cpu" else None,
            return_convergence_delta=True,
        )
        token_scores = attributions.sum(dim=-1).squeeze(0).detach().cpu().tolist()
        line_scores = aggregate_line_scores(
            code, prepared.offsets, token_scores, prepared.tokens
        )
        return {
            "prediction_tokens": len(prepared.offsets),
            "line_scores": line_scores,
            "completeness_delta": float(delta.detach().abs().max().cpu().item()),
            "token_attributions": [
                {
                    "token": token,
                    "offset": [int(start), int(end)],
                    "score": float(score),
                }
                for token, (start, end), score in zip(
                    prepared.tokens, prepared.offsets, token_scores
                )
                if end > start and code[start:end].strip()
            ],
        }


def predict_probability(
    code: str,
    model: AutoModelForSequenceClassification,
    tokenizer: AutoTokenizer,
    device: torch.device | str = "cpu",
    max_length: int = 512,
) -> float:
    prepared = prepare_code(code, tokenizer, max_length)
    with torch.no_grad():
        logits = model(
            input_ids=prepared.input_ids.to(device),
            attention_mask=prepared.attention_mask.to(device),
        ).logits
        return float(torch.softmax(logits, dim=-1)[0, 1].cpu().item())
