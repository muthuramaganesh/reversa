"""
CashGPT — FastAPI Backend Service
Wraps cashgpt_fraud_detection.py model as a REST API.

Train and save the model first:
    python train_and_save.py

Then serve:
    pip install fastapi uvicorn joblib
    uvicorn api:app --host 0.0.0.0 --port 8000

React dashboard connects to this at API_BASE in CashGPTDashboard.jsx
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import joblib
import pandas as pd
import os, time, json

app = FastAPI(title="CashGPT Fraud Detection API", version="1.0.0")

# Allow React dashboard to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load model + artefacts on startup ────────────────────────────────────────
MODEL_PATH  = "cashgpt_stack.pkl"
SHAP_PATH   = "cashgpt_shap.json"
STATS_PATH  = "cashgpt_stats.json"

stack       = None
shap_data   = None
stats_data  = None

@app.on_event("startup")
async def load_model():
    global stack, shap_data, stats_data
    if os.path.exists(MODEL_PATH):
        stack = joblib.load(MODEL_PATH)
        print(f"✓ Model loaded from {MODEL_PATH}")
    else:
        print(f"⚠  {MODEL_PATH} not found — run train_and_save.py first")

    if os.path.exists(SHAP_PATH):
        with open(SHAP_PATH) as f:
            shap_data = json.load(f)

    if os.path.exists(STATS_PATH):
        with open(STATS_PATH) as f:
            stats_data = json.load(f)


# ── Request / Response schemas ────────────────────────────────────────────────
class Transaction(BaseModel):
    tx_id:   Optional[str] = None
    features: List[float]  # length must match FEATURE_COLS

class ScoreRequest(BaseModel):
    transactions: List[Transaction]
    threshold: float = 0.35

class ScoreResult(BaseModel):
    tx_id:      str
    fraud_prob: float
    predicted:  int
    risk:       str

class ScoreResponse(BaseModel):
    results:       List[ScoreResult]
    total:         int
    flagged:       int
    processing_ms: float


# ── Helper ────────────────────────────────────────────────────────────────────
def risk_label(p: float) -> str:
    if p >= 0.75: return "Critical"
    if p >= 0.50: return "High"
    if p >= 0.35: return "Medium"
    return "Low"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"service": "CashGPT Fraud Detection API", "status": "running",
            "model_loaded": stack is not None}


@app.post("/api/score", response_model=ScoreResponse)
def score_transactions(req: ScoreRequest):
    """
    Score a batch of transactions.
    Send feature vectors in the same order as FEATURE_COLS from the training script.
    """
    if stack is None:
        raise HTTPException(503, "Model not loaded — run train_and_save.py")

    t0 = time.perf_counter()
    X  = np.array([t.features for t in req.transactions])
    proba = stack.predict_proba(X)[:, 1]

    results = []
    for i, (tx, p) in enumerate(zip(req.transactions, proba)):
        pred = int(p >= req.threshold)
        results.append(ScoreResult(
            tx_id      = tx.tx_id or f"TXN-{i:05d}",
            fraud_prob = round(float(p), 4),
            predicted  = pred,
            risk       = risk_label(p),
        ))

    ms = (time.perf_counter() - t0) * 1000
    flagged = sum(1 for r in results if r.predicted == 1)

    return ScoreResponse(
        results       = results,
        total         = len(results),
        flagged       = flagged,
        processing_ms = round(ms, 2),
    )


@app.get("/api/stats")
def get_stats():
    """Return model metrics, confusion matrix and risk counts from last evaluation run."""
    if stats_data is None:
        raise HTTPException(404, "Stats not found — run train_and_save.py")
    return stats_data


@app.get("/api/shap")
def get_shap():
    """Return SHAP feature importance from XGBoost base learner."""
    if shap_data is None:
        raise HTTPException(404, "SHAP data not found — run train_and_save.py")
    return shap_data


@app.post("/api/explain/{tx_id}")
def explain_transaction(tx_id: str, features: List[float]):
    """
    Return LIME explanation for a single transaction.
    Pass features as a JSON array in the request body.
    """
    if stack is None:
        raise HTTPException(503, "Model not loaded")
    # LIME is slow — run synchronously for single transaction
    import lime.lime_tabular
    # Note: X_res and FEATURE_COLS must be persisted with the model for LIME
    # Store them via joblib alongside the stacking model (see train_and_save.py)
    return {"tx_id": tx_id, "message": "LIME explanation endpoint — see train_and_save.py for full implementation"}


@app.get("/health")
def health():
    return {"status": "ok", "model": "loaded" if stack else "not loaded"}
