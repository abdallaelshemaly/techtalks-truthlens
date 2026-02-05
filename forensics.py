import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from PIL.ExifTags import TAGS
import os
import uuid
from datetime import datetime

# ==========================================
# 1. METADATA ANALYSIS
# ==========================================
def get_metadata_score(image_path):
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'Software' and any(x in str(value).lower() for x in ['adobe', 'photoshop', 'gimp']):
                    return 100.0
            return 0.0
        else:
            return 40.0
    except:
        return 20.0

# ==========================================
# 2. COMPLETE ELA (Error Level Analysis)
# ==========================================
def get_ela_score(image_path, quality=95):
    temp_file = f"temp_{uuid.uuid4().hex}.jpg"
    try:
        original = Image.open(image_path).convert("RGB")
        original.save(temp_file, "JPEG", quality=quality)
        resaved = Image.open(temp_file)
        
        ela_diff = ImageChops.difference(original, resaved)
        extrema = ela_diff.getextrema()
        scale = 255.0 / (max(ex[1] for ex in extrema) or 1)
        ela_enhanced = ImageEnhance.Brightness(ela_diff).enhance(scale)
        
        avg_brightness = np.mean(np.array(ela_enhanced.convert("L")))
        score = min(100.0, avg_brightness * 4)
        return round(float(score), 2)
    except:
        return 0.0
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

# ==========================================
# 3. COPY-MOVE DETECTION
# ==========================================
def get_copy_move_score(image_path):
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        orb = cv2.ORB_create(nfeatures=1000)
        kp, des = orb.detectAndCompute(img, None)
        if des is None: return 0.0
        
        bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        matches = bf.knnMatch(des, des, k=2)
        clones = sum(1 for m, n in matches if m.queryIdx != m.trainIdx and m.distance < 0.1 * n.distance)
        return min(float(clones * 10), 100.0)
    except:
        return 0.0

# ==========================================
# 4. COMBINED SCORE (CALLED BY API)
# ==========================================
def run_full_forensic_analysis(image_path, label="uploaded"):
    ela = get_ela_score(image_path)
    meta = get_metadata_score(image_path)
    cm = get_copy_move_score(image_path)
    
    # Combined score (Weighted: 40% ELA, 40% Meta, 20% Copy-Move)
    combined = round((ela * 0.4) + (meta * 0.4) + (cm * 0.2), 2)
    risk_lvl = "HIGH" if combined > 70 else "MEDIUM" if combined > 35 else "LOW"

    return {
        "filename": os.path.basename(image_path),
        "label": label,
        "ela_score": ela,
        "metadata_score": meta,
        "copy_move_score": cm,
        "combined_risk": combined,
        "risk_level": risk_lvl
    }

# ==========================================
# 5. AUTO-SCAN LOOP
# ==========================================
if __name__ == "__main__":
    base_raw_path = r"C:\Users\HCES\MyProject\data\raw"
    sub_folders = ["fake", "real"]
    
    print("--- STARTING FORENSIC ANALYSIS ---")
    
    for folder in sub_folders:
        folder_path = os.path.join(base_raw_path, folder)
        if not os.path.exists(folder_path):
            continue
        
        print(f"\nFolder: {folder.upper()}")
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(folder_path, filename)
                res = run_full_forensic_analysis(img_path, label=folder)
                
                # Print results clearly in terminal
                print(f"File: {res['filename']} | ELA: {res['ela_score']} | Meta: {res['metadata_score']} | CM: {res['copy_move_score']} | TOTAL: {res['combined_risk']}% ({res['risk_level']})")

    print("\n--- ANALYSIS FINISHED ---")