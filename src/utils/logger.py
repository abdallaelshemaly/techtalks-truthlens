import logging
import sys
import os


def setup_logger(name, log_file="truthlens.log"):
    """Setup logger for any module"""
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # File handler
    fh = logging.FileHandler(f"logs/{log_file}")
    # Console handler
    ch = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger


# Test the function
if __name__ == "__main__":
    test_logger = setup_logger("test")
    test_logger.info("Logger working correctly!")
    print("✅ Logger test passed!")
