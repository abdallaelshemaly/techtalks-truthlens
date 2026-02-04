from fastapi import FastAPI, HTTPException
import os
from datetime import datetime

# Import database helpers
from database import get_analysis_by_id, log_analysis

# Import analysis functions (MUST already exist in your project)
from ela_analyzer import analyze_single_image
from cnn_model import predict_image
from copy_move import detect_copy_move
from metadata_analyzer import analyze_metadata

app = FastAPI()


@app.post("/api/analyze/complete")
def analyze_complete(analysis_id: int):

    # 1. Get analysis record from DB
    record = get_analysis_by_id(analysis_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Analysis ID not found")

    file_path = record["file_path"] if record["file_path"] else record["filename"]

    # 2. Check image exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image file not found")

    # 3. CNN prediction
    is_fake, cnn_confidence = predict_image(file_path)

    # 4. ELA analysis
    ela_result = analyze_single_image(file_path)
    ela_score = ela_result["ela_score"]

    # 5. Copy-move detection
    copy_move_score = detect_copy_move(file_path)

    # 6. Metadata analysis
    metadata_score = analyze_metadata(file_path)

    # 7. Compute overall risk score
    overall_risk_score = (
        cnn_confidence * 0.4 +
        ela_score * 0.3 +
        copy_move_score * 0.2 +
        metadata_score * 0.1
    )

    # 8. Risk level
    if overall_risk_score < 30:
        risk_level = "LOW"
    elif overall_risk_score < 70:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    # 9. Store result in DB
    log_analysis({
        "filename": record["filename"],
        "is_fake": is_fake,
        "cnn_confidence": cnn_confidence,
        "ela_score": ela_score,
        "metadata_score": metadata_score,
        "copy_move_score": copy_move_score,
        "risk_level": risk_level,
        "file_path": file_path,
        "report_path": ""
    })

    # 10. Return result
    return {
        "id": analysis_id,
        "filename": record["filename"],
        "risk_level": risk_level,
        "overall_risk_score": round(overall_risk_score, 2)
    }