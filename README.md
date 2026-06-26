# 🔐 Biometric Authentication System
A Python-based multimodal biometric authentication system that progresses from a unimodal facial recognition baseline through to a secure, fused Face + Fingerprint pipeline with cryptographic template protection. Built as a group laboratory assessment covering the full biometric pipeline from live data capture and preprocessing to feature extraction, score-level fusion, threshold testing, performance evaluation, and AES-encrypted storage.


## Overview

This project implements a complete biometric authentication pipeline in three phases:

Phase 1 — Unimodal Facial Baseline: Live webcam capture, ORB feature extraction, Euclidean matching, and EER performance evaluation (baseline EER: 35.80%).

Phase 2 — Multimodal Fusion: A secondary fingerprint modality (Kaggle dataset) is processed via CLAHE and Hamming distance scoring, then fused with facial scores using weighted score-level fusion (60% Face / 40% Fingerprint), significantly reducing the EER.

Phase 3 — Cryptographic Vault: AES encryption (via Python's cryptography.fernet library) locks all stored biometric template matrices (.npy files) into .enc payloads, accessible only through an authorized CLI

## Features

- Live webcam facial data capture, segmented into enrolment and test sets
- Image preprocessing: grayscale conversion, Histogram Equalization, Gaussian noise reduction
- ORB (Oriented FAST and Rotated BRIEF) feature extraction and template generation
- Fingerprint ridge analysis via CLAHE and Binary Thresholding
- Euclidean distance matching (facial) and Hamming distance matching (fingerprint)
- Genuine and impostor score matrix generation and .npy caching
- Full FAR / FRR threshold sweep and EER calculation
- ROC curve comparison: unimodal vs. multimodal
- Min-Max Normalization for cross-modality score alignment
- AES encryption / decryption CLI for biometric template protection

## Datasets Used 
Primary (Face): Live webcam captures, organized into per-subject folders.

Secondary (Fingerprint): Kaggle fingerprint dataset.



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
Run scripts in order. Each task depends on the .npy caches written by the previous one.

## Installation

**1. Clone the repository**

**2. Install dependencies**

**3. Download the datasets**

Download the ORL dataset from [Kaggle](https://www.kaggle.com/datasets/tavarez/the-orl-database-for-training-and-testing) and place it in the `biometric-data/` folder 
Download the Fingerprint dataset as well from [fingerprint_dataset](https://www.kaggle.com/datasets/kundurunonieshreddy/finger-printdataset)


## How It Works

### 1. Data Preparation

task1_data_pipeline.py initializes the biometric_data/ directory tree and captures live facial images via webcam, strictly routing frames into enrolment_set/ or test_set/ subdirectories.

Common data quality issues logged during this step:
- Blurry images
- Poor lighting conditions
- Partially occluded faces
- Unusual angles

> **Why this matters:** Poor image quality leads to unreliable feature extraction, which directly increases false acceptances and false rejections.

---

### 2. Image Preprocessing

Each image passes through a standardized pipeline before feature extraction: grayscale conversion, Histogram Equalization for contrast normalization, and Gaussian blur for noise reduction. Outputs are cached in processed directories.

### 3. Feature Extraction & Template Generation

Images are converted into compact numerical vectors called **biometric templates**.ORB (Oriented FAST and Rotated BRIEF) detects spatially invariant keypoints and computes binary descriptors. These descriptors form the biometric template stored as a .npy NumPy array.

Templates are stored securely for use during the matching phase.

> **Raw Image vs. Template:** A raw image is the actual photo. A biometric template is a compact mathematical representation of that photo smaller, faster to compare, and safer to store.

---

### 4. Matching & Score Generation

The matching engine uses Euclidean distance to compare a live face (the "probe") against the saved templates in the database.task4_euclidean_matching.py performs 1:N comparisons : every test probe against every enrolled template. Comparisons between the same subject populate genuine_scores.npy; cross-subject comparisons populate impostor_scores.npy

Two types of scores are generated:

Genuine scores :a user compared against their own template
Impostor scores : a user compared against someone else's template


**Verification (1:1)** : answers "Is this really Person X?"

**Identification (1:N)** : answers "Who is this person?"

**Similarity Measures:**

- **Euclidean Distance** — lower score = more similar
- **Cosine Similarity** — higher score = more similar

Match scores are recorded separately:

- **Genuine scores** : same person compared to themselves
- **Impostor scores** : different people compared to each other

---

### 5. Threshold Testing

A threshold determines whether a match score is accepted or rejected.A full threshold sweep runs from 0 to the maximum recorded score. At each step, the system counts false acceptances (impostors let through) and false rejections (genuine users locked out), building a complete FAR/FRR trade-off table.

Phase 1 : Proof of Concept
A single fixed threshold (e.g. T = 15) is tested against individual scores to show the system can make a basic Accept/Reject decision.

Phase 2 : Full Threshold Sweep
The threshold is automatically swept from 0 up to the highest recorded score. At each step, the system counts how many impostors got through and how many genuine users got locked out. This maps the full trade-off between security and usability.

What different thresholds mean in practice:

ThresholdEffectBest suited forLow (e.g. T = 2)Easy access, but lets impostors through (high FAR)Low-risk settings, e.g. a cafeteriaHigh (e.g. T = 25)Blocks impostors, but locks out real users (high FRR)High-risk settings, e.g. a security operations center

Thresholds tested: `0.50, 0.60, 0.70, 0.80, 0.90`


### 6. Performance Evaluation
task6_performance.py finds the Equal Error Rate (EER) : the threshold where FAR = FRR  and renders ROC and DET curves. The unimodal facial baseline settled at EER = 35.80%.
Running this stage opens a window with two graphs:

1. FAR vs. FRR Graph
As the threshold increases, FAR drops toward zero while FRR climbs. The point where the two lines cross is the Equal Error Rate (EER) — the optimal balance between security and usability for this dataset. A clean EER crossing confirms the ORB + Euclidean matching pipeline is working correctly.

2. ROC Curve
Plots Genuine Acceptance Rate against False Acceptance Rate. A curve that bends toward the top-left corner means the system is accurately accepting real users before it starts wrongly accepting impostors.


### 7. Multimodal Biometrics 
Multimodal Fusion (Face + Fingerprint)
The fingerprint pipeline applies CLAHE to enhance ridge contrast, Binary Thresholding to isolate structural patterns, and Hamming distance for structural matching. Since Euclidean (facial) and Hamming (fingerprint) scores operate on different scales, both are brought to a common 0.0–1.0 range via Min-Max Normalization before the weighted fusion step:

To improve on the face-only (unimodal) system, we added a second biometric: fingerprint matching, then combined both for stronger security.

Combining the two systems:
Since face scores (Euclidean distance) and fingerprint scores (Hamming distance) use different scales, both are converted to a common scale using Min-Max Normalization.
The normalized scores are then combined using a weighted sum:

Fused Score = (0.6 × Face Score) + (0.4 × Fingerprint Score)

Result:

Comparing ROC curves of the fused system against the face-only baseline showed that fusion significantly lowered the bined system is more accurate and harder to fool than either biometric alone.

The work is split across three scripts:

1. task7a_fingerprint_engine.py : Fingerprint Pipeline
A separate pipeline built specifically for fingerprints, since they need ridge analysis rather than facial geometry:


CLAHE (Contrast Limited Adaptive Histogram Equalization) and Binary Thresholding to isolate ridge patterns
Extracts features and calculates Hamming distance scores (instead of Euclidean, since fingerprint data is structural, not spatial)


2. task7b_multimodal_fusion.py : Fusion Layer
Face scores (Euclidean) and fingerprint scores (Hamming) are on different scales, so this script:


Applies Min-Max Normalization to bring both score types onto the same 0.0–1.0 scale
Combines them using a weighted sum: 60% face + 40% fingerprint


3. task7c_comparative_evaluation.py : Comparison
Plots the ROC curves of the unimodal (face-only) and multimodal (face + fingerprint) systems on the same graph.

Result: The multimodal system had a noticeably lower EER than the face-only system. Combining two biometrics narrows the overlap between genuine and impostor scores, making the system more resistant to single points of failure.

> **Why multimodal?** If one biometric fails (e.g., dirty fingerprint), the second modality provides a fallback — improving both accuracy and resistance to spoofing.

---

### 8. Security & Privacy

task8_template_security.py applies AES symmetric encryption via cryptography.fernet to all .npy template matrices, locking them into .enc payloads. Even if the database is exfiltrated, the biometric templates remain cryptographically unreadable without the vault key.

Beyond encryption, the system also considered cancelable biometrics — a complementary one-way transformation strategy. Unlike AES (which is reversible), cancelable biometrics irreversibly scramble templates before storage. If a template is ever compromised, administrators can revoke it and re-enroll the user without changing the underlying biometric. This technique was documented in the lab report as a theoretical extension; the implemented code uses two-way AES to satisfy the rubric requirement of recoverable template storage.


## Performance Metrics

Results are recorded and tabulated across thresholds:

| Threshold | FAR | FRR | Notes |
|-----------|-----|-----|-------|
| 0.50 | High | Low | Too permissive |
| 0.70 | Medium | Medium | Balanced |
| EER Point | FAR = FRR | — | Optimal operating point |
| 0.90 | Low | High | Too restrictive |


---

## References

- ORL Face Database - [Kaggle](https://www.kaggle.com/datasets/tavarez/the-orl-database-for-training-and-testing)
- OpenCV Documentation -[https://docs.opencv.org](https://docs.opencv.org)
- scikit-learn - [https://scikit-learn.org](https://scikit-learn.org)
- cryptography (Fernet) - [https://cryptography.io](https://cryptography.io)

---

## License

This project was developed for academic purposes. Dataset usage is subject to the original ORL Database license terms.
