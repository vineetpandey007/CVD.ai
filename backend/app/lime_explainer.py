import numpy as np
import torch
from lime.lime_text import LimeTextExplainer

class CVDExplainer:
    def __init__(self, inference_engine):
        self.engine = inference_engine
        self.explainer = LimeTextExplainer(class_names=['Safe', 'Vulnerable'], split_expression=r'\W+')

    def _predict_proba(self, texts):
        self.engine.model.eval()
        probs = []
        batch_size = 8
        
        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i+batch_size]
                inputs = self.engine.tokenizer(
                    batch_texts, padding=True, truncation=True, max_length=512, return_tensors="pt"
                )
                inputs = {k: v.to(self.engine.device) for k, v in inputs.items()}
                logits = self.engine.model(**inputs).logits
                batch_probs = torch.nn.functional.softmax(logits, dim=-1).cpu().numpy()
                probs.extend(batch_probs)
                
        return np.array(probs)

    def explain(self, code_snippet, start_line):
        exp = self.explainer.explain_instance(code_snippet, self._predict_proba, num_features=10, num_samples=50)
        vuln_tokens = {token: weight for token, weight in exp.as_list() if weight > 0}
        
        lines = code_snippet.split('\n')
        line_scores = []
        
        for idx, line in enumerate(lines):
            score = 0.0
            top_tokens = []
            for token, weight in vuln_tokens.items():
                if token in line:
                    score += weight
                    top_tokens.append(token)
            
            if score > 0:
                line_scores.append({
                    "line": start_line + idx,
                    "score": float(score),
                    "top_tokens": top_tokens[:4]
                })
                
        return sorted(line_scores, key=lambda x: x["score"], reverse=True)