"""
Database operations for TruthLens
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = "truthlens.db"


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Main analyses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_fake BOOLEAN,
            cnn_confidence REAL,
            ela_score REAL,
            metadata_score REAL,
            copy_move_score REAL,
            risk_level TEXT,
            report_path TEXT,
            file_path TEXT
        )
    ''')
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp
        ON analyses(timestamp)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_is_fake
        ON analyses(is_fake)
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")


def log_analysis(data):
    """Insert a new analysis record into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO analyses 
        (filename, is_fake, cnn_confidence, ela_score, metadata_score, 
         copy_move_score, risk_level, report_path, file_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("filename", "unknown"),
        data.get("is_fake", False),
        data.get("cnn_confidence", 0.0),
        data.get("ela_score", 0.0),
        data.get("metadata_score", 0.0),
        data.get("copy_move_score", 0.0),
        data.get("risk_level", "Unknown"),
        data.get("report_path", ""),
        data.get("file_path", "")
    ))

    conn.commit()
    analysis_id = cursor.lastrowid
    conn.close()
    return analysis_id


def get_history(limit=20):
    """Retrieve past analyses."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM analyses ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    
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
            "metadata_score": row[6],
            "copy_move_score": row[7],
            "risk_level": row[8],
            "report_path": row[9]
        })
    
    conn.close()
    return history


def get_analysis_by_id(analysis_id):
    """Get specific analysis by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "filename": row[1],
            "timestamp": row[2],
            "is_fake": bool(row[3]),
            "cnn_confidence": row[4],
            "ela_score": row[5],
            "metadata_score": row[6],
            "copy_move_score": row[7],
            "risk_level": row[8],
            "report_path": row[9]
        }
    return None


def get_stats():
    """Get statistics about analyses."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total analyses
    cursor.execute("SELECT COUNT(*) FROM analyses")
    total = cursor.fetchone()[0]
    
    # Fake vs Real
    cursor.execute("SELECT COUNT(*) FROM analyses WHERE is_fake = 1")
    fake_count = cursor.fetchone()[0]
    
    # Average risk scores
    cursor.execute("SELECT AVG(cnn_confidence), AVG(ela_score) FROM analyses")
    avg_cnn, avg_ela = cursor.fetchone()
    
    conn.close()
    
    return {
        "total_analyses": total,
        "fake_count": fake_count,
        "real_count": total - fake_count,
        "avg_cnn_confidence": avg_cnn or 0,
        "avg_ela_score": avg_ela or 0
    }


if __name__ == "__main__":
    # Test the database
    init_db()
    print("Database test completed.")