import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from PIL import Image

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

import matplotlib.pyplot as plt


# -------------------------
# Config
# -------------------------
@dataclass
class EvalConfig:
    model_path: str = "checkpoints/BEST_DEEPFAKE_MODEL.pth"
    test_real_dir: str = "data/test/real"
    test_fake_dir: str = "data/test/fake"

    out_dir: str = "evaluation/results"
    batch_size: int = 32
    num_workers: int = 0

    # Device auto-detect
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


# -------------------------

# -------------------------
class DeepfakeEfficientNet(nn.Module):
    def __init__(self, pretrained: bool = False):
        super().__init__()
        weights = EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
        backbone = efficientnet_b0(weights=weights)

       
        for param in backbone.features[:4].parameters():
            param.requires_grad = False

        self.features = backbone.features
        self.avgpool = backbone.avgpool
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(1280, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, 2),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)


class ModelLoader:
    """Loads checkpoint into model."""
    def __init__(self, cfg: EvalConfig):
        self.cfg = cfg

    def load(self) -> nn.Module:
        if not os.path.exists(self.cfg.model_path):
            raise FileNotFoundError(f"❌ Model not found: {self.cfg.model_path}")

        model = DeepfakeEfficientNet(pretrained=False).to(self.cfg.device)
        ckpt = torch.load(self.cfg.model_path, map_location=self.cfg.device)

        if isinstance(ckpt, dict) and "model_state_dict" in ckpt:
            model.load_state_dict(ckpt["model_state_dict"])
        else:
            model.load_state_dict(ckpt)

        model.eval()
        return model


# -------------------------
# Dataset / Loader
# -------------------------
class TestFaceDataset(Dataset):
    """Loads data/test/real and data/test/fake."""
    def __init__(self, real_dir: str, fake_dir: str, transform=None):
        self.transform = transform
        self.samples: List[Tuple[str, int]] = []

        self.samples += [(p, 0) for p in self._list_images(real_dir)]
        self.samples += [(p, 1) for p in self._list_images(fake_dir)]

        if len(self.samples) == 0:
            raise RuntimeError(
                "❌ No test images found.\n"
                f"Expected folders:\n- {real_dir}\n- {fake_dir}"
            )

    @staticmethod
    def _list_images(folder: str) -> List[str]:
        exts = (".jpg", ".jpeg", ".png", ".webp")
        folder = Path(folder)
        if not folder.exists():
            return []
        files = []
        for e in exts:
            files.extend(folder.glob(f"*{e}"))
        return [str(p) for p in files]

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label


class DataModule:
    """Builds DataLoader for test set."""
    def __init__(self, cfg: EvalConfig):
        self.cfg = cfg
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225]),
        ])

    def get_test_loader(self) -> DataLoader:
        ds = TestFaceDataset(self.cfg.test_real_dir, self.cfg.test_fake_dir, self.transform)
        return DataLoader(
            ds,
            batch_size=self.cfg.batch_size,
            shuffle=False,
            num_workers=self.cfg.num_workers
        )


# -------------------------
# Inference Timing
# -------------------------
class InferenceTimer:
    def __init__(self, cfg: EvalConfig):
        self.cfg = cfg

    def run(self, model: nn.Module, loader: DataLoader, warmup_batches=2, timed_batches=30) -> Dict[str, float]:
        times = []
        model.eval()

        with torch.no_grad():
            for i, (x, _) in enumerate(loader):
                x = x.to(self.cfg.device)

                # warmup
                if i < warmup_batches:
                    _ = model(x)
                    continue

                if i >= warmup_batches + timed_batches:
                    break

                if self.cfg.device == "cuda":
                    torch.cuda.synchronize()

                start = time.perf_counter()
                _ = model(x)
                if self.cfg.device == "cuda":
                    torch.cuda.synchronize()
                end = time.perf_counter()

                per_image = (end - start) / x.size(0)
                times.append(per_image)

        avg_s = float(np.mean(times)) if times else 0.0
        p95_s = float(np.percentile(times, 95)) if len(times) >= 5 else float(max(times) if times else 0.0)

        return {"avg_seconds": avg_s, "p95_seconds": p95_s}


# -------------------------
# Precision/Recall + other metrics
# -------------------------
class MetricsCalculator:
    def __init__(self, cfg: EvalConfig):
        self.cfg = cfg

    def predict_all(self, model: nn.Module, loader: DataLoader) -> Tuple[np.ndarray, np.ndarray]:
        y_true, y_pred = [], []
        model.eval()

        with torch.no_grad():
            for x, labels in loader:
                x = x.to(self.cfg.device)
                logits = model(x)
                preds = torch.argmax(logits, dim=1).cpu().numpy()
                y_pred.extend(preds)
                y_true.extend(labels.numpy())

        return np.array(y_true), np.array(y_pred)

    def compute(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision_fake": float(precision_score(y_true, y_pred, pos_label=1, zero_division=0)),
            "recall_fake": float(recall_score(y_true, y_pred, pos_label=1, zero_division=0)),
            "f1_fake": float(f1_score(y_true, y_pred, pos_label=1, zero_division=0)),
        }


# -------------------------
# Confusion Matrix Visualization
# -------------------------
class ConfusionMatrixVisualizer:
    def __init__(self, cfg: EvalConfig):
        self.cfg = cfg

    def save(self, y_true: np.ndarray, y_pred: np.ndarray, path: str):
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])  # [[TN, FP],[FN, TP]]

        plt.figure(figsize=(6, 5))
        plt.imshow(cm)
        plt.title("Confusion Matrix (REAL vs FAKE)")
        plt.xticks([0, 1], ["REAL", "FAKE"])
        plt.yticks([0, 1], ["REAL", "FAKE"])

        for i in range(2):
            for j in range(2):
                plt.text(j, i, str(cm[i][j]), ha="center", va="center")

        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.tight_layout()
        plt.savefig(path, dpi=200)
        plt.close()
        return cm


# -------------------------
# Model Documentation
# -------------------------
class ModelDocWriter:
    def __init__(self, cfg: EvalConfig):
        self.cfg = cfg

    def write(self, metrics: Dict[str, float], timing: Dict[str, float], cm: np.ndarray, path: str):
        tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])

        doc = f"""# TruthLens Model Evaluation

## Model
- Architecture: EfficientNetB0 (binary classifier: REAL=0, FAKE=1)
- Checkpoint: `{self.cfg.model_path}`
- Evaluation data: `{self.cfg.test_real_dir}` and `{self.cfg.test_fake_dir}`

## Inference Time (Task 1)
- Average per image: {timing["avg_seconds"]:.4f} sec
- 95th percentile:  {timing["p95_seconds"]:.4f} sec
- Requirement: < 2 sec per image
- Status: {"PASS ✅" if timing["avg_seconds"] < 2.0 else "FAIL ❌"}

## Test Metrics (Task 2)
(FAKE treated as the positive class)
- Accuracy: {metrics["accuracy"]*100:.2f}%
- Precision (FAKE): {metrics["precision_fake"]*100:.2f}%
- Recall (FAKE): {metrics["recall_fake"]*100:.2f}%
- F1 (FAKE): {metrics["f1_fake"]:.4f}

## Confusion Matrix (Task 3)
|               | Pred REAL | Pred FAKE |
|---|---:|---:|
| **Actual REAL** | {tn} | {fp} |
| **Actual FAKE** | {fn} | {tp} |

## Accuracy & Limitations (Task 4)
### Strengths
- Fast inference suitable for API usage.
- Good performance on the provided test set.

### Limitations
- Dataset bias: performance depends on similarity to real-world data.
- Compression/blur/low resolution can reduce accuracy.
- New deepfake techniques may not be detected well → periodic retraining may be needed.
- Probabilistic confidence is not guaranteed truth; low confidence should be treated as “uncertain”.

### Recommended usage
- Use CNN output as one signal and combine with other forensic tools + human review.
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(doc)


# -------------------------
# Runner
# -------------------------
def main():
    cfg = EvalConfig()
    os.makedirs(cfg.out_dir, exist_ok=True)

    print(f"✓ Device: {cfg.device}")
    print(f"✓ Model:  {cfg.model_path}")
    print(f"✓ Test:   {cfg.test_real_dir} | {cfg.test_fake_dir}")
    print(f"✓ Output: {cfg.out_dir}")

    model = ModelLoader(cfg).load()
    loader = DataModule(cfg).get_test_loader()


    timing = InferenceTimer(cfg).run(model, loader)
    with open(os.path.join(cfg.out_dir, "inference_time.txt"), "w", encoding="utf-8") as f:
        f.write(f"avg_seconds={timing['avg_seconds']:.6f}\n")
        f.write(f"p95_seconds={timing['p95_seconds']:.6f}\n")
        f.write(f"pass_avg_lt_2s={timing['avg_seconds'] < 2.0}\n")


    calc = MetricsCalculator(cfg)
    y_true, y_pred = calc.predict_all(model, loader)
    metrics = calc.compute(y_true, y_pred)
    with open(os.path.join(cfg.out_dir, "metrics.txt"), "w", encoding="utf-8") as f:
        for k, v in metrics.items():
            f.write(f"{k}={v}\n")


    cm_path = os.path.join(cfg.out_dir, "confusion_matrix.png")
    cm = ConfusionMatrixVisualizer(cfg).save(y_true, y_pred, cm_path)

  
    doc_path = os.path.join(cfg.out_dir, "MODEL_DOCUMENTATION.md")
    ModelDocWriter(cfg).write(metrics, timing, cm, doc_path)

    print(f"- {os.path.join(cfg.out_dir, 'inference_time.txt')}")
    print(f"- {os.path.join(cfg.out_dir, 'metrics.txt')}")
    print(f"- {cm_path}")
    print(f"- {doc_path}")


if __name__ == "__main__":
    main()
