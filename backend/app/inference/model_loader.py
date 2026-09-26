import os

from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_CHECKPOINT = os.getenv(
    "MODEL_CHECKPOINT",
    "mrm8488/codebert-base-finetuned-detect-insecure-code",
)

_tokenizer = AutoTokenizer.from_pretrained(MODEL_CHECKPOINT)
_model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_CHECKPOINT,
    use_safetensors=False,
)
if _tokenizer.vocab_size != _model.config.vocab_size:
    if _model.config.model_type != "roberta":
        raise ValueError(
            f"Tokenizer vocabulary ({_tokenizer.vocab_size}) does not match "
            f"model vocabulary ({_model.config.vocab_size}) for model type "
            f"{_model.config.model_type!r}."
        )
    _tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
_model.to("cpu")
_model.eval()


def get_model():
    return _model


def get_tokenizer():
    return _tokenizer