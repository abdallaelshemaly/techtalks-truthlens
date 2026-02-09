from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TEST_DIR = DATA_DIR / "test"
REAL_TEST_DIR = TEST_DIR / "real"
FAKE_TEST_DIR = TEST_DIR / "fake"

# CNN settings
IMAGE_SIZE = (224, 224) 

# Logging
LOG_DIR = PROJECT_ROOT / "logs"
UPLOADS_DIR = PROJECT_ROOT / "uploads"

# Enhanced forensic directories
PROCESSED_DIR = DATA_DIR / "processed"
REAL_PROCESSED_DIR = PROCESSED_DIR / "real"
FAKE_PROCESSED_DIR = PROCESSED_DIR / "fake"

REPORTS_DIR = PROJECT_ROOT / "reports"
MODELS_DIR = PROJECT_ROOT / "models"
ELA_OUTPUT_DIR = UPLOADS_DIR / "ela_samples"
ELA_OVERLAY_DIR = UPLOADS_DIR / "ela_overlays"
COPY_MOVE_VISUAL_DIR = UPLOADS_DIR / "cm_visuals"

# Database
DB_PATH = PROJECT_ROOT / "truthlens.db"

# Create all directories on import
for directory in [LOG_DIR, UPLOADS_DIR, ELA_OVERLAY_DIR, COPY_MOVE_VISUAL_DIR, 
                  REPORTS_DIR, MODELS_DIR, PROCESSED_DIR, REAL_PROCESSED_DIR, FAKE_PROCESSED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)