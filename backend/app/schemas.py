from pydantic import BaseModel
from typing import List, Optional

class LineScore(BaseModel):
    line: int
    score: float
    top_tokens: Optional[List[str]] = []
    code: Optional[str] = ""

class FunctionResult(BaseModel):
    name: str
    start_line: int
    end_line: int
    probability: float
    truncated: bool = False
    line_scores: Optional[List[LineScore]] = []

class ModelInfo(BaseModel):
    checkpoint: str
    threshold: float
    training_data: str
    test_f1: float

class AnalyzeRequest(BaseModel):
    code: str
    language: str = "c"

class AnalyzeResponse(BaseModel):
    vulnerable: bool
    overall_confidence: float
    functions: List[FunctionResult]
    model_info: ModelInfo