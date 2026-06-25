# Biometric-security-project-CYB-302
A simple biometric authentication system that:
Uses a biometric dataset (Face or Fingerprint), Cleans and processes images, Extracts features from images, Compares people for matching, Tests different security thresholds , Calculates accuracy metrics,Tries multimodal authentication (optional enhancement) and Protects biometric data

# 🔐 Biometric Authentication System

A Python-based biometric authentication system that uses facial recognition to verify and identify individuals. Built as a group project using the ORL Face Database, this system covers the full biometric pipeline — from data capture and preprocessing to feature extraction, matching, threshold testing, and security.

---


## Overview
 Overview

This project implements a complete biometric authentication pipeline in three phases:

Phase 1 — Unimodal Facial Baseline: Live webcam capture, ORB feature extraction, Euclidean matching, and EER performance evaluation (baseline EER: 35.80%).

Phase 2 — Multimodal Fusion: A secondary fingerprint modality (Kaggle dataset) is processed via CLAHE and Hamming distance scoring, then fused with facial scores using weighted score-level fusion (60% Face / 40% Fingerprint), significantly reducing the EER.

Phase 3 — Cryptographic Vault: AES encryption (via Python's cryptography.fernet library) locks all stored biometric template matrices (.npy files) into .enc payloads, accessible only through an authorized CLI.
---
---

## Features

- ✅ Face image preprocessing (grayscale, resize, normalize, denoise, enhance contrast)
- ✅ Feature extraction using ORB / SIFT / face embeddings
- ✅ Biometric template generation and storage
- ✅ 1:1 Verification (identity claim matching)
- ✅ 1:N Identification (unknown person vs. database)
- ✅ Configurable security thresholds
- ✅ FAR, FRR, and EER calculation
- ✅ ROC and DET curve visualization
- ✅ Biometric template encryption (Fernet)
- ✅ Optional: Multimodal score fusion

---

## Dataset
Primary (Face): Live webcam captures, organized into per-subject folders.

Secondary (Fingerprint): Kaggle fingerprint dataset.


**ORL Face Database** (also known as the AT&T Database of Faces)

- 40 subjects × 10 images each = 400 total images
- Images are 92×112 pixels, grayscale PGM format
- Variations in lighting, expression, and pose

**Download:** [Kaggle — ORL Database for Training and Testing](https://www.kaggle.com/datasets/tavarez/the-orl-database-for-training-and-testing)

**Folder Structure:**

```
dataset/
├── person1/
│   ├── img1.jpg
│   ├── img2.jpg
│   └── img3.jpg
├── person2/
│   ├── img1.jpg
│   └── ...
└── ...
```

**Split:**

| Set | Images Used | Purpose |
|-----|-------------|---------|
| Enrollment Set | img1, img2 per person | Registration / Template creation |
| Test Set | img3+ per person | Verification / Identification |


## Tech Stack

| Tool / Library | Purpose |
|----------------|---------|
| **Python 3.x** | Core programming language |
| **OpenCV (`cv2`)** | Image loading, preprocessing, feature extraction |
| **NumPy** | Numerical operations and vector math |
| **Matplotlib** | Plotting ROC/DET curves and result graphs |
| **scikit-learn** | Similarity metrics, evaluation utilities |
| **cryptography (Fernet)** | Encrypting biometric templates at rest |

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/AbeEgbezien06/Biometric-security-project-CYB-302-.git
cd Biometric-security-project-CYB-302-
```

**2. Install dependencies**

```bash
pip install opencv-python numpy matplotlib scikit-learn cryptography
```

Or using the requirements file:

```bash
pip install -r requirements.txt
```

**3. Download the dataset**

Download the ORL dataset from [Kaggle](https://www.kaggle.com/datasets/tavarez/the-orl-database-for-training-and-testing) and place it in the `biometric-data/` folder 
Download gerprint dataset as well from [fingerprint_dataset](https://www.kaggle.com/datasets/kundurunonieshreddy/finger-printdataset)the Fin
---




## How It Works

### 1. Data Preparation

The dataset is downloaded and organized into per-person subfolders. Images are manually reviewed and split into:

- **Enrollment set** — used to create biometric templates (registration phase)
- **Test set** — used during authentication (verification/identification phase)

- task1_data_pipeline.py initializes the biometric_data/ directory tree and captures live facial images via webcam, strictly routing frames into enrolment_set/ or test_set/ subdirectories.

Common data quality issues logged during this step:
- Blurry images
- Poor lighting conditions
- Partially occluded faces
- Unusual angles

> **Why this matters:** Poor image quality leads to unreliable feature extraction, which directly increases false acceptances and false rejections.

---

### 2. Image Preprocessing

Each image is passed through a standardized preprocessing pipeline before feature extraction:

```python
import cv2

img = cv2.imread("image.jpg")                          # Step 1: Load
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)           # Step 2: Grayscale
resized = cv2.resize(gray, (100, 100))                 # Step 3: Resize to 100×100
normalized = resized / 255.0                           # Step 4: Normalize intensity
blurred = cv2.GaussianBlur(normalized, (5, 5), 0)     # Step 5: Remove noise
equalized = cv2.equalizeHist(resized)                  # Step 6: Contrast enhancement
```

| Step | Operation | Reason |
|------|-----------|--------|
| Load | `cv2.imread()` | Read image from disk |
| Grayscale | `cv2.cvtColor()` | Reduce complexity, standardize input |
| Resize | `cv2.resize()` | Ensure all images are the same size |
| Normalize | Divide by 255 | Bring pixel values to [0, 1] range |
| Denoise | Gaussian / Median Blur | Remove noise artifacts |
| Equalize | Histogram Equalization | Improve low-contrast images |

---

### 3. Feature Extraction & Template Generation

Images are converted into compact numerical vectors called **biometric templates**.ORB (Oriented FAST and Rotated BRIEF) detects spatially invariant keypoints and computes binary descriptors. These descriptors form the biometric template stored as a .npy NumPy array.

```python
orb = cv2.ORB_create()
keypoints, descriptors = orb.detectAndCompute(image, None)
# descriptors → [0.21, 0.55, 0.18, ...]  ← this is the biometric template
```

**Available methods:**

| Method | Difficulty | Notes |
|--------|-----------|-------|
| ORB | Beginner | Fast, open-source, good for face matching |
| SIFT | Intermediate | More accurate, scale-invariant |
| Face Embeddings | Advanced | Deep learning-based, highest accuracy |

Templates are stored securely for use during the matching phase.

> **Raw Image vs. Template:** A raw image is the actual photo. A biometric template is a compact mathematical representation of that photo — smaller, faster to compare, and safer to store.

---

### 4. Matching & Score Generation

The matching engine uses Euclidean distance to compare a live face (the "probe") against the saved templates in the database.task4_euclidean_matching.py performs 1:N comparisons — every test probe against every enrolled template. Comparisons between the same subject populate genuine_scores.npy; cross-subject comparisons populate impostor_scores.npy

Two types of scores are generated:

Genuine scores — a user compared against their own template
Impostor scores — a user compared against someone else's template


**Verification (1:1)** — answers "Is this really Person X?"

**Identification (1:N)** — answers "Who is this person?"

**Similarity Measures:**

- **Euclidean Distance** — lower score = more similar
- **Cosine Similarity** — higher score = more similar

Match scores are recorded separately:

- **Genuine scores** — same person compared to themselves
- **Impostor scores** — different people compared to each other


### 5. Threshold Testing

A threshold determines whether a match score is accepted or rejected.A full threshold sweep runs from 0 to the maximum recorded score. At each step, the system counts false acceptances (impostors let through) and false rejections (genuine users locked out), building a complete FAR/FRR trade-off table.

```
If Score ≥ Threshold → ACCEPT (person verified)
If Score < Threshold → REJECT (person denied)
```
Phase 1 — Proof of Concept
A single fixed threshold (e.g. T = 15) is tested against individual scores to show the system can make a basic Accept/Reject decision.

Phase 2 — Full Threshold Sweep
The threshold is automatically swept from 0 up to the highest recorded score. At each step, the system counts how many impostors got through and how many genuine users got locked out. This maps the full trade-off between security and usability.

What different thresholds mean in practice:

ThresholdEffectBest suited forLow (e.g. T = 2)Easy access, but lets impostors through (high FAR)Low-risk settings, e.g. a cafeteriaHigh (e.g. T = 25)Blocks impostors, but locks out real users (high FRR)High-risk settings, e.g. a security operations center

Thresholds tested: `0.50, 0.60, 0.70, 0.80, 0.90`

| Threshold | Effect |
|-----------|--------|
| Low (e.g. 0.50) | Easier to log in — but attackers more likely accepted |
| High (e.g. 0.90) | More secure — but real users may be rejected |

---

### 6. Performance Evaluation
task6_performance.py finds the Equal Error Rate (EER) — the threshold where FAR = FRR — and renders ROC and DET curves. The unimodal facial baseline settled at EER = 35.80%.
Running this stage opens a window with two graphs:

1. FAR vs. FRR Graph
As the threshold increases, FAR drops toward zero while FRR climbs. The point where the two lines cross is the Equal Error Rate (EER) — the optimal balance between security and usability for this dataset. A clean EER crossing confirms the ORB + Euclidean matching pipeline is working correctly.

2. ROC Curve
Plots Genuine Acceptance Rate against False Acceptance Rate. A curve that bends toward the top-left corner means the system is accurately accepting real users before it starts wrongly accepting impostors.

Three key metrics are calculated:

**FAR — False Acceptance Rate**
> Percentage of impostors incorrectly accepted

```
FAR = False Acceptances / Total Impostor Attempts
```

**FRR — False Rejection Rate**
> Percentage of genuine users incorrectly rejected

```
FRR = False Rejections / Total Genuine Attempts
```

**EER — Equal Error Rate**
> The threshold point where FAR = FRR. Lower EER = better system.

**Visualizations generated:**

- 📈 **ROC Curve** — True Positive Rate vs. False Positive Rate
- 📉 **DET Curve** — FRR vs. FAR (log scale)

```python
import matplotlib.pyplot as plt
# Plots generated using matplotlib and saved to outputs/
```

---

### 7. Multimodal Biometrics (Optional)
— Multimodal Fusion (Face + Fingerprint)

To improve on the face-only (unimodal) system, we added a second biometric: fingerprint matching, then combined both for stronger security.

Fingerprint pipeline:

CLAHE (Contrast Limited Adaptive Histogram Equalization) — enhances ridge contrast
Binary Thresholding — isolates the fingerprint ridge structure
Hamming distance — used to score how closely two fingerprints match
 To improve on the face-only (unimodal) system, we added a second biometric: fingerprint matching, then combined both for stronger security.

Combining the two systems:
Since face scores (Euclidean distance) and fingerprint scores (Hamming distance) use different scales, both are converted to a common scale using Min-Max Normalization.
The normalized scores are then combined using a weighted sum:

Fused Score = (0.6 × Face Score) + (0.4 × Fingerprint Score)

Result:

Comparing ROC curves of the fused system against the face-only baseline showed that fusion significantly lowered the EER — meaning the combined system is more accurate and harder to fool than either biometric alone.

The work is split across three scripts:

1. task7a_fingerprint_engine.py — Fingerprint Pipeline
A separate pipeline built specifically for fingerprints, since they need ridge analysis rather than facial geometry:


CLAHE (Contrast Limited Adaptive Histogram Equalization) and Binary Thresholding to isolate ridge patterns
Extracts features and calculates Hamming distance scores (instead of Euclidean, since fingerprint data is structural, not spatial)


2. task7b_multimodal_fusion.py — Fusion Layer
Face scores (Euclidean) and fingerprint scores (Hamming) are on different scales, so this script:


Applies Min-Max Normalization to bring both score types onto the same 0.0–1.0 scale
Combines them using a weighted sum: 60% face + 40% fingerprint


3. task7c_comparative_evaluation.py — Comparison
Plots the ROC curves of the unimodal (face-only) and multimodal (face + fingerprint) systems on the same graph.

Result: The multimodal system had a noticeably lower EER than the face-only system. Combining two biometrics narrows the overlap between genuine and impostor scores, making the system more resistant to single points of failure.

Combines two biometric scores for improved accuracy and robustness.

**Score Fusion Example:**

```python
# Weighted sum fusion
final_score = 0.7 * score_system_A + 0.3 * score_system_B
```

Steps:
1. Get individual scores from System A and System B
2. Normalize scores to the same scale
3. Apply fusion rule (sum or weighted average)
4. Re-run matching with fused scores and compare EER

> **Why multimodal?** If one biometric fails (e.g., dirty fingerprint), the second modality provides a fallback — improving both accuracy and resistance to spoofing.

---

### 8.  Security & Encryption

task8_template_security.py applies AES symmetric encryption via cryptography.fernet to all .npy template matrices, locking them into .enc payloads. Even if the database is exfiltrated, the biometric templates remain cryptographically unreadable without the vault key. 
Faces and fingerprints can't be "reset" like a password, so the stored templates need strong protection.Two protections were implemented:

1.AES (Fernet) encryption of the template database, controlled via a command-line interface built with argparse. Separate --encrypt and --decrypt flags keep the two operations from ever running together, so the database can't accidentally be left in an inconsistent or exposed state. Even if the underlying files were exfiltrated, the templates inside remain unreadable without the key.

2.Cancelable biometrics — templates are passed through a one-way, irreversible transformation before being stored. If a database is ever compromised, administrators can revoke the affected templates and re-enroll the user with a new transformation, effectively giving biometric credentials a "password reset" equivalent.

## Performance Metrics

Results are recorded and tabulated across thresholds:

| Threshold | FAR | FRR | Notes |
|-----------|-----|-----|-------|
| 0.50 | High | Low | Too permissive |
| 0.70 | Medium | Medium | Balanced |
| EER Point | FAR = FRR | — | Optimal operating point |
| 0.90 | Low | High | Too restrictive |

---

## Team & Responsibilities

| Student | Role |
|---------|------|
| Student 1 | Dataset Collection |
| Student 2 | Dataset Organization |
| Student 3 | Image Preprocessing |
| Student 4 | Feature Extraction |
| Student 5 | Template Generation |
| Student 6 | Authentication & Matching |
| Student 7 | Threshold Testing |
| Student 8 | FAR / FRR / EER Calculation |
| Student 9 | Security & Encryption |
| Student 10 | Report Writing & Presentation |

---


---

## Project Timeline

| Week | Tasks |
|------|-------|
| Week 1 | Download dataset, organize data, preprocess images, take screenshots |
| Week 2 | Extract features, perform matching, test thresholds |
| Week 3 | Calculate FAR/FRR/EER, create graphs, add security section, write report |

---

## References

- ORL Face Database — [Kaggle](https://www.kaggle.com/datasets/tavarez/the-orl-database-for-training-and-testing)
- OpenCV Documentation — [https://docs.opencv.org](https://docs.opencv.org)
- scikit-learn — [https://scikit-learn.org](https://scikit-learn.org)
- cryptography (Fernet) — [https://cryptography.io](https://cryptography.io)

---

## License

This project was developed for academic purposes. Dataset usage is subject to the original ORL Database license terms.
