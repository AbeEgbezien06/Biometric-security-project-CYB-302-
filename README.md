# Biometric-security-project-CYB-302-
A simple biometric authentication system that:
Uses a biometric dataset (Face or Fingerprint), Cleans and processes images, Extracts features from images, Compares people for matching, Tests different security thresholds , Calculates accuracy metrics,Tries multimodal authentication (optional enhancement) and Protects biometric data

# 🔐 Biometric Authentication System

A Python-based biometric authentication system that uses facial recognition to verify and identify individuals. Built as a group project using the ORL Face Database, this system covers the full biometric pipeline — from data capture and preprocessing to feature extraction, matching, threshold testing, and security.

---


## Overview

This project implements a **biometric authentication system** using facial images. It demonstrates the core concepts of a real-world biometric pipeline including:

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


**Split:**

| Set | Images Used | Purpose |
|-----|-------------|---------|
| Enrollment Set | img1, img2 per person | Registration / Template creation |
| Test Set | img3+ per person | Verification / Identification |

---

## Project Structure

```
biometric-auth-system/
│
├── dataset/                    # ORL face images (enrollment + test splits)
│
├── preprocessing/
│   └── preprocess.py           # Grayscale, resize, normalize, denoise, equalize
│
├── features/
│   └── extract_features.py     # ORB/SIFT feature extraction, template generation
│
├── matching/
│   └── authenticate.py         # Verification (1:1) and identification (1:N)
│
├── evaluation/
│   ├── threshold_test.py       # FAR/FRR at multiple thresholds
│   └── metrics.py              # EER calculation, ROC/DET curve plotting
│
├── security/
│   └── encrypt_templates.py    # Fernet encryption for stored biometric templates
│
├── multimodal/
│   └── score_fusion.py         # Optional: combine two biometric scores
│
├── templates/                  # Stored (encrypted) biometric templates
│
├── outputs/                    # Graphs, screenshots, results
│
├── requirements.txt
└── README.md
```

---

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

Download the ORL dataset from [Kaggle](https://www.kaggle.com/datasets/tavarez/the-orl-database-for-training-and-testing) and place it in the `dataset/` folder following the structure above.

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

Thresholds tested: `0.50, 0.60, 0.70, 0.80, 0.90`

| Threshold | Effect |
|-----------|--------|
| Low (e.g. 0.50) | Easier to log in — but attackers more likely accepted |
| High (e.g. 0.90) | More secure — but real users may be rejected |

---

### 6. Performance Evaluation

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

### 8. Security & Privacy

**Threat Model:**

| Stage | Threat |
|-------|--------|
| Capture | Fake face / spoofed biometric |
| Transmission | Data interception (man-in-the-middle) |
| Storage | Database theft |
| Matching | System manipulation |

**Mitigations implemented:**

- **Encryption** — Biometric templates are encrypted using `Fernet` (symmetric encryption) before storage
- **Access Control** — Only authorized processes can read/decrypt templates
- **Cancelable Biometrics** — If a template is compromised, a new transformed version can be generated without changing the underlying biometric

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
