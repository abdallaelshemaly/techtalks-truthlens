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