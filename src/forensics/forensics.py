import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from PIL.ExifTags import TAGS
import os
import uuid
from datetime import datetime
from pathlib import Path  # ✅ Added

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
def get_ela_image_and_score(image_path, quality=95):
    """Get ELA image and score together (reusable for visualizations)"""
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
        
        return ela_enhanced, round(float(score), 2), original
    except Exception as e:
        return None, 0.0, None
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def get_ela_score(image_path, quality=95):
    """Wrapper for backward compatibility"""
    _, score, _ = get_ela_image_and_score(image_path, quality)
    return score

# ==========================================
# 3. COPY-MOVE DETECTION
# ==========================================
def get_copy_move_image_and_score(image_path, enhanced=False):
    """Get copy-move visualization and score"""
    img = cv2.imread(image_path)
    if img is None:
        return img, 0.0
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Use enhanced parameters for Week 3 task
    if enhanced:
        orb = cv2.ORB_create(nfeatures=1500)
        distance_threshold = 0.12
        score_multiplier = 3.5
    else:
        orb = cv2.ORB_create(nfeatures=1000)
        distance_threshold = 0.10
        score_multiplier = 10.0
    
    kp, des = orb.detectAndCompute(gray, None)
    
    suspicious_points = []
    if des is not None:
        bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        matches = bf.knnMatch(des, des, k=2)
        
        for m, n in matches:
            if m.distance < distance_threshold * n.distance and m.queryIdx != m.trainIdx:
                suspicious_points.append((kp[m.queryIdx].pt, kp[m.trainIdx].pt))
    
    # Draw on image
    for p1, p2 in suspicious_points:
        cv2.circle(img, tuple(map(int, p1)), 6, (0, 0, 255), 2)  # Red for source
        cv2.circle(img, tuple(map(int, p2)), 6, (255, 0, 0), 2)  # Blue for duplicate
    
    # Calculate score
    cm_score = min(100.0, len(suspicious_points) * score_multiplier)
    
    return img, round(cm_score, 2)

def get_copy_move_score(image_path):
    """Wrapper for backward compatibility"""
    _, score = get_copy_move_image_and_score(image_path, enhanced=False)
    return score

# ==========================================
# 4. VISUALIZATION FUNCTIONS (Week 3 Task)
# ==========================================
def generate_ela_overlay(image_path, output_dir="uploads/ela_overlays"):
    """Create ELA heatmap overlay visualization"""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Get ELA image and score efficiently
    ela_image, ela_score, original = get_ela_image_and_score(image_path)
    if ela_image is None:
        return None, ela_score
    
    # Convert to heatmap
    ela_gray = np.array(ela_image.convert("L"))
    heatmap = cv2.applyColorMap(ela_gray, cv2.COLORMAP_JET)
    
    # Overlay on original
    original_np = np.array(original)
    overlay = cv2.addWeighted(original_np, 0.7, heatmap, 0.3, 0)
    
    # Save
    filename = Path(image_path).name
    output_path = Path(output_dir) / f"ela_overlay_{filename}"
    cv2.imwrite(str(output_path), cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    
    return str(output_path), ela_score

def generate_copy_move_visualization(image_path, output_dir="uploads/cm_visuals"):
    """Create copy-move detection visualization with enhanced detection"""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Get enhanced visualization
    cm_image, cm_score = get_copy_move_image_and_score(image_path, enhanced=True)
    
    # Save
    filename = Path(image_path).name
    output_path = Path(output_dir) / f"cm_visual_{filename}"
    cv2.imwrite(str(output_path), cm_image)
    
    return str(output_path), cm_score

# ==========================================
# 5. COMBINED ANALYSIS FUNCTIONS
# ==========================================
def run_full_forensic_analysis(image_path, label="uploaded"):
    """Original forensic analysis (for backward compatibility)"""
    ela = get_ela_score(image_path)
    meta = get_metadata_score(image_path)
    cm = get_copy_move_score(image_path)
    
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

def run_enhanced_forensic_analysis(image_path):
    """Enhanced forensic analysis with visualizations (Week 3 Task)"""
    # Get base scores
    base_result = run_full_forensic_analysis(image_path)
    
    # Generate visualizations
    ela_overlay_path, ela_enhanced = generate_ela_overlay(image_path)
    cm_visual_path, cm_enhanced = generate_copy_move_visualization(image_path)
    
    # Calculate enhanced combined score (50% ELA, 30% CM, 20% Meta)
    enhanced_combined = round(
        (ela_enhanced * 0.5) + 
        (cm_enhanced * 0.3) + 
        (base_result['metadata_score'] * 0.2), 
        2
    )
    
    enhanced_risk = "HIGH" if enhanced_combined > 65 else "MEDIUM" if enhanced_combined > 30 else "LOW"
    
    # Return enhanced results
    return {
        **base_result,
        "ela_enhanced_score": ela_enhanced,
        "copy_move_enhanced_score": cm_enhanced,
        "enhanced_combined_risk": enhanced_combined,
        "enhanced_risk_level": enhanced_risk,
        "ela_overlay_url": f"/uploads/ela_overlays/{Path(ela_overlay_path).name}" if ela_overlay_path else None,
        "copy_move_visual_url": f"/uploads/cm_visuals/{Path(cm_visual_path).name}" if cm_visual_path else None,
        "visualizations_generated": ela_overlay_path is not None and cm_visual_path is not None
    }

# ==========================================
# 6. TEST/MAIN FUNCTION
# ==========================================
if __name__ == "__main__":
    # Test the enhanced forensic analysis
    test_image = "test_image.jpg"  # Replace with actual test image
    
    if os.path.exists(test_image):
        print("--- TESTING ENHANCED FORENSIC ANALYSIS ---")
        
        # Test original
        original_result = run_full_forensic_analysis(test_image)
        print(f"Original: ELA={original_result['ela_score']}, CM={original_result['copy_move_score']}")
        
        # Test enhanced
        enhanced_result = run_enhanced_forensic_analysis(test_image)
        print(f"Enhanced: ELA={enhanced_result['ela_enhanced_score']}, CM={enhanced_result['copy_move_enhanced_score']}")
        print(f"Visualizations: {enhanced_result['visualizations_generated']}")
        
        print("--- TEST COMPLETE ---")
    else:
        print(f"Test image not found: {test_image}")