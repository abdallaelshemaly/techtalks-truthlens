# TruthLens Model Evaluation

## Model
- Architecture: EfficientNetB0 (binary classifier: REAL=0, FAKE=1)
- Checkpoint: `checkpoints/BEST_DEEPFAKE_MODEL.pth`
- Evaluation data: `data/test/real` and `data/test/fake`

## Inference Time (Task 1)
- Average per image: 0.0154 sec
- 95th percentile:  0.0169 sec
- Requirement: < 2 sec per image
- Status: PASS ✅

## Test Metrics (Task 2)
(FAKE treated as the positive class)
- Accuracy: 95.34%
- Precision (FAKE): 96.76%
- Recall (FAKE): 93.23%
- F1 (FAKE): 0.9496

## Confusion Matrix (Task 3)
|               | Pred REAL | Pred FAKE |
|---|---:|---:|
| **Actual REAL** | 210 | 6 |
| **Actual FAKE** | 13 | 179 |

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
