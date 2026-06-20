# Biometric-security-project-CYB-302
A simple biometric authentication system that:
Uses a biometric dataset (Face or Fingerprint), Cleans and processes images, Extracts features from images, Compares people for matching, Tests different security thresholds , Calculates accuracy metrics,Tries multimodal authentication (optional enhancement) and Protects biometric data

# 🔐 Biometric Authentication System

A Python-based biometric authentication system that uses facial recognition to verify and identify individuals. Built as a group project using the ORL Face Database, this system covers the full biometric pipeline — from data capture and preprocessing to feature extraction, matching, threshold testing, and security.

---


## Overview

This project implements a **biometric authentication system** using facial images and fingerprint . It demonstrates the core concepts of a real-world biometric pipeline including:

- Biometric data capture and organization
- Image quality enhancement through preprocessing
- Feature extraction and template generation
- 1:1 Verification and 1:N Identification
- Security threshold tuning
- FAR, FRR, and EER performance measurement
- Encryption and privacy protection of stored templates

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
git clone https://github.com/your-username/biometric-auth-system.git
cd biometric-auth-system
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

Download the ORL dataset from [Kaggle](https://www.kaggle.com/datasets/tavarez/the-orl-database-for-training-and-testing)

---

## How It Works

### 1. Data Preparation

The dataset is downloaded and organized into per-person subfolders. Images are manually reviewed and split into:

- **Enrollment set** — used to create biometric templates (registration phase)
- **Test set** — used during authentication (verification/identification phase)

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

Images are converted into compact numerical vectors called **biometric templates**.

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

### 4. Authentication & Identification

The matching engine uses Euclidean distance to compare a live face (the "probe") against the saved templates in the database.

Two types of scores are generated:


Genuine scores — a user compared against their own template
Impostor scores — a user compared against someone else's template


In our testing, genuine comparisons averaged ~21 matching points, while impostor comparisons averaged only ~6. Both score arrays are saved to disk with np.save() so the matching algorithm doesn't need to be re-run every time — this also feeds directly into Stage 5.

**Verification (1:1)** — answers "Is this really Person X?"

```
Claimed Template  ←→  Stored Template for X  →  Match Score
```

**Identification (1:N)** — answers "Who is this person?"

```
Unknown Template  ←→  All Templates in Database  →  Best Match
```

**Similarity Measures:**

- **Euclidean Distance** — lower score = more similar
- **Cosine Similarity** — higher score = more similar

Match scores are recorded separately:

- **Genuine scores** — same person compared to themselves
- **Impostor scores** — different people compared to each other

---

### 5. Threshold Testing

A threshold determines whether a match score is accepted or rejected.

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

Faces and fingerprints can't be "reset" like a password, so the stored templates need strong protection.

1. Threat Identification
We mapped out where the system could be attacked — during capture, storage, and matching.

2. Database Encryption
The template database is locked using AES encryption, built as a command-line tool with Python's argparse:

bashpython secure_db.py --encrypt   # locks the database
python secure_db.py --decrypt   # unlocks the database

Keeping --encrypt and --decrypt as separate flags means the two actions can never run at the same time by accident. Even if someone steals the database files, the templates inside are unreadable without the key.

3. Cancelable Biometrics (Concept)
We also looked into cancelable biometrics — scrambling a template through a one-way transformation before saving it. If a template is ever compromised, it can be revoked and the user re-enrolled with a new transformed version, similar to resetting a password.

**Ethical Considerations:**

- User consent must be obtained before capturing biometrics
- Data retention policies must be defined and enforced
- Users have the right to request deletion of their data
- System must comply with relevant data protection regulations (e.g., NDPR in Nigeria, GDPR in Europe)

---

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

## Screenshots

> _Add screenshots of your results here. Suggested images to include:_

- `outputs/before_after_preprocessing.png` — Side-by-side original vs. processed image
- `outputs/feature_keypoints.png` — Detected ORB keypoints on a face
- `outputs/roc_curve.png` — ROC curve across thresholds
- `outputs/det_curve.png` — DET curve
- `outputs/far_frr_plot.png` — FAR and FRR vs. threshold graph

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
