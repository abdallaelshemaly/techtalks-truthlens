
from pathlib import Path
import shutil
import random

def split_data(
    base_dir: str = ".",    
    test_ratio: float = 0.2,
    seed: int = 42
):
    print("=" * 60)
    print("SPLITTING DATA INTO TRAIN/TEST ")
    print("=" * 60)

    base = Path(base_dir)

    real_source = base / "data" / "processed" / "real"
    fake_source = base / "data" / "processed" / "fake"

    test_real = base / "data" / "test" / "real"
    test_fake = base / "data" / "test" / "fake"

    if not real_source.exists():
        print(f"Error: {real_source} doesn't exist!")
        return
    if not fake_source.exists():
        print(f" Error: {fake_source} doesn't exist!")
        return

    test_real.mkdir(parents=True, exist_ok=True)
    test_fake.mkdir(parents=True, exist_ok=True)

    def list_images(folder: Path):
        exts = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
        imgs = []
        for e in exts:
            imgs += list(folder.glob(e))
        return imgs

    # Split REAL
    real_images = list_images(real_source)
    if len(real_images) == 0:
        print(f"No images found in {real_source}")
        return

    random.seed(seed)
    random.shuffle(real_images)
    real_test_count = int(len(real_images) * test_ratio)

    print("\nREAL images:")
    print(f"  Total: {len(real_images)}")
    print(f"  Copying to test: {real_test_count}")
    print(f"  Keeping in processed (train): {len(real_images)} (unchanged)")

    for img in real_images[:real_test_count]:
        dest = test_real / img.name
        if not dest.exists():  
            shutil.copy2(img, dest)

    # Split FAKE
    fake_images = list_images(fake_source)
    if len(fake_images) == 0:
        print(f"No images found in {fake_source}")
        return

    random.shuffle(fake_images)
    fake_test_count = int(len(fake_images) * test_ratio)

    print("\nFAKE images:")
    print(f"  Total: {len(fake_images)}")
    print(f"  Copying to test: {fake_test_count}")
    print(f"  Keeping in processed (train): {len(fake_images)} (unchanged)")

    for img in fake_images[:fake_test_count]:
        dest = test_fake / img.name
        if not dest.exists():
            shutil.copy2(img, dest)

    print("\n" + "=" * 60)
    print("SPLIT COMPLETE ")
    print("=" * 60)
    print("\nNew structure:")
    print("data/")
    print("├── processed/ ")
    print("│   ├── real/")
    print("│   └── fake/")
    print("└── test/ ")
    print("    ├── real/")
    print("    └── fake/")

    # Verify counts
    train_real_count = len(list_images(real_source))
    train_fake_count = len(list_images(fake_source))
    test_real_count2 = len(list_images(test_real))
    test_fake_count2 = len(list_images(test_fake))

    print("\nVerification:")
    print(f"  Processed real (train source): {train_real_count} images")
    print(f"  Processed fake (train source): {train_fake_count} images")
    print(f"  Test real : {test_real_count2} images")
    print(f"  Test fake : {test_fake_count2} images")


if __name__ == "__main__":
    split_data(base_dir=".")
