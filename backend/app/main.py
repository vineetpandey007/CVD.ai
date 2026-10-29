import os
import sys
import threading
import requests
import chromadb
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# --- BULLETPROOF .ENV LOADING ---
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
root_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", ".env"))

load_dotenv(dotenv_path=root_env_path, override=True)
load_dotenv(dotenv_path=env_path, override=True)

# Ensure the 'ml' and 'app' modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.routes import analyze

app = FastAPI(title="CVD NLP Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model state
app.state.cvd_model = None
app.state.model_loaded = False

# Initialize ChromaDB for Semantic Search
app.state.chroma_client = chromadb.PersistentClient(path="./chroma_db")
app.state.vector_collection = app.state.chroma_client.get_or_create_collection(name="scanned_functions")

def load_model_background():
    try:
        print("Loading CodeBERT model in background...")
        from ml.src.inference import CVDInference
        # Loads the best checkpoint and validation threshold
        app.state.cvd_model = CVDInference()
        app.state.model_loaded = True
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=load_model_background)
    thread.start()

app.include_router(analyze.router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "model_loaded": app.state.model_loaded}

# --- NLG Security Audit Report Endpoint ---
class ReportRequest(BaseModel):
    source_code: str
    vulnerability_type: str
    lime_flagged_tokens: list[str]

@app.post("/api/generate-report")
def generate_threat_report(req: ReportRequest):
    load_dotenv(dotenv_path=root_env_path, override=True)
    load_dotenv(dotenv_path=env_path, override=True)

    groq_api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if groq_api_key:
        groq_api_key = groq_api_key.strip().strip('"').strip("'")

    if not groq_api_key or not groq_api_key.startswith("gsk_"):
        raise HTTPException(
            status_code=500,
            detail="Valid GROQ_API_KEY (starting with 'gsk_') not found in backend/.env file."
        )

    system_prompt = (
        "You are a Security Assistant reviewing a flagged C/C++ function. "
        "Do NOT write in paragraphs and do NOT use Markdown symbols like **, *, `, or ```cpp. "
        "Output plain text ONLY under these exact three headers:\n\n"
        "1. THE ISSUE:\n"
        "- Explain the specific syntax flaw in one or two concise bullet points.\n\n"
        "2. THE DANGER:\n"
        "- Explain the security risk in one or two concise bullet points.\n\n"
        "3. THE FIX:\n"
        "- State the solution in one bullet point.\n"
        "- Provide the patched C/C++ code directly below it without code fences."
    )

    user_prompt = (
        f"Detected Issue: {req.vulnerability_type}\n"
        f"LIME High-Weight Tokens: {', '.join(req.lime_flagged_tokens)}\n\n"
        f"Source Code:\n```cpp\n{req.source_code}\n```"
    )

    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    # Current production Free/Developer Tier models on Groq (with automatic fallback)
    candidate_models = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "groq/compound-mini"
    ]

    # Split domain string so clipboard never converts it into a Markdown bracket link
    groq_endpoint = "https://api." + "groq" + ".com/openai/v1/chat/completions"
    last_error = ""

    for model_name in candidate_models:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_completion_tokens": 1024
        }

        try:
            response = requests.post(
                groq_endpoint,
                headers=headers,
                json=payload,
                timeout=20
            )
            if response.status_code == 200:
                result = response.json()
                print(f"\n--- GROQ API SUCCESS ({model_name}) ---\n")
                report_text = result["choices"][0]["message"]["content"]
                if report_text:
                    clean_report = (
                        report_text.replace("```cpp", "")
                        .replace("```c", "")
                        .replace("```", "")
                        .replace("**", "")
                        .replace("`", "'")
                        .strip()
                    )
                    return {"report": clean_report}
            else:
                last_error = response.text
                print(f"Model {model_name} failed ({response.status_code}): {last_error}")
        except Exception as e:
            last_error = str(e)

    raise HTTPException(status_code=500, detail=f"NLG Generation Error: {last_error}")

# --- Semantic Vector Search Endpoint ---
class SemanticSearchRequest(BaseModel):
    source_code: str

@app.post("/api/semantic-search")
def semantic_search(req: SemanticSearchRequest):
    if not app.state.model_loaded:
        raise HTTPException(status_code=503, detail="Model is still loading.")

    try:
        # Generate the 768-dimensional mathematical vector for the pasted code
        query_embedding = app.state.cvd_model.get_embedding(req.source_code)

        # Search ChromaDB for the top 3 most structurally similar functions
        results = app.state.vector_collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )

        # Format the response
        similar_matches = []
        if results and results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                similar_matches.append({
                    "id": results["ids"][0][i],
                    "code": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0
                })

        return {"status": "success", "matches": similar_matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic Search Error: {str(e)}")