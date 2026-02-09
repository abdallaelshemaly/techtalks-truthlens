import cv2
import numpy as np
import os
from PIL import Image, ImageChops, ImageEnhance
import uuid
from matplotlib import pyplot as plt
import glob

BASE_OUTPUT = "forensics_output"
ELA_OVERLAY_DIR = f"{BASE_OUTPUT}/overlay_ela"
COPY_MOVE_DIR = f"{BASE_OUTPUT}/copy_move_maps"
GALLERY_DIR = f"{BASE_OUTPUT}/gallery"

for d in [BASE_OUTPUT, ELA_OVERLAY_DIR, COPY_MOVE_DIR, GALLERY_DIR]:
    os.makedirs(d, exist_ok=True)

ELA_QUALITY = 95

def ela_overlay(image_path):
    original = Image.open(image_path).convert("RGB")
    temp_file = f"temp_{uuid.uuid4().hex}.jpg"
    original.save(temp_file, "JPEG", quality=ELA_QUALITY)
    recompressed = Image.open(temp_file)
    ela = ImageChops.difference(original, recompressed)
    extrema = ela.getextrema()
    scale = 255.0/(max(ex[1] for ex in extrema) or 1)
    ela = ImageEnhance.Brightness(ela).enhance(scale)
    ela_gray = np.array(ela.convert("L"))
    score = round(min(100,np.mean(ela_gray)*4),2)
    heatmap = cv2.applyColorMap(ela_gray, cv2.COLORMAP_JET)
    original_np = np.array(original)
    overlay = cv2.addWeighted(original_np,0.7,heatmap,0.3,0)
    os.remove(temp_file)
    return overlay, score

def copy_move_visual(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(nfeatures=1500)
    kp, des = orb.detectAndCompute(gray,None)
    if des is None: return img, 0
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = bf.knnMatch(des,des,k=2)
    suspicious = []
    for m,n in matches:
        if m.distance<0.12*n.distance and m.queryIdx!=m.trainIdx:
            suspicious.append((kp[m.queryIdx].pt,kp[m.trainIdx].pt))
    for p1,p2 in suspicious:
        cv2.circle(img,tuple(map(int,p1)),6,(0,0,255),2)
        cv2.circle(img,tuple(map(int,p2)),6,(255,0,0),2)
    score = min(100,len(suspicious)*4)
    return img,score

def analyze_image(image_path):
    filename = os.path.basename(image_path)
    ela_overlay_img, ela_score = ela_overlay(image_path)
    cm_img, cm_score = copy_move_visual(image_path)
    total = round((ela_score*0.6)+(cm_score*0.4),2)
    level = "HIGH" if total>65 else "MEDIUM" if total>30 else "LOW"
    ela_path = f"{ELA_OVERLAY_DIR}/ela_{filename}"
    cm_path = f"{COPY_MOVE_DIR}/cm_{filename}"
    gallery_path = f"{GALLERY_DIR}/gallery_{filename}"
    cv2.imwrite(ela_path, cv2.cvtColor(ela_overlay_img, cv2.COLOR_RGB2BGR))
    cv2.imwrite(cm_path, cm_img)
    fig, ax = plt.subplots(1,3,figsize=(15,5))
    ax[0].imshow(Image.open(image_path)); ax[0].set_title("Original")
    ax[1].imshow(ela_overlay_img); ax[1].set_title(f"ELA ({ela_score})")
    ax[2].imshow(cm_img[...,::-1]); ax[2].set_title(f"Copy-Move ({cm_score})")
    for a in ax: a.axis("off")
    plt.suptitle(f"Risk: {level} ({total}%)",fontsize=14)
    plt.savefig(gallery_path,dpi=200,bbox_inches="tight")
    plt.close()
    return [filename, ela_score, cm_score, total, level]

if __name__=="__main__":
    input_folders = ["data/raw/fake","data/raw/real"]
    for folder in input_folders:
        for img in glob.glob(f"{folder}/*.[jJ][pP][gG]") + glob.glob(f"{folder}/*.[pP][nN][gG]"):
            analyze_image(img)

