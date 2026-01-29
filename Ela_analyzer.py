import sys
import io
import csv
import os
from PIL import Image, ImageChops, ImageEnhance

# Fix Windows terminal encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Threshold for no significant manipulation
NO_CHANGE_THRESHOLD = 10


def calculate_tamper_score(ela_image):
    """
    Calculates a basic tampering score (0–100) based on pixel brightness.
    """
    grayscale_ela = ela_image.convert('L')
    pixels = list(grayscale_ela.getdata())
    avg_brightness = sum(pixels) / len(pixels)
    score = min(100, avg_brightness * 4)
    return round(score, 2)


def perform_ela(image_path, quality=95):
    """
    Performs ELA and returns a dictionary.
    """
    output_dir = "uploads/ela_samples"
    os.makedirs(output_dir, exist_ok=True)

    temp_file = "temp_resaved.jpg"

    try:
        base_name = os.path.basename(image_path)
        output_path = os.path.join(output_dir, f"ela_{base_name}")

        # Open original image
        original = Image.open(image_path).convert("RGB")
        original.save(temp_file, "JPEG", quality=quality)
        resaved = Image.open(temp_file)

        # Compute ELA
        ela_image = ImageChops.difference(original, resaved)
        extrema = ela_image.getextrema()
        max_diff = max(ex[1] for ex in extrema) or 1
        scale = 255.0 / max_diff
        ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)

        # Calculate score
        score = calculate_tamper_score(ela_image)

        # Save ELA image
        ela_image.save(output_path)

        if os.path.exists(temp_file):
            os.remove(temp_file)

        return {
            "success": True,
            "ela_score": score,
            "ela_image_path": output_path,
            "original_image": original,
            "ela_image": ela_image,
            "filename": base_name
        }

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def process_all_folders(folder_list):
    """
    Processes folders and copies ORIGINAL images with no significant change.
    """
    os.makedirs("uploads/no_significant_change", exist_ok=True)

    csv_file = "uploads/ela_results_data.csv"
    headers = ["Folder Name", "File Name", "ELA Image Path", "Tamper Score (0-100)"]

    no_change_images = []

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for folder_path in folder_list:
            if not os.path.exists(folder_path):
                print(f"Skipping missing folder: {folder_path}")
                continue

            folder_name = os.path.basename(folder_path)
            print(f"\nProcessing Folder: {folder_path}")

            files = [
                f for f in os.listdir(folder_path)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]

            for filename in files:
                img_path = os.path.join(folder_path, filename)
                result = perform_ela(img_path)

                if not result["success"]:
                    continue

                score = result["ela_score"]
                ela_path = result["ela_image_path"]

                writer.writerow([folder_name, filename, ela_path, score])
                print(f" Done: {filename} | Score: {score}")

                # Copy ORIGINAL if no significant manipulation
                if score <= NO_CHANGE_THRESHOLD:
                    clean_path = os.path.join("uploads/no_significant_change", filename)
                    result["original_image"].save(clean_path)

                    no_change_images.append(result)

    return csv_file, no_change_images


if __name__ == "__main__":
    my_folders = [
        r"C:\Users\HCES\OneDrive\Desktop\turthlens\real_and_fake_face_detection\real_and_fake_face\training_fake",
        r"C:\Users\HCES\OneDrive\Desktop\turthlens\real_and_fake_face_detection\real_and_fake_face\training_real"
    ]

    result_csv, clean_images = process_all_folders(my_folders)

    print("\n--- SUCCESS ---")
    print(f"CSV file: {result_csv}")
    print("ELA images: uploads/ela_samples/")
    print("Clean originals: uploads/no_significant_change/")
    print(f"Clean images count: {len(clean_images)}")

    if clean_images:
        first = clean_images[0]
        print(f"First clean image: {first['filename']} | Score: {first['ela_score']}")
        first["original_image"].show(title="Original Image")
        first["ela_image"].show(title="ELA Image")