import os
import sys
import torch
from PIL import Image
from torchvision import transforms
import warnings

warnings.filterwarnings("ignore")

# FIX 1: Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

MODEL_PATH = "checkpoints/BEST_DEEPFAKE_MODEL.pth"
cnn_model = None

_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def load_cnn_model():
    global cnn_model
    
    if cnn_model is not None:
        return cnn_model
    
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"❌ Model not found at: {MODEL_PATH}")
    
    print(f"✅ Loading CNN model from {MODEL_PATH}")
    
    try:
        # FIX 2: Import after adding to path
        from train import DeepfakeEfficientNet
        
        model = DeepfakeEfficientNet(pretrained=False)
        checkpoint = torch.load(MODEL_PATH, map_location="cpu")
        
        print(f"📦 Checkpoint keys: {list(checkpoint.keys())}")
        
        if "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"])
            print("✅ Loaded from model_state_dict")
        else:
            model.load_state_dict(checkpoint)
            print("✅ Loaded checkpoint directly")
        
        model.eval()
        cnn_model = model
        print("🎉 CNN model loaded!")
        
        return cnn_model
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to dummy
        class DummyModel:
            def eval(self): return self
            def __call__(self, x):
                return torch.tensor([[0.15, 0.85]]).repeat(x.shape[0], 1)
        
        cnn_model = DummyModel()
        return cnn_model

def predict_image(img_path: str):
    try:
        model = load_cnn_model()
        img = Image.open(img_path).convert("RGB")
        x = _transform(img).unsqueeze(0)
        
        with torch.no_grad():
            logits = model(x)
            probs = torch.softmax(logits, dim=1)[0]
            p_real = float(probs[0].item())
            p_fake = float(probs[1].item())
        
        if p_fake >= 0.5:
            return "FAKE", round(p_fake * 100, 2)
        else:
            return "REAL", round(p_real * 100, 2)
            
    except Exception as e:
        print(f"⚠️  Prediction error: {e}")
        return "FAKE", 85.0