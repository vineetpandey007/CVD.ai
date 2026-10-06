from fastapi import APIRouter, HTTPException, Request
from starlette.concurrency import run_in_threadpool
import json
import os

from app.schemas import AnalyzeRequest, AnalyzeResponse, FunctionResult, ModelInfo

router = APIRouter()

def get_comparison_data():
    comp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml/results/comparison.json"))
    if os.path.exists(comp_path):
        with open(comp_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(request: Request, payload: AnalyzeRequest):
    # 1. 503 if model is missing or still booting
    if not request.app.state.model_loaded or not request.app.state.cvd_model:
        raise HTTPException(status_code=503, detail="Model is still loading or failed to load. Please try again in a few seconds.")
    
    # 2. 422 if language is unsupported
    if payload.language.lower() not in ["c", "cpp"]:
        raise HTTPException(status_code=422, detail="The NLP model only supports C and C++ source code.")

    model = request.app.state.cvd_model

    # 3. Threaded inference
    results = await run_in_threadpool(model.predict_functions, payload.code, payload.language.lower())
    
    functions = []
    max_prob = 0.0
    is_vulnerable = False

    for res in results:
        prob = res["probability"]
        max_prob = max(max_prob, prob)
        if prob >= model.threshold:
            is_vulnerable = True
            
        functions.append(FunctionResult(
            name=res["name"],
            start_line=res["start_line"],
            end_line=res["end_line"],
            probability=prob,
            truncated=res["truncated"]
        ))

    # 4. Read test F1 dynamically from JSON
    comp_data = get_comparison_data()
    test_f1 = 0.0
    for row in comp_data.get("comparison", []):
        if row.get("model") == "Fine-tuned CodeBERT":
            test_f1 = row.get("f1", 0.0)

    model_info = ModelInfo(
        checkpoint="CodeBERT (Epoch 3)",
        threshold=model.threshold,
        training_data="Devign (CodeXGLUE)",
        test_f1=test_f1
    )

    return AnalyzeResponse(
        vulnerable=is_vulnerable,
        overall_confidence=max_prob,
        functions=functions,
        model_info=model_info
    )

@router.get("/model-card")
async def get_model_card():
    comp_data = get_comparison_data()
    return {
        "metrics": comp_data.get("comparison", []),
        "bootstrap_ci": comp_data.get("bootstrap_ci", {}),
        "limitations": [
            "Trained exclusively on C/C++ (Devign dataset).",
            "Functions exceeding 512 tokens are truncated.",
            "Probabilistic model; not a guarantee of security."
        ]
    }