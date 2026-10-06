import pytest
from ml.src.ast_slicer import get_functions
from ml.src.inference import CVDInference

def test_ast_slicer_multiple_functions():
    code = """
    int safe_func() { return 0; }
    void vuln_func(char *str) { char buf[10]; strcpy(buf, str); }
    """
    funcs = get_functions(code, "c")
    assert len(funcs) == 2
    assert funcs[0]["name"] == "safe_func"
    assert funcs[1]["name"] == "vuln_func"
    assert funcs[0]["start_line"] == 2
    assert funcs[1]["start_line"] == 3

def test_ast_slicer_fallback():
    code = "int x = 10; float y = 20.0;"
    funcs = get_functions(code, "c")
    assert len(funcs) == 1
    assert funcs[0]["name"] == "snippet"

def test_inference_truncation(monkeypatch):
    # Mock inference to bypass loading heavy model in unit tests
    class MockInference(CVDInference):
        def __init__(self):
            # Bypass super().__init__
            self.threshold = 0.5
            class MockTokenizer:
                def encode(self, text, add_special_tokens):
                    # Mock 600 tokens
                    return [1] * 600
                def build_inputs_with_special_tokens(self, tokens):
                    return [0] + tokens + [2]
            self.tokenizer = MockTokenizer()
            self.device = "cpu"
            class MockModel:
                def __call__(self, input_ids, attention_mask):
                    import torch
                    class Output:
                        logits = torch.tensor([[0.2, 0.8]])
                    return Output()
            self.model = MockModel()

    inferer = MockInference()
    code = "void large_func() { int x = 0; }"
    res = inferer.predict_functions(code)
    
    assert len(res) == 1
    assert res[0]["truncated"] is True
    assert res[0]["label"] == 1
    assert res[0]["probability"] > 0.5