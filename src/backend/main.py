"""
FastAPI Backend for TruthLens with enhanced report generation
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
import sqlite3
from datetime import datetime, timezone
import sys
import traceback
from evaluation_routes import router as evaluation_router

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Try to import project modules
try:
    from src.cnn.loader import predict_image
    CNN_AVAILABLE = True
except ImportError:
    print("⚠️  CNN module not available, using dummy predictions")
    CNN_AVAILABLE = False

try:
    from src.forensics.forensics import run_full_forensic_analysis
    FORENSICS_AVAILABLE = True
except ImportError:
    print("⚠️  Forensics module not available")
    FORENSICS_AVAILABLE = False

# Try to import enhanced forensics
try:
    from src.forensics.forensics import run_enhanced_forensic_analysis
    ENHANCED_FORENSICS_AVAILABLE = True
except ImportError:
    ENHANCED_FORENSICS_AVAILABLE = False
    print("⚠️  Enhanced forensics module not available")

# Try to import advanced report generator
try:
    from src.advanced.report_generator import TruthLensReportGenerator
    REPORT_GEN_AVAILABLE = True
    print("✅ Advanced report generator available")
except ImportError:
    REPORT_GEN_AVAILABLE = False
    print("⚠️  Advanced report generator not available")

app = FastAPI(title="TruthLens API", description="Deepfake Detection System")

app.include_router(evaluation_router)

# Allow CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = CURRENT_FILE_DIR 
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_FILE_DIR)) 

UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")
ELA_DIR = os.path.join(UPLOAD_DIR, "ela_samples")
ELA_OVERLAY_DIR = os.path.join(UPLOAD_DIR, "ela_overlays")
COPY_MOVE_VISUAL_DIR = os.path.join(UPLOAD_DIR, "cm_visuals")
REPORTS_DIR = os.path.join(BACKEND_DIR, "reports")  
EVALUATION_DIR = os.path.join(BACKEND_DIR, "evaluation") 

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ELA_DIR, exist_ok=True)
os.makedirs(ELA_OVERLAY_DIR, exist_ok=True)
os.makedirs(COPY_MOVE_VISUAL_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(EVALUATION_DIR, exist_ok=True)
os.makedirs(os.path.join(EVALUATION_DIR, "results"), exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")
app.mount("/evaluation", StaticFiles(directory=EVALUATION_DIR), name="evaluation")

DB_PATH = os.path.join(BACKEND_DIR, "truthlens.db") 

def init_db():
    """Initialize database on startup"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Main analyses table with enhanced fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_fake BOOLEAN,
            cnn_confidence REAL,
            ela_score REAL,
            ela_enhanced_score REAL,
            metadata_score REAL,
            copy_move_score REAL,
            copy_move_enhanced_score REAL,
            risk_level TEXT,
            enhanced_risk_level TEXT,
            ela_overlay_url TEXT,
            copy_move_visual_url TEXT,
            report_path TEXT,
            file_path TEXT
        )
    ''')
    
    # Batch analyses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS batch (
            id TEXT PRIMARY KEY,
            total_images INTEGER,
            processed_images INTEGER,
            status TEXT,
            results_summary TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized with enhanced fields")

def log_analysis(data):
    """Insert analysis into database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO analyses 
        (filename, is_fake, cnn_confidence, ela_score, ela_enhanced_score, 
         metadata_score, copy_move_score, copy_move_enhanced_score,
         risk_level, enhanced_risk_level, ela_overlay_url, 
         copy_move_visual_url, report_path, file_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("filename", "unknown"),
        data.get("is_fake", False),
        data.get("cnn_confidence", 0.0),
        data.get("ela_score", 0.0),
        data.get("ela_enhanced_score", data.get("ela_score", 0.0)),
        data.get("metadata_score", 0.0),
        data.get("copy_move_score", 0.0),
        data.get("copy_move_enhanced_score", data.get("copy_move_score", 0.0)),
        data.get("risk_level", "Pending"),
        data.get("enhanced_risk_level", data.get("risk_level", "Pending")),
        data.get("ela_overlay_url", ""),
        data.get("copy_move_visual_url", ""),
        data.get("report_path", ""),
        data.get("file_path", "")
    ))
    
    conn.commit()
    analysis_id = cursor.lastrowid
    conn.close()
    return analysis_id

def get_history(limit=20):
    """Get analysis history from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM analyses ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    history = []
    for row in rows:
        history.append({
            "id": row[0],
            "filename": row[1],
            "timestamp": row[2],
            "is_fake": bool(row[3]),
            "cnn_confidence": row[4],
            "ela_score": row[5],
            "ela_enhanced_score": row[6],
            "metadata_score": row[7],
            "copy_move_score": row[8],
            "copy_move_enhanced_score": row[9],
            "risk_level": row[10],
            "enhanced_risk_level": row[11],
            "ela_overlay_url": row[12],
            "copy_move_visual_url": row[13],
            "report_path": row[14]
        })
    
    return history

# ---------- Startup ----------
@app.on_event("startup")
def startup_event():
    """Initialize on startup"""
    print("🚀 Starting TruthLens Backend...")
    print(f"   - CNN Available: {CNN_AVAILABLE}")
    print(f"   - Forensics Available: {FORENSICS_AVAILABLE}")
    print(f"   - Enhanced Forensics: {ENHANCED_FORENSICS_AVAILABLE}")
    print(f"   - Advanced Reports: {REPORT_GEN_AVAILABLE}")
    init_db()
    print("✅ Backend ready!")

# ---------- Health Check ----------
@app.get("/")
async def root():
    return {"message": "TruthLens API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ---------- Upload Endpoint ----------
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Simple upload endpoint - saves file and returns ID."""
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        original_name = file.filename or "unknown.jpg"
        filename = f"{file_id}_{original_name}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create initial database record
        analysis_data = {
            "filename": original_name,
            "file_path": file_path,
            "is_fake": False,
            "cnn_confidence": 0.0,
            "ela_score": 0.0,
            "ela_enhanced_score": 0.0,
            "metadata_score": 0.0,
            "copy_move_score": 0.0,
            "copy_move_enhanced_score": 0.0,
            "risk_level": "Pending",
            "enhanced_risk_level": "Pending",
            "ela_overlay_url": "",
            "copy_move_visual_url": "",
            "report_path": ""
        }
        
        analysis_id = log_analysis(analysis_data)
        
        return JSONResponse(content={
            "status": "success",
            "message": "File uploaded successfully",
            "id": analysis_id,
            "filename": original_name,
            "file_path": file_path
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ---------- Enhanced Forensics Analysis ----------
@app.post("/api/analyze/enhanced-forensics")
async def enhanced_forensics(file: UploadFile = File(...)):
    """Enhanced forensic analysis with visualizations"""
    try:
        print(f"📤 Enhanced forensics for: {file.filename}")
        
        # Save uploaded file
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{file_timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"✅ File saved: {file_path}")
        
        # Run enhanced forensic analysis
        start_time = datetime.now()
        
        if ENHANCED_FORENSICS_AVAILABLE:
            try:
                results = run_enhanced_forensic_analysis(file_path)
                print(f"🔍 Enhanced forensics: ELA={results.get('ela_enhanced_score')}, CM={results.get('copy_move_enhanced_score')}")
            except Exception as e:
                print(f"⚠️  Enhanced forensics error: {e}")
                # Fallback to regular forensics
                results = run_full_forensic_analysis(file_path)
                results["ela_enhanced_score"] = results["ela_score"]
                results["copy_move_enhanced_score"] = results["copy_move_score"]
                results["enhanced_risk_level"] = results["risk_level"]
                results["ela_overlay_url"] = ""
                results["copy_move_visual_url"] = ""
        else:
            # Fallback to regular forensics
            results = run_full_forensic_analysis(file_path)
            results["ela_enhanced_score"] = results["ela_score"]
            results["copy_move_enhanced_score"] = results["copy_move_score"]
            results["enhanced_risk_level"] = results["risk_level"]
            results["ela_overlay_url"] = ""
            results["copy_move_visual_url"] = ""
            print("⚠️  Using regular forensics (enhanced not available)")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Prepare response data
        response_data = {
            "status": "success",
            "result": {
                **results,
                "processing_time": round(processing_time, 2)
            }
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        print(f"❌ Enhanced forensics error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Enhanced forensics failed: {str(e)}")

# ---------- Complete Analysis ----------
@app.post("/api/analyze/complete")
async def analyze_complete(file: UploadFile = File(...)):
    """Complete analysis: CNN + Forensics + Database + Enhanced Reports"""
    try:
        print(f"📤 Received file: {file.filename}")
        
        # 1. Save uploaded file
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{file_timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"✅ File saved: {file_path}")
        
        # 2. CNN Prediction
        start_time = datetime.now()
        if CNN_AVAILABLE:
            try:
                cnn_prediction, cnn_confidence = predict_image(file_path)
                is_fake = cnn_prediction == "FAKE"
                print(f"🤖 CNN: {cnn_prediction} ({cnn_confidence}%)")
            except Exception as e:
                print(f"⚠️  CNN error: {e}")
                # Fallback to dummy
                cnn_confidence = 75.0
                is_fake = True
        else:
            # Dummy data for testing
            cnn_confidence = 85.5
            is_fake = True
            print("⚠️  Using dummy CNN data")
        
        # 3. Forensic Analysis (try enhanced first)
        if ENHANCED_FORENSICS_AVAILABLE:
            try:
                forensic_results = run_enhanced_forensic_analysis(file_path)
                ela_score = forensic_results.get("ela_score", 0.0)
                ela_enhanced = forensic_results.get("ela_enhanced_score", ela_score)
                metadata_score = forensic_results.get("metadata_score", 0.0)
                copy_move_score = forensic_results.get("copy_move_score", 0.0)
                copy_move_enhanced = forensic_results.get("copy_move_enhanced_score", copy_move_score)
                forensic_combined = forensic_results.get("enhanced_combined_risk", forensic_results.get("combined_risk", 0.0))
                ela_overlay_url = forensic_results.get("ela_overlay_url", "")
                copy_move_visual_url = forensic_results.get("copy_move_visual_url", "")
                risk_level = forensic_results.get("enhanced_risk_level", forensic_results.get("risk_level", "UNKNOWN"))
                print(f"🔍 Enhanced Forensics: ELA={ela_enhanced}, CM={copy_move_enhanced}")
            except Exception as e:
                print(f"⚠️  Enhanced forensics error, falling back: {e}")
                forensic_results = run_full_forensic_analysis(file_path)
                ela_score = forensic_results.get("ela_score", 0.0)
                ela_enhanced = ela_score
                metadata_score = forensic_results.get("metadata_score", 0.0)
                copy_move_score = forensic_results.get("copy_move_score", 0.0)
                copy_move_enhanced = copy_move_score
                forensic_combined = forensic_results.get("combined_risk", 0.0)
                ela_overlay_url = ""
                copy_move_visual_url = ""
                risk_level = forensic_results.get("risk_level", "UNKNOWN")
        elif FORENSICS_AVAILABLE:
            try:
                forensic_results = run_full_forensic_analysis(file_path)
                ela_score = forensic_results.get("ela_score", 0.0)
                ela_enhanced = ela_score
                metadata_score = forensic_results.get("metadata_score", 0.0)
                copy_move_score = forensic_results.get("copy_move_score", 0.0)
                copy_move_enhanced = copy_move_score
                forensic_combined = forensic_results.get("combined_risk", 0.0)
                ela_overlay_url = ""
                copy_move_visual_url = ""
                risk_level = forensic_results.get("risk_level", "UNKNOWN")
                print(f"🔍 Forensics: ELA={ela_score}, Meta={metadata_score}, Copy={copy_move_score}")
            except Exception as e:
                print(f"⚠️  Forensics error: {e}")
                ela_score = 65.0
                ela_enhanced = ela_score
                metadata_score = 45.0
                copy_move_score = 25.0
                copy_move_enhanced = copy_move_score
                forensic_combined = 45.0
                ela_overlay_url = ""
                copy_move_visual_url = ""
                risk_level = "UNKNOWN"
        else:
            # Dummy data for testing
            ela_score = 72.5
            ela_enhanced = ela_score
            metadata_score = 38.0
            copy_move_score = 15.0
            copy_move_enhanced = copy_move_score
            forensic_combined = 42.0
            ela_overlay_url = ""
            copy_move_visual_url = ""
            risk_level = "MEDIUM"
            print("⚠️  Using dummy forensic data")
        
        # 4. Calculate Overall Risk
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if is_fake:
            overall_risk = (forensic_combined * 0.5) + (cnn_confidence * 0.5)
        else:
            overall_risk = forensic_combined
        
        # Clamp to 0-100
        overall_risk = max(0, min(100, overall_risk))
        
        # 5. Determine Risk Level
        if overall_risk >= 70:
            final_risk_level = "HIGH"
        elif overall_risk >= 40:
            final_risk_level = "MEDIUM"
        else:
            final_risk_level = "LOW"
        
        # 6. Prepare Analysis Data
        analysis_data = {
            "filename": file.filename,
            "is_fake": is_fake,
            "cnn_confidence": round(cnn_confidence, 2),
            "ela_score": round(ela_score, 2),
            "ela_enhanced_score": round(ela_enhanced, 2),
            "metadata_score": round(metadata_score, 2),
            "copy_move_score": round(copy_move_score, 2),
            "copy_move_enhanced_score": round(copy_move_enhanced, 2),
            "risk_level": final_risk_level,
            "enhanced_risk_level": risk_level,
            "ela_overlay_url": ela_overlay_url,
            "copy_move_visual_url": copy_move_visual_url,
            "report_path": "",
            "file_path": file_path,
            "processing_time": round(processing_time, 2)
        }
        
        # 7. Save to Database
        analysis_id = log_analysis(analysis_data)
        print(f"💾 Saved to DB with ID: {analysis_id}")
        
        # 8. Generate Enhanced Reports
        report_path = ""
        report_url = ""
        
        if REPORT_GEN_AVAILABLE:
            try:
                # Add analysis_id to data
                analysis_data["id"] = analysis_id
                analysis_data["analysis_id"] = f"report_{analysis_id}_{file_timestamp}"
                analysis_data["timestamp"] = datetime.now().isoformat()
                
                # Generate enhanced reports
                generator = TruthLensReportGenerator(REPORTS_DIR)
                reports = generator.generate_backend_report(analysis_data, "html")
                
                if "html" in reports:
                    report_path = reports["html"]
                    report_filename = os.path.basename(report_path)
                    report_url = f"/reports/{report_filename}"
                    print(f"📄 Enhanced HTML report generated: {report_path}")
                else:
                    # Fallback to simple report
                    report_path = generate_simple_report(analysis_data, analysis_id)
                    report_url = f"/reports/{os.path.basename(report_path)}"
                    
            except Exception as e:
                print(f"⚠️  Enhanced report failed: {e}")
                # Fallback to simple report
                report_path = generate_simple_report(analysis_data, analysis_id)
                report_url = f"/reports/{os.path.basename(report_path)}"
        else:
            # Generate simple report
            report_path = generate_simple_report(analysis_data, analysis_id)
            report_url = f"/reports/{os.path.basename(report_path)}"
        
        # Update analysis data with report path
        analysis_data["report_path"] = report_path
        
        # 9. Check for ELA image
        ela_image_url = None
        ela_image_name = f"ela_{filename}"
        ela_image_path = os.path.join(ELA_DIR, ela_image_name)
        if os.path.exists(ela_image_path):
            ela_image_url = f"/uploads/ela_samples/{ela_image_name}"
        
        # 10. Prepare Response
        response_data = {
            "status": "success",
            "id": analysis_id,
            "result": analysis_data,
            "ela_image_url": ela_image_url,
            "ela_overlay_url": ela_overlay_url,
            "copy_move_visual_url": copy_move_visual_url,
            "report_url": report_url,
            "processing_time": round(processing_time, 2)
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# ---------- CNN Only Analysis ----------
@app.post("/api/analyze/cnn")
async def analyze_cnn_only(file: UploadFile = File(...)):
    """CNN-only analysis endpoint"""
    try:
        # Save file temporarily
        file_id = str(uuid.uuid4())
        temp_path = os.path.join(UPLOAD_DIR, f"temp_{file_id}.jpg")
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Get CNN prediction
        if CNN_AVAILABLE:
            prediction, confidence = predict_image(temp_path)
            is_fake = prediction == "FAKE"
        else:
            # Dummy data
            prediction = "FAKE"
            confidence = 85.0
            is_fake = True
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "is_fake": is_fake
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Forensics Only Analysis ----------
@app.post("/api/analyze/forensics")
async def analyze_forensics_only(file: UploadFile = File(...)):
    """Forensics-only analysis endpoint"""
    try:
        # Save file temporarily
        file_id = str(uuid.uuid4())
        temp_path = os.path.join(UPLOAD_DIR, f"temp_{file_id}.jpg")
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Get forensic analysis
        if FORENSICS_AVAILABLE:
            results = run_full_forensic_analysis(temp_path)
            ela_score = results.get("ela_score", 0.0)
            metadata_score = results.get("metadata_score", 0.0)
            copy_move_score = results.get("copy_move_score", 0.0)
        else:
            # Dummy data
            ela_score = 65.0
            metadata_score = 40.0
            copy_move_score = 20.0
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        forensic_avg = (ela_score + metadata_score + copy_move_score) / 3.0
        
        return {
            "ela_score": ela_score,
            "metadata_score": metadata_score,
            "copy_move_score": copy_move_score,
            "forensic_average": round(forensic_avg, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- History Endpoint ----------
@app.get("/api/history")
async def fetch_history(limit: int = 20):
    """Get analysis history"""
    try:
        history = get_history(limit)
        return {"history": history, "count": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Stats Endpoint ----------
@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total analyses
        cursor.execute("SELECT COUNT(*) FROM analyses")
        total = cursor.fetchone()[0]
        
        # Fake vs Real
        cursor.execute("SELECT COUNT(*) FROM analyses WHERE is_fake = 1")
        fake_count = cursor.fetchone()[0]
        
        # Average scores
        cursor.execute("SELECT AVG(cnn_confidence), AVG(ela_enhanced_score), AVG(copy_move_enhanced_score) FROM analyses")
        avg_cnn, avg_ela_enhanced, avg_cm_enhanced = cursor.fetchone()
        
        # Recent analyses
        cursor.execute("SELECT filename, enhanced_risk_level, timestamp FROM analyses ORDER BY timestamp DESC LIMIT 5")
        recent = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_analyses": total,
            "fake_count": fake_count,
            "real_count": total - fake_count,
            "avg_cnn_confidence": round(avg_cnn or 0, 2),
            "avg_ela_enhanced_score": round(avg_ela_enhanced or 0, 2),
            "avg_cm_enhanced_score": round(avg_cm_enhanced or 0, 2),
            "recent_analyses": [
                {"filename": r[0], "risk_level": r[1], "timestamp": r[2]} 
                for r in recent
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Report Generation ----------
def generate_simple_report(analysis_data, analysis_id):
    """Generate a simple text report (fallback)"""
    try:
        report_filename = f"report_{analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path = os.path.join(REPORTS_DIR, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("TRUTHLENS ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Report ID: {analysis_id}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Filename: {analysis_data['filename']}\n\n")
            
            f.write("-" * 40 + "\n")
            f.write("ANALYSIS RESULTS\n")
            f.write("-" * 40 + "\n")
            
            f.write(f"Risk Level: {analysis_data['risk_level']}\n")
            f.write(f"Enhanced Risk Level: {analysis_data.get('enhanced_risk_level', analysis_data['risk_level'])}\n")
            f.write(f"CNN Prediction: {'FAKE' if analysis_data['is_fake'] else 'REAL'}\n")
            f.write(f"CNN Confidence: {analysis_data['cnn_confidence']}%\n\n")
            
            f.write("Forensic Analysis:\n")
            f.write(f"  • ELA Score: {analysis_data['ela_score']}%\n")
            f.write(f"  • ELA Enhanced: {analysis_data.get('ela_enhanced_score', analysis_data['ela_score'])}%\n")
            f.write(f"  • Metadata Score: {analysis_data['metadata_score']}%\n")
            f.write(f"  • Copy-Move Score: {analysis_data['copy_move_score']}%\n")
            f.write(f"  • Copy-Move Enhanced: {analysis_data.get('copy_move_enhanced_score', analysis_data['copy_move_score'])}%\n\n")
            
            f.write("-" * 40 + "\n")
            f.write("INTERPRETATION\n")
            f.write("-" * 40 + "\n")
            
            risk_level = analysis_data.get('enhanced_risk_level', analysis_data['risk_level'])
            if risk_level == "HIGH":
                f.write("⚠️  HIGH RISK: Significant evidence of manipulation detected.\n")
                f.write("   Recommendations:\n")
                f.write("   - Verify image source\n")
                f.write("   - Do not use for authentication\n")
                f.write("   - Consider expert verification\n")
            elif risk_level == "MEDIUM":
                f.write("⚠️  MEDIUM RISK: Some suspicious indicators found.\n")
                f.write("   Recommendations:\n")
                f.write("   - Check image context\n")
                f.write("   - Cross-reference with other sources\n")
                f.write("   - Use with caution\n")
            else:
                f.write("✅ LOW RISK: Minimal evidence of manipulation.\n")
                f.write("   Recommendations:\n")
                f.write("   - Standard verification sufficient\n")
                f.write("   - Maintain digital security practices\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("End of Report\n")
            f.write("=" * 60 + "\n")
        
        print(f"📄 Simple report generated: {report_path}")
        return report_path
        
    except Exception as e:
        print(f"⚠️  Simple report generation failed: {e}")
        return ""

# ---------- Model Evaluation Endpoint (ADD THIS) ----------
@app.get("/api/model/evaluation")
async def get_model_evaluation():
    """
    Get CNN model evaluation metrics from evaluation script
    Returns accuracy, precision, recall, inference time, confusion matrix
    """
    try:
        # Paths to evaluation results
        metrics_path = "evaluation/results/metrics.txt"
        time_path = "evaluation/results/inference_time.txt"
        cm_path = "evaluation/results/confusion_matrix.png"
        
        metrics = {}
        
        # Read metrics file
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=')
                        try:
                            metrics[key] = float(value)
                        except ValueError:
                            metrics[key] = value
        else:
            return JSONResponse(content={
                "status": "error",
                "message": "Evaluation metrics not found. Run evaluation/evaluate_testset.py first",
                "metrics": {}
            })
        
        # Read inference time
        if os.path.exists(time_path):
            with open(time_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=')
                        try:
                            metrics[key] = float(value) if key != 'pass_avg_lt_2s' else (value == 'True')
                        except ValueError:
                            metrics[key] = value
        
        # Check if confusion matrix exists
        cm_url = None
        if os.path.exists(cm_path):
            # You might want to serve static files from evaluation folder
            # For now, just return the path
            cm_url = "/evaluation/results/confusion_matrix.png"
        
        return JSONResponse(content={

            "status": "success",
            "metrics": metrics,
            "confusion_matrix_url": cm_url,
            "inference_pass": metrics.get('pass_avg_lt_2s', False),
            "model_path": "checkpoints/BEST_DEEPFAKE_MODEL.pth"
        })
        
    except Exception as e:
        print(f"❌ Error getting model evaluation: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )
    
    
# ---------- Run Server ----------
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting TruthLens Backend with enhanced features...")
    print(f"   - CNN Available: {CNN_AVAILABLE}")
    print(f"   - Forensics Available: {FORENSICS_AVAILABLE}")
    print(f"   - Enhanced Forensics: {ENHANCED_FORENSICS_AVAILABLE}")
    print(f"   - Advanced Reports: {REPORT_GEN_AVAILABLE}")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)