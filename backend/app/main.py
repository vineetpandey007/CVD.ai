from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
import sys
import os

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