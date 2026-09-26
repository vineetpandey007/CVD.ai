import re

import torch


def _label_name(config, index: int) -> str | None:
    id2label = getattr(config, "id2label", {}) or {}
    return id2label.get(index) or id2label.get(str(index))


def _is_vulnerable_label(label: str | None, index: int) -> bool:
    if label:
        normalized = label.lower()
        if any(word in normalized for word in ("vulnerable", "unsafe", "positive")):
            return True
        if any(word in normalized for word in ("safe", "clean", "negative")):
            return False
    return index == 1


def _cwe_from_config(config, index: int, label: str | None) -> str | None:
    configured = getattr(config, "cwe_labels", None)
    if isinstance(configured, dict):
        value = configured.get(index, configured.get(str(index), configured.get(label)))
        values = (value,) if value is not None else ()
    elif isinstance(configured, (list, tuple)):
        values = (configured[index],) if index < len(configured) else ()
    else:
        values = ()
    for value in values:
        match = re.search(r"\bCWE-\d+\b", str(value), re.IGNORECASE)
        if match:
            return match.group(0).upper()

    match = re.search(r"\bCWE-\d+\b", label or "", re.IGNORECASE)
    return match.group(0).upper() if match else None


def predict(code: str) -> dict:
    from .model_loader import get_model, get_tokenizer

    tokenizer = get_tokenizer()
    model = get_model()
    inputs = tokenizer(code, return_tensors="pt", truncation=True)
    inputs = {name: value.to("cpu") for name, value in inputs.items()}

    with torch.no_grad():
        logits = model(**inputs).logits
    probabilities = torch.softmax(logits, dim=-1)[0]
    index = int(torch.argmax(probabilities).item())
    confidence = float(probabilities[index].item())
    config = model.config
    label = _label_name(config, index)
    vulnerable = _is_vulnerable_label(label, index)

    return {
        "vulnerable": vulnerable,
        "confidence": confidence,
        "cwe": _cwe_from_config(config, index, label) if vulnerable else None,
    }