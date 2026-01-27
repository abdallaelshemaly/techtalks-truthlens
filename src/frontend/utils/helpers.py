"""
Helper functions for TruthLens dashboard.
"""

import streamlit as st
from PIL import Image
import io
import base64
from datetime import datetime

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def validate_image_file(file) -> tuple[bool, str]:
    """
    Validate uploaded image file.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        return False, f"File size exceeds 10MB limit. Current size: {format_file_size(file.size)}"
    
    # Check file type
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
    if file.type not in allowed_types:
        return False, f"Invalid file type. Allowed: JPG, PNG, JPEG"
    
    # Try to open the image
    try:
        image = Image.open(file)
        image.verify()  # Verify it's a valid image
        return True, "File is valid"
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"

def create_mock_analysis(image_filename: str) -> dict:
    """Create mock analysis results for demonstration."""
    return {
        "filename": image_filename,
        "timestamp": datetime.now().isoformat(),
        "risk_score": 32.5,
        "authenticity_score": 67.5,
        "confidence": 85.2,
        "processing_time": 2.1,
        "findings": {
            "artifacts_detected": False,
            "ai_generation_suspected": False,
            "metadata_consistent": True,
            "compression_artifacts": True
        },
        "recommendations": [
            "Verify original source",
            "Check context of use",
            "Consider expert review for critical decisions"
        ]
    }