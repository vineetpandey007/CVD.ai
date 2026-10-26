from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from starlette.concurrency import run_in_threadpool
import json
import os
import zipfile
import io
import re
import hashlib

os.environ["TOKENIZERS_PARALLELISM"] = "false"

from app.schemas import AnalyzeRequest, AnalyzeResponse, FunctionResult, ModelInfo
from app.lime_explainer import CVDExplainer
from app.db import record_scan, list_scans, get_scan

router = APIRouter()

def strip_c_comments(code: str) -> str:
    pattern = re.compile(
        r'(?P<string>"(?:\\.|[^\\"])*")|'
        r"(?P<char>'(?:\\.|[^\\'])*')|"
        r'(?P<comment>/\*.*?\*/|//[^\r\n]*)',
        re.DOTALL
    )
    def replacer(match):
        if match.group('comment'):
            return "\n" * match.group('comment').count('\n')
        return match.group(0)
    
    return re.sub(pattern, replacer, code)

def get_comparison_data():
    comp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml/results/comparison.json"))
    if os.path.exists(comp_path):
        with open(comp_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def store_function_vector(request: Request, name: str, code: str, probability: float, threshold: float):
    """Helper function to store function embeddings into ChromaDB."""
    try:
        if not hasattr(request.app.state, "vector_collection") or not request.app.state.vector_collection:
            return
        
        # Extract 768-dim CodeBERT vector
        embedding = request.app.state.cvd_model.get_embedding(code)
        
        # Generate a deterministic unique ID based on function name and code hash
        func_hash = hashlib.sha256(code.encode('utf-8')).hexdigest()[:12]
        doc_id = f"{name}_{func_hash}"

        request.app.state.vector_collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[code],
            metadatas=[{
                "function_name": name,
                "probability": float(probability),
                "is_vulnerable": bool(probability >= threshold)
            }]
        )
    except Exception as e:
        print(f"Warning: ChromaDB vector upsert failed for {name}: {e}")

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(request: Request, payload: AnalyzeRequest):
    if not request.app.state.model_loaded or not request.app.state.cvd_model:
        raise HTTPException(status_code=503, detail="Model is loading. Try again.")
    
    clean_code = strip_c_comments(payload.code)
    model = request.app.state.cvd_model
    results = await run_in_threadpool(model.predict_functions, clean_code, payload.language.lower())
    
    functions = []
    max_prob = 0.0
    is_vulnerable = False
    explainer = CVDExplainer(model)
    code_lines = clean_code.split('\n')

    for res in results:
        prob = res["probability"]
        max_prob = max(max_prob, prob)
        line_scores = []
        fn_code = "\n".join(code_lines[res["start_line"]-1 : res["end_line"]])
        
        if prob >= model.threshold:
            is_vulnerable = True
            line_scores = await run_in_threadpool(explainer.explain, fn_code, res["start_line"])
            
        functions.append(FunctionResult(
            name=res["name"],
            start_line=res["start_line"],
            end_line=res["end_line"],
            probability=prob,
            truncated=res["truncated"],
            line_scores=line_scores
        ))

        # Store in ChromaDB vector repository
        if fn_code.strip():
            await run_in_threadpool(
                store_function_vector,
                request,
                res["name"],
                fn_code,
                prob,
                model.threshold
            )

    comp_data = get_comparison_data()
    test_f1 = next((row.get("f1", 0.0) for row in comp_data.get("comparison", []) if row.get("model") == "Fine-tuned CodeBERT"), 0.0)

    response = AnalyzeResponse(
        vulnerable=is_vulnerable,
        overall_confidence=max_prob,
        functions=functions,
        model_info=ModelInfo(checkpoint="CodeBERT", threshold=model.threshold, training_data="Devign", test_f1=test_f1)
    )

    # Persist in DuckDB
    try:
        record_scan(scan_type="snippet", target_name=f"Snippet ({payload.language.upper()})", response_data=response.dict())
    except Exception as e:
        print(f"Warning: DuckDB save failed: {e}")

    return response

@router.post("/analyze-bulk", response_model=AnalyzeResponse)
async def analyze_bulk(request: Request, file: UploadFile = File(...)):
    if not request.app.state.model_loaded or not request.app.state.cvd_model:
        raise HTTPException(status_code=503, detail="Model is loading. Try again.")

    print(f"\n Received Bulk Upload: {file.filename}")
    model = request.app.state.cvd_model
    explainer = CVDExplainer(model)
    
    all_functions = []
    max_prob = 0.0
    is_vulnerable = False
    contents = await file.read()
    
    try:
        with zipfile.ZipFile(io.BytesIO(contents)) as zip_ref:
            c_cpp_files = [name for name in zip_ref.namelist() if name.endswith(('.c', '.cpp', '.h', '.hpp'))]
            print(f" Found {len(c_cpp_files)} C/C++ files to audit.")

            for filename in c_cpp_files:
                print(f" Scanning file: {filename}...")
                with zip_ref.open(filename) as f:
                    try:
                        code_bytes = f.read()
                        code_text = code_bytes.decode('utf-8') 
                        clean_code = strip_c_comments(code_text)
                    except UnicodeDecodeError:
                        continue
                        
                lang = "cpp" if filename.endswith(('.cpp', '.hpp')) else "c"
                results = await run_in_threadpool(model.predict_functions, clean_code, lang)
                code_lines = clean_code.split('\n')

                for res in results:
                    prob = res["probability"]
                    max_prob = max(max_prob, prob)
                    line_scores = []
                    fn_code = "\n".join(code_lines[res["start_line"]-1 : res["end_line"]])
                    
                    if prob >= model.threshold:
                        is_vulnerable = True
                        if len(all_functions) < 15: 
                            line_scores = await run_in_threadpool(explainer.explain, fn_code, res["start_line"])
                        
                    display_name = f"{filename} -> {res['name']}"
                    all_functions.append(FunctionResult(
                        name=display_name,
                        start_line=res["start_line"],
                        end_line=res["end_line"],
                        probability=prob,
                        truncated=res["truncated"],
                        line_scores=line_scores
                    ))

                    # Store in ChromaDB vector repository
                    if fn_code.strip():
                        await run_in_threadpool(
                            store_function_vector,
                            request,
                            display_name,
                            fn_code,
                            prob,
                            model.threshold
                        )

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid or corrupted ZIP file.")

    comp_data = get_comparison_data()
    test_f1 = next((row.get("f1", 0.0) for row in comp_data.get("comparison", []) if row.get("model") == "Fine-tuned CodeBERT"), 0.0)

    all_functions.sort(key=lambda x: x.probability, reverse=True)

    response = AnalyzeResponse(
        vulnerable=is_vulnerable,
        overall_confidence=max_prob,
        functions=all_functions,
        model_info=ModelInfo(checkpoint="CodeBERT", threshold=model.threshold, training_data="Devign", test_f1=test_f1)
    )

    # Persist in DuckDB
    try:
        record_scan(scan_type="repository", target_name=file.filename or "repository.zip", response_data=response.dict())
    except Exception as e:
        print(f"Warning: DuckDB save failed: {e}")

    return response

@router.get("/history")
async def get_history():
    return list_scans()

@router.get("/history/{scan_id}")
async def get_history_detail(scan_id: str):
    data = get_scan(scan_id)
    if not data:
        raise HTTPException(status_code=404, detail="Scan record not found.")
    return data

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