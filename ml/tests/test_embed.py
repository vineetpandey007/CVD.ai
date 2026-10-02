from __future__ import annotations

import numpy as np
import torch

from ml.scripts.embed import encode_texts, mean_pool


class _Encoded(dict):
    def to(self, device: torch.device):
        return _Encoded({key: value.to(device) for key, value in self.items()})


class _Tokenizer:
    def __call__(self, texts, **kwargs):
        token_ids = [[ord(char) % 16 + 1 for char in text] or [1] for text in texts]
        width = max(map(len, token_ids))
        ids = torch.zeros((len(texts), width), dtype=torch.long)
        mask = torch.zeros_like(ids)
        for row, tokens in enumerate(token_ids):
            ids[row, :len(tokens)] = torch.tensor(tokens)
            mask[row, :len(tokens)] = 1
        return _Encoded(input_ids=ids, attention_mask=mask)


class _Model(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding = torch.nn.Embedding(32, 4)
        with torch.no_grad():
            self.embedding.weight.copy_(torch.arange(128).reshape(32, 4) / 128)

    def forward(self, input_ids, attention_mask):
        return type("Output", (), {"last_hidden_state": self.embedding(input_ids)})()


def test_pooling_ignores_padding() -> None:
    short = torch.tensor([[[1.0, 2.0], [3.0, 4.0]]])
    short_mask = torch.tensor([[1, 1]], dtype=torch.long)
    padded = torch.tensor([[[1.0, 2.0], [3.0, 4.0], [99.0, 101.0], [-5.0, 7.0]]])
    padded_mask = torch.tensor([[1, 1, 0, 0]], dtype=torch.long)
    assert torch.allclose(mean_pool(short, short_mask), mean_pool(padded, padded_mask))


def test_different_functions_embed_differently() -> None:
    model = _Model().eval()
    tokenizer = _Tokenizer()
    a = encode_texts(["int add(int a, int b) { return a + b; }"], tokenizer, model, torch.device("cpu"))
    b = encode_texts(["void clear(char *p) { *p = 0; }"], tokenizer, model, torch.device("cpu"))
    assert not torch.allclose(a, b)


def test_deterministic_output() -> None:
    model = _Model().eval()
    tokenizer = _Tokenizer()
    code = ["int check(int x) { return x != 0; }"]
    first = encode_texts(code, tokenizer, model, torch.device("cpu"))
    second = encode_texts(code, tokenizer, model, torch.device("cpu"))
    assert torch.equal(first, second)
