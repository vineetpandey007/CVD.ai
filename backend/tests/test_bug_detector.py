import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import torch

from app.inference import bug_detector


def test_predict_returns_expected_shape_without_loading_checkpoint(monkeypatch) -> None:
    tokenizer = Mock(return_value={"input_ids": torch.tensor([[0, 1, 2]])})
    model = Mock(return_value=SimpleNamespace(logits=torch.tensor([[0.1, 2.1]])))
    model.config = SimpleNamespace(
        id2label={0: "safe", 1: "vulnerable"},
        cwe_labels={1: "CWE-89"},
    )
    loader = ModuleType("app.inference.model_loader")
    loader.get_model = Mock(return_value=model)
    loader.get_tokenizer = Mock(return_value=tokenizer)
    monkeypatch.setitem(sys.modules, "app.inference.model_loader", loader)

    result = bug_detector.predict("SELECT * FROM users")

    assert set(result) == {"vulnerable", "confidence", "cwe"}
    assert result["vulnerable"] is True
    assert isinstance(result["confidence"], float)
    assert result["cwe"] == "CWE-89"
    tokenizer.assert_called_once_with(
        "SELECT * FROM users", return_tensors="pt", truncation=True
    )
    model.assert_called_once()
