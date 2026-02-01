def check_dependencies():
    """
    Check if all required dependencies are available.
    Returns dictionary with availability status.
    """
    dependencies = {
        "opencv": False,
        "numpy": False,
        "PIL": False,
        "torch": False,
        "torchvision": False,
    }

    try:
        import cv2

        dependencies["opencv"] = True
    except ImportError:
        pass

    try:
        import numpy

        dependencies["numpy"] = True
    except ImportError:
        pass

    try:
        from PIL import Image

        dependencies["PIL"] = True
    except ImportError:
        pass

    try:
        import torch

        dependencies["torch"] = True
    except ImportError:
        pass

    try:
        import torchvision

        dependencies["torchvision"] = True
    except ImportError:
        pass

    return dependencies


def get_dataset_statistics():
    """
    Get detailed statistics about the dataset.
    """
    real_processed = len(list(Path("data/processed/real").glob("*.*")))
    fake_processed = len(list(Path("data/processed/fake").glob("*.*")))
    real_raw = len(list(Path("data/real").glob("*.*")))
    fake_raw = len(list(Path("data/fake").glob("*.*")))

    return {
        "raw": {"real": real_raw, "fake": fake_raw, "total": real_raw + fake_raw},
        "processed": {
            "real": real_processed,
            "fake": fake_processed,
            "total": real_processed + fake_processed,
        },
        "test": {
            "real": len(get_test_images("real")),
            "fake": len(get_test_images("fake")),
        },
    }
