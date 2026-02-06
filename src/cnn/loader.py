import os
import torch
from PIL import Image
from torchvision import transforms
import warnings

warnings.filterwarnings("ignore")

# Path to the trained model (from Sprint 1)
MODEL_PATH = "checkpoints/BEST_DEEPFAKE_MODEL.pth"

# Global model (loaded once)
cnn_model = None

# Image preprocessing (same as training)
_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])


def load_cnn_model():
    """
    Loads the trained CNN model once and keeps it in memory.
    Task 1: CNN model loaded in FastAPI backend
    """
    global cnn_model

    # Return already loaded model
    if cnn_model is not None:
        return cnn_model

    # Check model file exists
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"❌ Model not found at: {MODEL_PATH}. "
            "Make sure BEST_DEEPFAKE_MODEL.pth exists."
        )

    print(f"✅ Loading CNN model from {MODEL_PATH}")

    # Import model architecture from training code
    from train import DeepfakeEfficientNet
    model = DeepfakeEfficientNet(pretrained=False)

    # Load weights
    checkpoint = torch.load(MODEL_PATH, map_location="cpu")
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)

    model.eval()
    cnn_model = model

    print("✅ CNN model loaded and ready")
    return cnn_model


def predict_image(img_path: str):
   
    model = load_cnn_model()

    # Load and validate image
    try:
        img = Image.open(img_path).convert("RGB")
    except Exception as e:
        raise ValueError(f"Invalid image file: {e}")

    # Preprocess
    x = _transform(img).unsqueeze(0)  # (1, 3, 224, 224)

    # Inference
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)[0]  # [p_real, p_fake]

    p_real = float(probs[0].item())
    p_fake = float(probs[1].item())

    if p_fake >= 0.5:
        return "FAKE", round(p_fake * 100, 2)
    else:
        return "REAL", round(p_real * 100, 2)
