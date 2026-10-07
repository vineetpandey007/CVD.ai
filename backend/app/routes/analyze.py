from fastapi import APIRouter, HTTPException, Request
from starlette.concurrency import run_in_threadpool
import json
import os

from app.schemas import AnalyzeRequest, AnalyzeResponse, FunctionResult, ModelInfo
from app.lime_explainer import CVDExplainer

router = APIRouter()

def get_comparison_data():
    comp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml/results/comparison.json"))
    if os.path.exists(comp_path):
        with open(comp_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(request: Request, payload: AnalyzeRequest):
    if not request.app.state.model_loaded or not request.app.state.cvd_model:
        raise HTTPException(status_code=503, detail="Model is loading. Try again.")
    
    if payload.language.lower() not in ["c", "cpp"]:
        raise HTTPException(status_code=422, detail="Only C/C++ supported.")

    model = request.app.state.cvd_model
    results = await run_in_threadpool(model.predict_functions, payload.code, payload.language.lower())
    
    functions = []
    max_prob = 0.0
    is_vulnerable = False
    
    explainer = CVDExplainer(model)
    code_lines = payload.code.split('\n')

    for res in results:
        prob = res["probability"]
        max_prob = max(max_prob, prob)
        line_scores = []
        
        if prob >= model.threshold:
            is_vulnerable = True
            fn_code = "\n".join(code_lines[res["start_line"]-1 : res["end_line"]])
            line_scores = await run_in_threadpool(explainer.explain, fn_code, res["start_line"])
            
        functions.append(FunctionResult(
            name=res["name"],
            start_line=res["start_line"],
            end_line=res["end_line"],
            probability=prob,
            truncated=res["truncated"],
            line_scores=line_scores
        ))

    comp_data = get_comparison_data()
    test_f1 = next((row.get("f1", 0.0) for row in comp_data.get("comparison", []) if row.get("model") == "Fine-tuned CodeBERT"), 0.0)

    return AnalyzeResponse(
        vulnerable=is_vulnerable,
        overall_confidence=max_prob,
        functions=functions,
        model_info=ModelInfo(checkpoint="CodeBERT (Epoch 3)", threshold=model.threshold, training_data="Devign", test_f1=test_f1)
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