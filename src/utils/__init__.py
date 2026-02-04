"""
TruthLens Utilities Package
Exposes all utilities for easy import
"""

from pathlib import Path

# Import from submodules
from .logger import setup_logger
from .helpers import (
    load_image_for_cnn,
    validate_test_images,
    get_test_images,
    create_dataset_report,
    check_dependencies,
)
from .config import (
    PROJECT_ROOT,
    DATA_DIR,
    TEST_DIR,
    REAL_TEST_DIR,
    FAKE_TEST_DIR,
    IMAGE_SIZE,
    LOG_DIR,
    UPLOADS_DIR,
    DB_PATH,
    REPORTS_DIR, 
    MODELS_DIR, 
    PROCESSED_DIR,
    ELA_OUTPUT_DIR,
)

__all__ = [
    # Functions
    "setup_logger",
    "load_image_for_cnn",
    "validate_test_images",
    "get_test_images",
    "create_dataset_report",
    "check_dependencies",
    # Paths
    "PROJECT_ROOT",
    "DATA_DIR",
    "TEST_DIR",
    "REAL_TEST_DIR",
    "FAKE_TEST_DIR",
    "UPLOADS_DIR",
    "LOG_DIR",
    "DB_PATH",
    "REPORTS_DIR",
    "MODELS_DIR",
    "PROCESSED_DIR",
    "ELA_OUTPUT_DIR",
    # Configurations
    "IMAGE_SIZE",
]

"""
# In config.py - ADD THESE:
PROCESSED_DIR = DATA_DIR / "processed"
REAL_PROCESSED_DIR = PROCESSED_DIR / "real"
FAKE_PROCESSED_DIR = PROCESSED_DIR / "fake"

REPORTS_DIR = PROJECT_ROOT / "reports"
MODELS_DIR = PROJECT_ROOT / "models"
ELA_OUTPUT_DIR = UPLOADS_DIR / "ela_samples"
"""
