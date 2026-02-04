"""
Performs Error Level Analysis (ELA) on images.
For batch processing of dataset or single image analysis.
"""

import sys
import io
import csv
import os
from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance
import numpy as np

# Fix Windows terminal encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Threshold for no significant manipulation
NO_CHANGE_THRESHOLD = 10


def calculate_tamper_score(ela_image):
    """Calculates tampering score (0-100) based on pixel brightness."""
    grayscale_ela = ela_image.convert("L")
    pixels = list(grayscale_ela.getdata())
    avg_brightness = sum(pixels) / len(pixels)
    score = min(100, avg_brightness * 4)
    return round(score, 2)


def perform_ela(image_path, output_dir="uploads/ela_samples", quality=95):
    """
    Performs ELA on a single image.

    Args:
        image_path: Path to input image
        output_dir: Where to save ELA results
        quality: JPEG compression quality (85-95 optimal)

    Returns:
        Dictionary with ELA results
    """
    os.makedirs(output_dir, exist_ok=True)

    temp_file = os.path.join(output_dir, "temp_resaved.jpg")

    try:
        # Get filename and create output path
        base_name = os.path.basename(image_path)
        output_path = os.path.join(output_dir, f"ela_{base_name}")

        # Open and process image
        original = Image.open(image_path).convert("RGB")
        original.save(temp_file, "JPEG", quality=quality)
        resaved = Image.open(temp_file)

        # Compute ELA difference
        ela_image = ImageChops.difference(original, resaved)
        extrema = ela_image.getextrema()
        max_diff = max(ex[1] for ex in extrema) or 1
        scale = 255.0 / max_diff
        ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)

        # Calculate score
        score = calculate_tamper_score(ela_image)

        # Save ELA image
        ela_image.save(output_path)

        # Cleanup temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)

        return {
            "success": True,
            "ela_score": score,
            "ela_image_path": output_path,
            "original_image": original,
            "ela_image": ela_image,
            "filename": base_name,
        }

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return {"success": False, "error": str(e)}


def process_dataset_folders():
    """
    Process the dataset folders (for training/evaluation).
    Uses data/processed/real and data/processed/fake
    """
    processed_real = Path("data/processed/real")
    processed_fake = Path("data/processed/fake")

    # Create output directories
    ela_samples_dir = Path("data/ela_samples")
    no_change_dir = Path("data/no_significant_change")
    ela_samples_dir.mkdir(exist_ok=True, parents=True)
    no_change_dir.mkdir(exist_ok=True, parents=True)

    csv_file = "data/ela_results.csv"
    headers = ["Folder", "Filename", "ELA_Path", "Tamper_Score", "Label"]

    results = []

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        # Process real images
        if processed_real.exists():
            print(f"\nProcessing REAL images from: {processed_real}")
            for img_file in processed_real.glob("*.*"):
                if img_file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                    result = perform_ela(str(img_file), str(ela_samples_dir))
                    if result["success"]:
                        writer.writerow(
                            [
                                "real",
                                img_file.name,
                                result["ela_image_path"],
                                result["ela_score"],
                                "real",
                            ]
                        )
                        results.append(result)

        # Process fake images
        if processed_fake.exists():
            print(f"\nProcessing FAKE images from: {processed_fake}")
            for img_file in processed_fake.glob("*.*"):
                if img_file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                    result = perform_ela(str(img_file), str(ela_samples_dir))
                    if result["success"]:
                        writer.writerow(
                            [
                                "fake",
                                img_file.name,
                                result["ela_image_path"],
                                result["ela_score"],
                                "fake",
                            ]
                        )
                        results.append(result)

    print(f"\n✅ ELA processing complete!")
    print(f"   CSV saved to: {csv_file}")
    print(f"   ELA images saved to: {ela_samples_dir}")
    print(f"   Processed {len(results)} images")

    return csv_file, results


# For single image analysis (used by backend)
def analyze_single_image(image_path):
    """
    Analyze a single uploaded image.

    Args:
        image_path: Path to uploaded image (in uploads/ folder)

    Returns:
        ELA results dictionary
    """
    return perform_ela(image_path, output_dir="uploads/ela_samples")


if __name__ == "__main__":
    # Run batch processing on dataset
    csv_file, results = process_dataset_folders()
