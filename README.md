# TruthLens 🔍

**AI-Powered Media Verification Platform**

---

## 📖 About
TruthLens is a **multimodal AI dashboard** designed to assist analysts, media organizations, and security professionals in assessing the authenticity of digital content. By combining computer vision, NLP, and source analysis, TruthLens provides actionable risk scores and explanations empowering human judgment in an era of widespread misinformation.

**Important**: TruthLens is a **decision-support system**, not an absolute "truth detector". It aids but does not replace human analysis.

---

## 🚨 The Problem It Solves
In today's digital landscape, professionals face:

- **Misinformation & fake news** spreading rapidly
- **Manipulated images & deepfake videos** becoming indistinguishable from real content
- **Unreliable or coordinated sources** amplifying false narratives
- **Human limitations** in detecting sophisticated forgeries at scale

TruthLens addresses these challenges by providing **scalable, AI-assisted verification** to support critical decision-making.

---

## ✨ Main Features (Planned)

### **Phase 1: Core MVP (Current Focus)**
- ✅ **Image Authenticity Analysis**
  - Detects AI-generated (GAN/diffusion) or tampered images
  - Highlights visual anomalies using OpenCV artifact detection
  - Outputs risk score (0-100%) with explanations

- ✅ **Interactive Dashboard**
  - Upload images/text for analysis
  - Visualize risk scores with color-coded alerts
  - View detailed explanations and anomaly highlights
  - Generate downloadable reports

### **Phase 2: Extended Features (If Time Allows)**
- 📝 **Text Intelligence Module**
  - Fake news detection using BERT/RoBERTa
  - Propaganda and manipulation pattern recognition
  - Suspicious phrase highlighting

- 🔗 **Source Risk Analysis**
  - Domain credibility scoring
  - Posting pattern analysis
  - Coordinated behavior detection

---

## 🛠️ Tech Stack

| Component           | Technology / Tool                          |
|---------------------|--------------------------------------------|
| **Language**        | Python 3.9+                                |
| **Image Analysis**  | OpenCV, pre-trained GAN/diffusion detectors |
| **Text Analysis**   | HuggingFace Transformers (BERT/RoBERTa)     |
| **Backend API**     | FastAPI                                    |
| **Dashboard**       | Streamlit (or Dash)                        |
| **Database**        | SQLite (prototype), PostgreSQL optional    |
| **ML Utilities**    | scikit-learn, NumPy, Pandas                |