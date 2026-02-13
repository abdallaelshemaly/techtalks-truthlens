"""
Database operations for TruthLens
Includes Auto-Migration, Indexes, and Pagination
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# Ensure DB is found in the backend directory
DB_PATH = os.path.join(os.path.dirname(__file__), "truthlens.db")

def get_db_connection():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database, create tables, add indexes, and migrate schema."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Create Main Table (if not exists)
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

    # 2. Create Batch Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS batch (
            id TEXT PRIMARY KEY,
            total_images INTEGER,
            processed_images INTEGER,
            status TEXT,
            results_summary TEXT
        )
    ''')

    # 3. Create Indexes (Task 1: Faster Queries)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON analyses(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_is_fake ON analyses(is_fake)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_filename ON analyses(filename)")

    # 4. Auto-Migration: Fix "no such column" errors
    # This checks existing columns and adds new ones if missing
    cursor.execute("PRAGMA table_info(analyses)")
    existing_columns = {row['name'] for row in cursor.fetchall()}
    
    new_columns = {
        "ela_enhanced_score": "REAL",
        "copy_move_enhanced_score": "REAL",
        "enhanced_risk_level": "TEXT",
        "ela_overlay_url": "TEXT",
        "copy_move_visual_url": "TEXT"
    }

    for col, dtype in new_columns.items():
        if col not in existing_columns:
            print(f"📦 Migrating DB: Adding missing column '{col}'...")
            try:
                cursor.execute(f"ALTER TABLE analyses ADD COLUMN {col} {dtype}")
            except Exception as e:
                print(f"⚠️ Migration warning: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Database initialized and verified at {DB_PATH}")

def check_db_connection() -> bool:
    """Check DB health (Task 4)."""
    try:
        conn = get_db_connection()
        conn.cursor().execute("SELECT 1")
        conn.close()
        return True
    except:
        return False

def log_analysis(data: Dict[str, Any]) -> int:
    """Insert analysis record into database."""
    conn = get_db_connection()
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

def get_history(limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """Get history with offset support."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM analyses ORDER BY timestamp DESC LIMIT ? OFFSET ?",
        (limit, offset)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_stats() -> Dict[str, Any]:
    """Get system stats."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM analyses")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM analyses WHERE is_fake = 1")
    fake_count = cursor.fetchone()[0]
    
    # Handle potentially null values safely
    cursor.execute("SELECT AVG(cnn_confidence), AVG(ela_enhanced_score), AVG(copy_move_enhanced_score) FROM analyses")
    row = cursor.fetchone()
    
    avg_cnn = row[0] if row and row[0] is not None else 0
    avg_ela = row[1] if row and row[1] is not None else 0
    avg_cm = row[2] if row and row[2] is not None else 0
    
    cursor.execute("SELECT filename, enhanced_risk_level, timestamp FROM analyses ORDER BY timestamp DESC LIMIT 5")
    recent = [dict(r) for r in cursor.fetchall()]

    conn.close()
    
    return {
        "total_analyses": total,
        "fake_count": fake_count,
        "real_count": total - fake_count,
        "avg_cnn_confidence": round(avg_cnn, 2),
        "avg_ela_enhanced_score": round(avg_ela, 2),
        "avg_cm_enhanced_score": round(avg_cm, 2),
        "recent_analyses": recent
    }

if __name__ == "__main__":
    init_db()