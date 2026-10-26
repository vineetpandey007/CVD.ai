import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import glob
import os
from .ast_slicer import get_functions

class CVDInference:
    def __init__(self, checkpoint_path=None, threshold=0.5):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
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
                code_lines = f["code"].strip().split('\n')
                
                # Context Filter: Prevent AI hallucinations on tiny toy functions
                if len(code_lines) <= 4 and "strcpy" not in f["code"]:
                    prob = 0.05 # Flag as Safe automatically
                    truncated = False
                else:
                    raw_tokens = self.tokenizer.encode(f["code"], add_special_tokens=False)
                    truncated = False
                    
                    if len(raw_tokens) > 510:
                        truncated = True
                        raw_tokens = raw_tokens[:384] + raw_tokens[-(510-384):]
                    
                    input_ids = self.tokenizer.build_inputs_with_special_tokens(raw_tokens)
                    input_tensor = torch.tensor([input_ids]).to(self.device)
                    attention_mask = torch.ones_like(input_tensor).to(self.device)

                    outputs = self.model(input_ids=input_tensor, attention_mask=attention_mask)
                    
                    # Reverted to [0][1] (Class 1 is Vulnerable)
                    prob = float(torch.softmax(outputs.logits, dim=1)[0][1].item())
                    
                    # --- HYBRID HEURISTIC POST-PROCESSING ---
                    # Reduce false positives for known safe bounding functions/types
                    if "snprintf" in f["code"] and "strcpy" not in f["code"] and "strcat" not in f["code"]:
                        prob = prob * 0.1  # Slash the probability by 90%
                    if "std::string" in f["code"] or "std::vector" in f["code"]:
                        prob = prob * 0.2  # Modern C++ containers handle memory safely

                results.append({
                    "name": f["name"],
                    "start_line": f["start_line"],
                    "end_line": f["end_line"],
                    "probability": prob,
                    "label": 1 if prob >= self.threshold else 0,
                    "truncated": truncated
                })
                
        return results

    def get_embedding(self, source_code: str) -> list[float]:
        """
        Extracts the 768-dimensional [CLS] token embedding from CodeBERT 
        to use for semantic vector search in ChromaDB.
        """
        # Tokenize the input code
        inputs = self.tokenizer(
            source_code, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512, 
            padding="max_length"
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Pass through CodeBERT without computing gradients
        with torch.no_grad():
            # Ensure output_hidden_states is True to access the raw embeddings
            outputs = self.model(**inputs, output_hidden_states=True)
            
        # Extract the [CLS] token embedding from the last hidden state
        # Shape: (batch_size, sequence_length, hidden_size). [CLS] is at index 0.
        cls_embedding = outputs.hidden_states[-1][0, 0, :].cpu().numpy().tolist()
        
        return cls_embedding