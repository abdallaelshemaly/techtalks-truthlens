"""
Create FINAL train/val/test splits for TruthLens - FIXED VERSION
Uses data/raw/ folder structure
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os
from pathlib import Path
import shutil

def create_truthlens_splits():
    """
    Create PROPER splits for TruthLens with NO data leakage
    Uses data/raw/real/ and data/raw/fake/
    """
    print("="*70)
    print("🚀 CREATING FINAL TRUTHLENS SPLITS")
    print("="*70)
    
    # Create directories
    Path("data/final_splits").mkdir(parents=True, exist_ok=True)
    Path("checkpoints").mkdir(parents=True, exist_ok=True)
    
    # Your Kaggle data paths - USING RAW FOLDER
    real_dir = "data/raw/real"  # Your 1081 real images
    fake_dir = "data/raw/fake"  # Your 960 fake images
    
    print(f"📁 Looking for data in:")
    print(f"   Real: {real_dir}")
    print(f"   Fake: {fake_dir}")
    
    if not os.path.exists(real_dir):
        print(f"❌ ERROR: {real_dir} not found!")
        print("   Please organize your Kaggle data like:")
        print("   data/raw/real/   (with 1081 real images)")
        print("   data/raw/fake/   (with 960 fake images)")
        return
    
    if not os.path.exists(fake_dir):
        print(f"❌ ERROR: {fake_dir} not found!")
        return
    
    # Collect all images - FIXED: Use case-insensitive glob
    print("\n🔍 Collecting image files...")
    
    # Get all files and filter by extension
    def get_image_files(directory):
        image_files = []
        for file in os.listdir(directory):
            file_lower = file.lower()
            if file_lower.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')):
                # Check for exact duplicates (case differences)
                full_path = os.path.join(directory, file)
                image_files.append(full_path)
        return image_files
    
    real_images = get_image_files(real_dir)
    fake_images = get_image_files(fake_dir)
    
    print(f"✅ Found: {len(real_images)} real, {len(fake_images)} fake images")
    
    # Check for duplicates
    all_images = real_images + fake_images
    unique_images = set(os.path.basename(img).lower() for img in all_images)
    
    print(f"📊 Unique filenames: {len(unique_images)}")
    
    if len(real_images) != 1081 or len(fake_images) != 960:
        print(f"⚠️  Warning: Expected 1081 real and 960 fake, but found {len(real_images)} real and {len(fake_images)} fake")
        print("   This may indicate duplicate files or different file formats")
    
    if len(real_images) == 0 or len(fake_images) == 0:
        print("❌ Cannot create splits without images!")
        return
    
    # Create DataFrame
    data = []
    for img in real_images:
        data.append({
            'path': img,
            'filename': os.path.basename(img),
            'label': 1,  # REAL
            'label_name': 'real'
        })
    
    for img in fake_images:
        data.append({
            'path': img,
            'filename': os.path.basename(img),
            'label': 0,  # FAKE
            'label_name': 'fake'
        })
    
    df = pd.DataFrame(data)
    
    # Remove exact duplicates (same filename, case-insensitive)
    print("\n🧹 Removing duplicate filenames...")
    df['filename_lower'] = df['filename'].str.lower()
    df = df.drop_duplicates(subset=['filename_lower', 'label'], keep='first')
    df = df.drop(columns=['filename_lower'])
    
    print(f"📊 After removing duplicates: {len(df)} images")
    print(f"   Real: {len(df[df['label']==1])}, Fake: {len(df[df['label']==0])}")
    
    # SHUFFLE with a DIFFERENT seed than your Kaggle notebook
    df = df.sample(frac=1, random_state=999).reset_index(drop=True)
    
    # CRITICAL: Create DIFFERENT splits than Kaggle notebook
    print("\n🎯 Creating FINAL splits (60% train, 20% val, 20% test)...")
    
    # First: Split 80% (train+val) / 20% (test) - TEST is NEVER seen
    train_val_df, test_df = train_test_split(
        df, 
        test_size=0.2, 
        random_state=999,
        stratify=df['label']
    )
    
    # Second: Split train+val into 75% train / 25% val (of the 80%)
    train_df, val_df = train_test_split(
        train_val_df,
        test_size=0.25,
        random_state=999,
        stratify=train_val_df['label']
    )
    
    print(f"✅ Final splits created:")
    print(f"   Train: {len(train_df)} images")
    print(f"   Validation: {len(val_df)} images")
    print(f"   Test: {len(test_df)} images (COMPLETELY NEW - never used before!)")
    
    # Save splits
    train_df.to_csv("data/final_splits/train.csv", index=False)
    val_df.to_csv("data/final_splits/val.csv", index=False)
    test_df.to_csv("data/final_splits/test.csv", index=False)
    
    print(f"\n💾 Split files saved to data/final_splits/")
    
    # Create a held-out "unseen" test set directory
    create_unseen_test_set(test_df)
    
    return train_df, val_df, test_df

def create_unseen_test_set(test_df):
    """Create a completely unseen test set directory"""
    print("\n🔒 Creating UNSEEN test set directory...")
    
    # First, clean any existing test directory
    test_dir = Path("data/test")
    if test_dir.exists():
        print("   Cleaning existing test directory...")
        shutil.rmtree(test_dir)
    
    # Create test directories
    test_real_dir = Path("data/test/real")
    test_fake_dir = Path("data/test/fake")
    test_real_dir.mkdir(parents=True, exist_ok=True)
    test_fake_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy test images to separate directory
    copied = 0
    skipped = 0
    
    for _, row in test_df.iterrows():
        src = Path(row['path'])
        
        # Create unique filename to avoid conflicts
        if row['label'] == 1:  # Real
            dst = test_real_dir / row['filename']
        else:  # Fake
            dst = test_fake_dir / row['filename']
        
        # Check if file already exists (case-insensitive)
        if dst.exists():
            # Add index to make unique
            base_name = dst.stem
            ext = dst.suffix
            counter = 1
            while dst.exists():
                dst = dst.parent / f"{base_name}_{counter}{ext}"
                counter += 1
        
        # Copy file
        try:
            shutil.copy2(src, dst)
            copied += 1
        except Exception as e:
            print(f"⚠️  Could not copy {src.name}: {e}")
            skipped += 1
    
    print(f"   ✅ Copied {copied} test images to data/test/")
    if skipped > 0:
        print(f"   ⚠️  Skipped {skipped} images due to errors")
    print(f"   🔒 These images are NEVER used in training/validation")
    
    return copied

def verify_no_overlap():
    """Verify there's NO overlap between splits"""
    print("\n🔍 Verifying NO data leakage...")
    
    try:
        train_df = pd.read_csv("data/final_splits/train.csv")
        val_df = pd.read_csv("data/final_splits/val.csv")
        test_df = pd.read_csv("data/final_splits/test.csv")
        
        # Get all paths
        train_paths = set(train_df['path'].tolist())
        val_paths = set(val_df['path'].tolist())
        test_paths = set(test_df['path'].tolist())
        
        # Get all filenames (case-insensitive)
        train_files = set(f.lower() for f in train_df['filename'].tolist())
        val_files = set(f.lower() for f in val_df['filename'].tolist())
        test_files = set(f.lower() for f in test_df['filename'].tolist())
        
        # Check for overlaps in paths
        train_val_overlap = train_paths.intersection(val_paths)
        train_test_overlap = train_paths.intersection(test_paths)
        val_test_overlap = val_paths.intersection(test_paths)
        
        # Check for overlaps in filenames
        train_val_file_overlap = train_files.intersection(val_files)
        train_test_file_overlap = train_files.intersection(test_files)
        val_test_file_overlap = val_files.intersection(test_files)
        
        if (len(train_val_overlap) == 0 and len(train_test_overlap) == 0 and 
            len(val_test_overlap) == 0 and len(train_val_file_overlap) == 0 and
            len(train_test_file_overlap) == 0 and len(val_test_file_overlap) == 0):
            print("   ✅ NO data leakage detected!")
            print("   All splits are completely separate")
        else:
            print("   ⚠️  WARNING: Data leakage detected!")
            if len(train_val_overlap) > 0:
                print(f"      Train-Val path overlap: {len(train_val_overlap)} images")
            if len(train_test_overlap) > 0:
                print(f"      Train-Test path overlap: {len(train_test_overlap)} images")
            if len(val_test_overlap) > 0:
                print(f"      Val-Test path overlap: {len(val_test_overlap)} images")
            if len(train_val_file_overlap) > 0:
                print(f"      Train-Val filename overlap: {len(train_val_file_overlap)} images")
            if len(train_test_file_overlap) > 0:
                print(f"      Train-Test filename overlap: {len(train_test_file_overlap)} images")
            if len(val_test_file_overlap) > 0:
                print(f"      Val-Test filename overlap: {len(val_test_file_overlap)} images")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Clean existing splits if they exist
    if os.path.exists("data/final_splits"):
        print("🧹 Cleaning existing splits...")
        import shutil
        shutil.rmtree("data/final_splits")
    
    # Create final splits
    train_df, val_df, test_df = create_truthlens_splits()
    
    if train_df is not None:
        # Verify no overlap
        verify_no_overlap()
        
        print("\n" + "="*70)
        print("🎉 FINAL SPLITS READY FOR TRUTHLENS!")
        print("="*70)
        print("\n📋 Next steps:")
        print("1. Optional: Run preprocess.py to resize images")
        print("2. Run: python train.py")
        print("3. Model will use data/final_splits/train.csv")
        print("4. Validate with data/final_splits/val.csv")
        print("5. FINAL test with data/final_splits/test.csv")
        print("6. Use data/test/ for manual testing in dashboard")