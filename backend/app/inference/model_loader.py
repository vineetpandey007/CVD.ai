import os
from threading import Lock

from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_CHECKPOINT = os.getenv(
    "MODEL_CHECKPOINT",
    "mrm8488/codebert-base-finetuned-detect-insecure-code",
)

_tokenizer = None
_model = None
_load_lock = Lock()


def _load() -> None:
    global _model, _tokenizer
    if _model is not None and _tokenizer is not None:
        return
    with _load_lock:
        if _model is not None and _tokenizer is not None:
            return

        tokenizer = AutoTokenizer.from_pretrained(MODEL_CHECKPOINT)
        model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_CHECKPOINT,
            use_safetensors=False,
        )
        if tokenizer.vocab_size != model.config.vocab_size:
            if model.config.model_type != "roberta":
                raise ValueError(
                    f"Tokenizer vocabulary ({tokenizer.vocab_size}) does not match "
                    f"model vocabulary ({model.config.vocab_size}) for model type "
                    f"{model.config.model_type!r}."
                )
            tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        model.to("cpu")
        model.eval()
        _tokenizer = tokenizer
        _model = model


def get_model():
    _load()
    return _model


def get_tokenizer():
    _load()
    return _tokenizer