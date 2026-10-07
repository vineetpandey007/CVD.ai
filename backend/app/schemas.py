from pydantic import BaseModel
from typing import List, Optional

class AnalyzeRequest(BaseModel):
    code: str
    language: str

class LineScore(BaseModel):
    line: int
    score: float
    top_tokens: List[str]

class FunctionResult(BaseModel):
    name: str
    start_line: int
    end_line: int
    probability: float
    truncated: bool
    line_scores: Optional[List[LineScore]] = []

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