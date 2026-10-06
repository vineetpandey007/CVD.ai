import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import glob
import os
from .ast_slicer import get_functions

class CVDInference:
    def __init__(self, checkpoint_path=None, threshold=0.5):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Auto-detect best checkpoint if none provided
        if not checkpoint_path:
            checkpoints = glob.glob("ml/checkpoints/best_codebert/*")
            if not checkpoints:
                raise FileNotFoundError("No checkpoint found in ml/checkpoints/best_codebert/")
            checkpoint_path = checkpoints[0]
            
        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path).to(self.device)
        self.model.eval()
        self.threshold = threshold

    def predict_functions(self, code: str, language: str = "c"):
        funcs = get_functions(code, language)
        results = []
        
        with torch.no_grad():
            for f in funcs:
                # Tokenize without special tokens to handle custom truncation
                raw_tokens = self.tokenizer.encode(f["code"], add_special_tokens=False)
                truncated = False
                
                # Head + Tail Truncation for > 510 tokens (leaves 2 slots for <s> and </s>)
                if len(raw_tokens) > 510:
                    truncated = True
                    raw_tokens = raw_tokens[:384] + raw_tokens[-(510-384):]
                
                # Rebuild with specials and tensorize
                input_ids = self.tokenizer.build_inputs_with_special_tokens(raw_tokens)
                input_tensor = torch.tensor([input_ids]).to(self.device)
                attention_mask = torch.ones_like(input_tensor).to(self.device)

                outputs = self.model(input_ids=input_tensor, attention_mask=attention_mask)
                prob = float(torch.softmax(outputs.logits, dim=1)[0][1].item())
                
                results.append({
                    "name": f["name"],
                    "start_line": f["start_line"],
                    "end_line": f["end_line"],
                    "probability": prob,
                    "label": 1 if prob >= self.threshold else 0,
                    "truncated": truncated
                })
                
        return results