from __future__ import annotations

import sys
from types import SimpleNamespace
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.src.explain import CodeExplainer, aggregate_line_scores, prepare_code


class _Tokenizer:
    cls_token_id = 1
    sep_token_id = 2
    pad_token_id = 0
    all_special_ids = [0, 1, 2]

    def __call__(self, text, **kwargs):
        ids = [3 + index for index, _ in enumerate(text.split())]
        offsets = []
        cursor = 0
        for word in text.split():
            start = text.index(word, cursor)
            end = start + len(word)
            offsets.append((start, end))
            cursor = end
        return {"input_ids": ids, "offset_mapping": offsets}

    def convert_ids_to_tokens(self, ids):
        return [f"tok-{token_id}" for token_id in ids]


class _Model(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.roberta = SimpleNamespace()
        self.roberta.embeddings = torch.nn.Embedding(32, 4)
        self.head = torch.nn.Linear(4, 2)
        self.config = SimpleNamespace(max_position_embeddings=16)

    def forward(self, input_ids, attention_mask):
        embedded = self.roberta.embeddings(input_ids)
        mask = attention_mask.unsqueeze(-1)
        pooled = (embedded * mask).sum(1) / mask.sum(1).clamp(min=1)
        return SimpleNamespace(logits=self.head(pooled))


def test_aggregate_line_scores_normalizes_and_selects_top_tokens():
    code = "alpha beta\ncharlie"
    offsets = [(0, 5), (6, 10), (11, 18)]
    result = aggregate_line_scores(code, offsets, [1.0, 3.0, 2.0], ["a", "b", "c"])
    assert result == [
        {"line": 1, "score": 1.0, "top_tokens": ["b", "a"]},
        {"line": 2, "score": 0.0, "top_tokens": ["c"]},
    ]


def test_prepare_code_aligns_token_offsets_and_special_tokens():
    code = "int value\nreturn value"
    prepared = prepare_code(code, _Tokenizer(), max_length=8)
    assert prepared.input_ids.shape == (1, 6)
    assert len(prepared.offsets) == len(prepared.tokens) == 6
    assert prepared.input_ids[0, 0].item() == _Tokenizer.cls_token_id
    assert prepared.input_ids[0, -1].item() == _Tokenizer.sep_token_id
    assert prepared.offsets[0] == prepared.offsets[-1] == (0, 0)
    assert prepared.offsets[1] == (0, 3)
    assert prepared.offsets[2] == (4, 9)


def test_layer_attribution_returns_per_token_offsets_and_delta():
    model = _Model()
    tokenizer = _Tokenizer()
    explainer = CodeExplainer(model, tokenizer, device="cpu", n_steps=2, max_length=12)
    result = explainer.explain("int value", n_steps=2)
    assert result["prediction_tokens"] == 4
    assert len(result["token_attributions"]) == 2
    assert result["token_attributions"][0]["offset"] == [0, 3]
    assert isinstance(result["completeness_delta"], float)
    assert len(result["line_scores"]) == 1
    assert 0.0 <= result["line_scores"][0]["score"] <= 1.0
