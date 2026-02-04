"""
Resizes images to 224x224 and saves them to data/processed/
"""

import os
from pathlib import Path
from PIL import Image
import numpy as np
from tqdm import tqdm


def create_directories():
    """Create necessary directories for processed data"""
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)

    fake_dir = processed_dir / "fake"
    real_dir = processed_dir / "real"

    fake_dir.mkdir(exist_ok=True)
    real_dir.mkdir(exist_ok=True)

    return fake_dir, real_dir


def preprocess_image(image_path, target_size=(224, 224)):
    """
    Preprocess a single image:
    - Load image
    - Resize to target_size
    - Convert to RGB if necessary

    Args:
        image_path: Path to the input image
        target_size: Tuple of (width, height) for output

    Returns:
        PIL Image object
    """
    try:
        # Open image
        img = Image.open(image_path)

        # Convert to RGB if image is in different mode (e.g., RGBA, L)
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Resize image
        img_resized = img.resize(target_size, Image.LANCZOS)

        return img_resized

    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return None


def process_directory(input_dir, output_dir, target_size=(224, 224)):
    """
    Process all images in a directory

    Args:
        input_dir: Path to input directory
        output_dir: Path to output directory
        target_size: Tuple of (width, height) for output
    """
    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"Warning: Directory {input_dir} does not exist. Skipping...")
        return

    # Get all image files
    image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]
    image_files = [
        f
        for f in input_path.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    if not image_files:
        print(f"No images found in {input_dir}")
        return

    print(f"\nProcessing {len(image_files)} images from {input_dir}...")

    # Process each image
    successful = 0
    for img_file in tqdm(image_files, desc=f"Processing {input_path.name}"):
        # Preprocess image
        processed_img = preprocess_image(img_file, target_size)

        if processed_img is not None:
            # Save processed image
            output_path = Path(output_dir) / img_file.name
            processed_img.save(output_path, quality=95)
            successful += 1

    print(f"Successfully processed {successful}/{len(image_files)} images")


def main():
    """Main preprocessing pipeline"""
    print("=" * 60)
    print("Image Preprocessing for TechTalks-TruthLens")
    print("=" * 60)

    # Create output directories
    fake_output, real_output = create_directories()

    # Process fake images - FIXED: uses data/raw/fake
    process_directory("data/raw/fake", fake_output, target_size=(224, 224))

    # Process real images - FIXED: uses data/raw/real
    process_directory("data/raw/real", real_output, target_size=(224, 224))

    print("\n" + "=" * 60)
    print("Preprocessing complete!")
    print(f"Processed images saved to: data/processed/")
    print("=" * 60)


if __name__ == "__main__":
    main()
