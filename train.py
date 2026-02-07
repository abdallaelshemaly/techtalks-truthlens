"""
TRUTHLENS TRAINING - WINDOWS SAFE VERSION
FEATURES:
- No Unicode characters (Windows compatible)
- CSV-based splits (data/final_splits/)
- Enhanced data augmentation to prevent overfitting
- Early stopping based on validation performance
- Proper train/val/test separation (60/20/20)
- Saves to checkpoints/FINAL_TRUTHLENS_MODEL.pth
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from PIL import Image
from pathlib import Path
from tqdm import tqdm
import time
import pandas as pd
import os
import numpy as np
import json

# ============================================
# DEVICE SETUP
# ============================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("=" * 70)
print("TRUTHLENS TRAINING - WINDOWS SAFE VERSION")
print("=" * 70)
print(f"Device: {device.type.upper()}")
if device.type == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")
print("=" * 70)


# ============================================
# DATASET CLASS (USES CSV SPLITS)
# ============================================
class TruthLensDataset(Dataset):
    """Dataset using CSV splits to prevent data leakage"""
    def __init__(self, csv_path, transform=None):
        """
        Args:
            csv_path: Path to CSV file (train.csv, val.csv, or test.csv)
            transform: Transformations to apply
        """
        self.df = pd.read_csv(csv_path)
        self.transform = transform
        
        # Print statistics
        real_count = len(self.df[self.df['label'] == 1])
        fake_count = len(self.df[self.df['label'] == 0])
        print(f"Loaded {len(self.df)} images from {csv_path}")
        print(f"  Real: {real_count}, Fake: {fake_count}")

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = row['path']
        
        try:
            image = Image.open(img_path).convert("RGB")
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            # Return black image as fallback
            image = Image.new("RGB", (224, 224), color="black")
        
        label = row['label']
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


# ============================================
# MODEL WITH ENHANCED REGULARIZATION
# ============================================
class TruthLensEfficientNet(nn.Module):
    """Enhanced model with batch normalization and dropout"""
    def __init__(self, pretrained=True):
        super().__init__()
        weights = EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
        backbone = efficientnet_b0(weights=weights)

        # Freeze early layers to prevent overfitting
        for param in backbone.features[:5].parameters():
            param.requires_grad = False

        self.features = backbone.features
        self.avgpool = backbone.avgpool
        
        # Enhanced classifier with batch normalization
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(1280, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(256, 2),  # REAL(0) vs FAKE(1)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


# ============================================
# TRAINING FUNCTIONS
# ============================================
def train_epoch(model, dataloader, criterion, optimizer, device, epoch_num):
    """Training with progress tracking"""
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    pbar = tqdm(dataloader, desc=f"Epoch {epoch_num} [Train]")
    
    for inputs, labels in pbar:
        inputs, labels = inputs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        
        # Gradient clipping to prevent exploding gradients
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        
        # Update progress bar
        pbar.set_postfix({
            "loss": f"{running_loss/(total/len(inputs)):.4f}",
            "acc": f"{100.*correct/total:.1f}%"
        })
    
    return running_loss / len(dataloader), 100.0 * correct / total


def validate(model, dataloader, criterion, device, mode="Validation"):
    """Validation with detailed metrics"""
    model.eval()
    running_loss, correct, total = 0.0, 0, 0
    
    with torch.no_grad():
        pbar = tqdm(dataloader, desc=mode)
        for inputs, labels in pbar:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            pbar.set_postfix({
                "loss": f"{running_loss/len(dataloader):.4f}",
                "acc": f"{100.*correct/total:.1f}%"
            })
    
    return running_loss / len(dataloader), 100.0 * correct / total


# ============================================
# DATA TRANSFORMS
# ============================================
def get_train_transform():
    """Strong augmentation for training"""
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])


def get_test_transform():
    """Minimal augmentation for validation/testing"""
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])


# ============================================
# MAIN TRAINING FUNCTION
# ============================================
def main():
    # Configuration
    BATCH_SIZE = 32
    LR = 0.0001  # Lower learning rate for better convergence
    MAX_EPOCHS = 30
    PATIENCE = 7  # Early stopping patience
    
    print("Configuration:")
    print(f"  Batch Size: {BATCH_SIZE}")
    print(f"  Learning Rate: {LR}")
    print(f"  Max Epochs: {MAX_EPOCHS}")
    print(f"  Early Stopping Patience: {PATIENCE}")
    print("-" * 50)
    
    # Check if splits exist
    if not os.path.exists("data/final_splits/train.csv"):
        print("ERROR: Final splits not found!")
        print("   Please run create_final_splits.py first")
        print("   This creates data/final_splits/train.csv, val.csv, test.csv")
        return
    
    # Create datasets
    print("Loading datasets...")
    train_dataset = TruthLensDataset(
        "data/final_splits/train.csv", 
        transform=get_train_transform()
    )
    val_dataset = TruthLensDataset(
        "data/final_splits/val.csv", 
        transform=get_test_transform()
    )
    test_dataset = TruthLensDataset(
        "data/final_splits/test.csv", 
        transform=get_test_transform()
    )
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset, 
        BATCH_SIZE, 
        shuffle=True, 
        num_workers=0,
        pin_memory=device.type == "cuda"
    )
    val_loader = DataLoader(
        val_dataset, 
        BATCH_SIZE, 
        shuffle=False, 
        num_workers=0,
        pin_memory=device.type == "cuda"
    )
    test_loader = DataLoader(
        test_dataset, 
        BATCH_SIZE, 
        shuffle=False, 
        num_workers=0,
        pin_memory=device.type == "cuda"
    )
    
    print(f"Train: {len(train_loader)} batches ({len(train_dataset)} images)")
    print(f"Validation: {len(val_loader)} batches ({len(val_dataset)} images)")
    print(f"Test: {len(test_loader)} batches ({len(test_dataset)} images)")
    
    # Initialize model
    print("\nInitializing model...")
    model = TruthLensEfficientNet(pretrained=True).to(device)
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Total parameters: {total_params:,}")
    print(f"  Trainable parameters: {trainable_params:,}")
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, 
        mode='max', 
        factor=0.5, 
        patience=3
    )
    
    # Training loop with early stopping
    print("\nStarting training...")
    print("-" * 70)
    
    best_val_acc = 0.0
    patience_counter = 0
    start_time = time.time()
    
    history = {
        'train_loss': [], 'train_acc': [],
        'val_loss': [], 'val_acc': [],
        'lr': []
    }
    
    # Create checkpoint directory
    checkpoint_dir = Path("checkpoints")
    checkpoint_dir.mkdir(exist_ok=True)
    
    for epoch in range(MAX_EPOCHS):
        # Training phase
        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, device, epoch+1
        )
        
        # Validation phase
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        
        # Update learning rate scheduler
        scheduler.step(val_acc)
        
        # Store history
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        history['lr'].append(optimizer.param_groups[0]['lr'])
        
        print(f"\nEpoch {epoch+1}/{MAX_EPOCHS}:")
        print(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        print(f"  Learning Rate: {optimizer.param_groups[0]['lr']:.6f}")
        
        # Early stopping check
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            
            # Save best model
            final_model_path = checkpoint_dir / "FINAL_TRUTHLENS_MODEL.pth"
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "scheduler_state_dict": scheduler.state_dict(),
                "train_acc": train_acc,
                "val_acc": val_acc,
                "best_val_acc": best_val_acc,
                "history": history,
                "config": {
                    "batch_size": BATCH_SIZE,
                    "lr": LR,
                    "max_epochs": MAX_EPOCHS,
                    "patience": PATIENCE
                }
            }, final_model_path)
            
            print(f"  [SAVED] New best model! (Val Acc: {val_acc:.2f}%)")
        else:
            patience_counter += 1
            print(f"  [NO IMPROVEMENT] ({patience_counter}/{PATIENCE})")
            
            if patience_counter >= PATIENCE:
                print(f"  [STOPPING] Early stopping at epoch {epoch+1}")
                break
        
        print("-" * 50)
    
    # Final evaluation on test set
    print("\n" + "=" * 70)
    print("FINAL EVALUATION ON UNSEEN TEST DATA")
    print("=" * 70)
    
    # Load best model
    checkpoint_path = "checkpoints/FINAL_TRUTHLENS_MODEL.pth"
    if os.path.exists(checkpoint_path):
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        print("Loaded best model from checkpoint")
    else:
        print(f"Warning: Best model not found at {checkpoint_path}")
        print("Using current model for testing...")
    
    # Test on completely unseen data
    test_loss, test_acc = validate(model, test_loader, criterion, device, mode="Test")
    
    # Print final results
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"  Best Validation Accuracy: {best_val_acc:.2f}%")
    print(f"  Test Accuracy (unseen data): {test_acc:.2f}%")
    
    # Calculate overfitting gap
    if history['train_acc']:
        final_train_acc = history['train_acc'][-1]
        overfit_gap = final_train_acc - test_acc
        print(f"  Final Train Accuracy: {final_train_acc:.2f}%")
        print(f"  Overfitting Gap: {overfit_gap:.1f}%")
        
        if overfit_gap > 15:
            print(f"  [WARNING] Large overfitting gap ({overfit_gap:.1f}%)")
        elif overfit_gap > 10:
            print(f"  [WARNING] Moderate overfitting gap ({overfit_gap:.1f}%)")
        else:
            print(f"  [GOOD] Small overfitting gap ({overfit_gap:.1f}%)")
    
    # Save reports
    save_final_report(history, test_acc, time.time() - start_time, best_val_acc)
    
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE!")
    print("=" * 70)
    print(f"[SUCCESS] Model saved: checkpoints/FINAL_TRUTHLENS_MODEL.pth")
    print(f"[RESULTS] Test Accuracy: {test_acc:.2f}%")
    print(f"[TIME] Training time: {(time.time() - start_time)/60:.1f} minutes")
    print("=" * 70)


def save_final_report(history, test_acc, training_time, best_val_acc):
    """Save training report - Windows safe with proper encoding"""
    
    # Get final training accuracy safely
    final_train_acc = history['train_acc'][-1] if history['train_acc'] else 0.0
    overfit_gap = final_train_acc - test_acc
    
    # Text report - ASCII only
    report = f"""
===================================================
TRUTHLENS MODEL TRAINING REPORT
===================================================
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

FINAL RESULTS:
- Test Accuracy: {test_acc:.2f}%
- Best Validation Accuracy: {best_val_acc:.2f}%
- Final Training Accuracy: {final_train_acc:.2f}%
- Training Time: {training_time/60:.1f} minutes
- Epochs Trained: {len(history['train_loss'])}

OVERFITTING ANALYSIS:
- Train-Test Gap: {overfit_gap:.2f}%
- Status: {'Good (< 10%)' if overfit_gap < 10 else 'Moderate (10-15%)' if overfit_gap < 15 else 'High (> 15%)'}
- Early Stopping: {'Used (stopped at epoch ' + str(len(history['train_loss'])) + ')' if len(history['train_loss']) < 30 else 'Not triggered'}

MODEL ARCHITECTURE:
- Base: EfficientNet-B0 (pretrained on ImageNet)
- Classifier: 1280 -> 512 -> 256 -> 2
- Batch Normalization: Yes (after each hidden layer)
- Dropout: 0.5 -> 0.3 -> 0.2
- Total Parameters: ~4M
- Trainable Parameters: ~2M

TRAINING CONFIGURATION:
- Optimizer: AdamW (weight decay=1e-4)
- Learning Rate: 0.0001 with ReduceLROnPlateau
- Batch Size: 32
- Data Augmentation: RandomCrop, HFlip, Rotation, ColorJitter
- Gradient Clipping: Max norm 1.0

DATASET:
- Source: Kaggle Real and Fake Face Detection
- Total Images: 2041 (1081 real, 960 fake)
- Split: 60% train, 20% validation, 20% test
- Test Set: COMPLETELY UNSEEN during training

===================================================
"""
    
    # JSON report for programmatic access
    json_report = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "results": {
            "test_accuracy": float(test_acc),
            "best_val_accuracy": float(best_val_acc),
            "final_train_accuracy": float(final_train_acc),
            "overfitting_gap": float(overfit_gap)
        },
        "training": {
            "time_minutes": float(training_time / 60),
            "epochs_trained": len(history['train_loss']),
            "final_learning_rate": float(history['lr'][-1]) if history['lr'] else None
        },
        "model_details": {
            "architecture": "EfficientNet-B0",
            "dropout": [0.5, 0.3, 0.2],
            "batch_normalization": True,
            "optimizer": "AdamW",
            "learning_rate": 0.0001,
            "batch_size": 32
        },
        "history": {
            "train_loss": [float(x) for x in history['train_loss']],
            "train_acc": [float(x) for x in history['train_acc']],
            "val_loss": [float(x) for x in history['val_loss']],
            "val_acc": [float(x) for x in history['val_acc']],
            "learning_rate": [float(x) for x in history['lr']]
        }
    }
    
    # Save reports
    os.makedirs("reports", exist_ok=True)
    
    # Save text report with UTF-8 encoding
    with open("reports/training_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    # Save JSON report
    with open("reports/training_report.json", "w", encoding="utf-8") as f:
        json.dump(json_report, f, indent=2)
    
    print(f"\n[REPORT] Training report saved: reports/training_report.txt")
    print(f"[REPORT] JSON report saved: reports/training_report.json")


if __name__ == "__main__":
    main()