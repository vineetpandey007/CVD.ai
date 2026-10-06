from pydantic import BaseModel, Field
from typing import List, Optional

class AnalyzeRequest(BaseModel):
    code: str = Field(..., max_length=50000)
    language: str
    explain: bool = False

class FunctionResult(BaseModel):
    name: str
    start_line: int
    end_line: int
    probability: float
    truncated: bool
    # We leave room for line attributions in Module 9
    line_scores: Optional[List[dict]] = None 

class ModelInfo(BaseModel):
    checkpoint: str
    threshold: float
    training_data: str
    test_f1: float

class AnalyzeResponse(BaseModel):
    vulnerable: bool
    overall_confidence: float
    functions: List[FunctionResult]
    model_info: ModelInfo