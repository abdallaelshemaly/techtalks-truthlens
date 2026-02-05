from fastapi import FastAPI, UploadFile, File, HTTPException
import sqlite3
import uuid
from datetime import datetime, timezone
import os

# Task 2 import
from src.cnn.loader import predict_image

app = FastAPI()

os.makedirs("uploads", exist_ok=True)

db = sqlite3.connect("truthlens.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS analyses(
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    cnn_confidence REAL NOT NULL,
    cnn_prediction TEXT,
    ela_score REAL,
    copy_move_score REAL,
    metadata_score REAL,
    overall_risk_score REAL,
    risk_level TEXT,
    created_at TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS batch(
    id TEXT PRIMARY KEY,
    total_images INTEGER,
    processed_images INTEGER,
    status TEXT,
    results_summary JSON
)
""")

db.commit()


# Existing endpoint (kept)
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    analysisId = str(uuid.uuid4())
    FilePath = f"uploads/{analysisId}.jpg"

    content = await file.read()
    with open(FilePath, "wb") as f:
        f.write(content)

    cnn_confidence = 0.0
    cnn_prediction = "unknown"
    ela_score = None
    copy_move_score = None
    metadata_score = None
    overall_risk_score = 0.0
    risk_level = "LOW"

    cursor.execute("""
        INSERT INTO analyses(
            id, filename, cnn_confidence, cnn_prediction,
            ela_score, copy_move_score, metadata_score,
            overall_risk_score, risk_level, created_at
        )
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        analysisId,
        FilePath,
        cnn_confidence,
        cnn_prediction,
        ela_score,
        copy_move_score,
        metadata_score,
        overall_risk_score,
        risk_level,
        datetime.now(timezone.utc).isoformat()
    ))

    db.commit()

    return {
        "id": analysisId,
        "filename": FilePath,
        "risk_level": risk_level,
        "overall_risk_score": overall_risk_score
    }


# Task 2 endpoint
@app.post("/api/analyze/cnn")
async def analyze_cnn(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Upload jpg/png/webp images only")

    analysisId = str(uuid.uuid4())

    # ✅ FIX: correct file extension for each content type
    ext_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    ext = ext_map[file.content_type]

    FilePath = f"uploads/{analysisId}{ext}"

    content = await file.read()
    with open(FilePath, "wb") as f:
        f.write(content)

    # prediction + confidence (0-100)
    prediction, confidence = predict_image(FilePath)

    # store results
    cursor.execute("""
        INSERT INTO analyses(
            id, filename, cnn_confidence, cnn_prediction,
            ela_score, copy_move_score, metadata_score,
            overall_risk_score, risk_level, created_at
        )
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        analysisId,
        FilePath,
        confidence,
        prediction,
        None,
        None,
        None,
        confidence,  # simple overall score for now
        "HIGH" if prediction == "FAKE" else "LOW",
        datetime.now(timezone.utc).isoformat()
    ))
    db.commit()

    return {
        "id": analysisId,
        "filename": FilePath,
        "prediction": prediction,
        "confidence": confidence
    }
