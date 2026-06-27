# 🔐 Biometric Authentication System

A biometric authentication system that uses facial recognition — with optional fingerprint fusion — to verify and identify individuals. Built as a group project for **CYB-302**, it covers the full biometric pipeline: dataset capture, preprocessing, feature extraction, matching, threshold tuning, performance evaluation, multimodal fusion, and template security.

---

## Overview

The system is built in three phases:

- **Phase 1 — Unimodal Facial Baseline.** Live webcam capture, ORB feature extraction, Euclidean distance matching, and full FAR/FRR/EER evaluation. *Baseline EER: 35.80%.*
- **Phase 2 — Multimodal Fusion.** A second fingerprint pipeline (Kaggle dataset) is matched using a dedicated minutiae-based engine, then fused with the facial scores via weighted score-level fusion (60% Face / 40% Fingerprint), substantially lowering the EER.
- **Phase 3 — Cryptographic Vault.** AES encryption (via Python's `cryptography.fernet`) locks every stored biometric template (`.npy`) into an encrypted `.enc` payload, accessible only through an authorized CLI.

---

## Features

- ✅ Face image preprocessing (grayscale, resize, normalize, contrast enhancement)
- ✅ ORB-based facial feature extraction
- ✅ Minutiae-based fingerprint feature extraction
- ✅ Biometric template generation and storage
- ✅ 1:1 Verification ("Is this really Person X?")
- ✅ 1:N Identification ("Who is this person?")
- ✅ Configurable, sweepable security thresholds
- ✅ FAR, FRR, and EER calculation
- ✅ ROC and DET curve visualization
- ✅ Multimodal score-level fusion (face + fingerprint)
- ✅ AES (Fernet) template encryption with CLI-controlled vault access

---

## Dataset

**Primary — Face:** Live webcam captures, organized per subject into enrollment and test sets (a 60/40 split).

**Secondary — Fingerprint:** [Kaggle fingerprint dataset](https://www.kaggle.com/datasets/kundurunonieshreddy/finger-print-dataset).

**Reference / substitute dataset — ORL Face Database** (AT&T Database of Faces), used as a standardized benchmark and fallback when live capture isn't available:

- 40 subjects × 10 images each = 400 total images
- 92×112 pixels, grayscale, PGM format
- Natural variation in lighting, expression, and pose
- 📥 [Download on Kaggle](https://www.kaggle.com/datasets/tavarez/the-orl-database-for-training-and-testing)

| Set | Images Used | Purpose |
|---|---|---|
| Enrollment Set | img1, img2 per person | Registration / template creation |
| Test Set | img3+ per person | Verification / identification |

---

## Tech Stack

| Tool / Library | Purpose |
|---|---|
| **Python 3.x** | Core programming language |
| **OpenCV (`cv2`)** | Image loading, preprocessing, feature extraction |
| **NumPy** | Numerical operations, score arrays, vector math |
| **Matplotlib** | ROC/DET curve and FAR–FRR graph plotting |
| **cryptography (Fernet)** | AES encryption of biometric templates at rest |

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/AbeEgbezien06/Biometric-security-project-CYB-302-.git
cd Biometric-security-project-CYB-302-
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```
or manually:
```bash
pip install opencv-python numpy matplotlib cryptography
```

**3. Download the datasets**

- Face (ORL reference set): [Kaggle — ORL Database](https://www.kaggle.com/datasets/tavarez/the-orl-database-for-training-and-testing) → place in `biometric-data/`
- Fingerprint: [Kaggle — Fingerprint Dataset](https://www.kaggle.com/datasets/kundurunonieshreddy/finger-print-dataset) → place in `biometric-data/fingerprints/`

---

## How It Works

### 1. Data Preparation

`task1_data_pipeline.py` initializes the `biometric_data/` directory tree and captures live facial images via webcam, routing frames into `enrollment_set/` or `test_set/` subdirectories on a 60% / 40% split.

Images are reviewed for common quality issues that degrade downstream matching:

- Blurry captures
- Poor or uneven lighting
- Partial occlusion
- Unusual head angles

**Why this matters:** weak image quality leads to unreliable feature extraction, which directly inflates both false acceptances and false rejections later in the pipeline.

### 2. Image Preprocessing

Each image passes through a standardized pipeline before feature extraction:

- Grayscale conversion
- Resize to a consistent 340×240 aspect ratio
- Histogram equalization (contrast enhancement)
- Pixel normalization
- Noise reduction

### 3. Feature Extraction & Template Generation

Images are converted into compact numerical vectors called **biometric templates**. For faces, **ORB (Oriented FAST and Rotated BRIEF)** detects spatially invariant keypoints and computes binary descriptors; these descriptors are the template, stored as `.npy` files on disk.

> **Raw Image vs. Template:** A raw image is the actual photo. A biometric template is a compact mathematical representation of that photo — smaller, faster to compare, and far safer to store.

### 4. Matching & Score Generation

`task4_euclidean_matching.py` runs full 1:N comparisons ,every test probe against every enrolled template — using **Euclidean distance**. Same-subject comparisons populate `genuine_scores.npy`; cross-subject comparisons populate `impostor_scores.npy`.

- **Verification (1:1):** "Is this really Person X?"
- **Identification (1:N):** "Who is this person?"

**Similarity measures used:**

| Measure | Direction |
|---|---|
| Euclidean Distance | Lower score = stronger match |
| Hamming / Minutiae Similarity | Higher score = stronger match |

### 5. Threshold Testing

A threshold determines whether a match score is accepted or rejected:

```
If Score ≥ Threshold → ACCEPT (person verified)
If Score < Threshold → REJECT (person denied)
```

**Phase 1 — Proof of Concept:** a single fixed threshold (e.g., T = 15) is tested against individual scores to demonstrate a basic Accept/Reject decision.

**Phase 2 — Full Threshold Sweep:** the threshold is automatically swept from 0 up to the highest recorded score. At each step, the system counts how many impostors got through and how many genuine users were locked out, mapping the complete FAR/FRR trade-off.

| Threshold | Effect | Best suited for |
|---|---|---|
| Low (e.g., T = 2 / 0.50) | Easy access, but lets more impostors through (high FAR) | Low-risk settings — e.g. a cafeteria |
| High (e.g., T = 25 / 0.90) | Blocks impostors, but locks out real users more often (high FRR) | High-risk settings — e.g. a security operations center |

Thresholds tested for the fused system: `0.50, 0.60, 0.70, 0.80, 0.90`.

### 6. Performance Evaluation

`task6_performance.py` locates the **Equal Error Rate (EER)** — the threshold at which FAR = FRR — and renders ROC and DET curves. The unimodal facial baseline settled at **EER = 35.80%**.

Running this stage produces two graphs:

1. **FAR vs. FRR Graph** : as the threshold rises, FAR falls toward zero while FRR climbs. The crossing point is the EER, the optimal balance between security and usability for this dataset. A clean crossing confirms the ORB + Euclidean pipeline is functioning correctly.
2. **ROC Curve** : plots Genuine Acceptance Rate against False Acceptance Rate. A curve bending toward the top-left corner means the system reliably accepts real users well before it starts accepting impostors.

**Core metrics:**

**FAR — False Acceptance Rate** — percentage of impostors incorrectly accepted
```
FAR = False Acceptances / Total Impostor Attempts
```

**FRR — False Rejection Rate** — percentage of genuine users incorrectly rejected
```
FRR = False Rejections / Total Genuine Attempts
```

**EER — Equal Error Rate** — the threshold where FAR = FRR. Lower EER = stronger system.

**Visualizations generated:**

- 📈 ROC Curve — True Positive Rate vs. False Positive Rate
- 📉 DET Curve — FRR vs. FAR (log scale)

```python
import matplotlib.pyplot as plt
# Plots generated using matplotlib and saved to outputs/
```

### 7. Multimodal Biometrics — Fusing Face and Fingerprint

To improve on the face-only baseline, a second biometric modality — fingerprint matching — was developed and fused with the facial scores for stronger, more spoof-resistant authentication.

#### 7a. From ORB to a Domain-Specific Minutiae Engine

The fingerprint pipeline initially reused the same **ORB** feature extractor built for faces. While computationally efficient, ORB evaluates general image contrast and keypoints rather than true physiological structure making it sensitive to environmental noise such as sensor artifacts and lighting shifts, and a weak foundation for a security-critical modality.

To harden the pipeline, this was replaced with a **purpose-built minutiae engine**. Rather than treating the fingerprint as a generic image, this engine **skeletonizes the ridge structure** and extracts the precise X/Y coordinates and angular orientation of each ridge ending and bifurcation ,the same class of features used in forensic-grade fingerprint matching. Verification then enforces strict geometric tolerances (an **L2-norm spatial distance**) alongside angular thresholds when comparing minutiae sets, producing a similarity score that is mathematically far more resistant to spoofing than a generic keypoint comparison.

#### 7b. Resolving the Fusion Logic

Combining the facial and fingerprint pipelines (`task7b_multimodal_fusion.py`) surfaced two subtle but important engineering issues:

**Metric direction.** The fusion logic was initially built on the assumption that the two pipelines produced *opposing* metrics , Euclidean distance for faces (where a *lower* score means a stronger match) against a similarity score for fingerprints (where a *higher* score means a stronger match). On closer inspection of the ORB output, both pipelines were found to behave as similarity metrics in practice. The scalar inversion that had been built into the normalization step was removed accordingly, so that strong genuine matches from both modalities reinforce each other instead of partially canceling out.

**Normalization scope.** Early fusion attempts normalized the genuine and impostor score arrays *independently*. This silently distorted the data pushing the highest-scoring impostors up to 1.0 and the lowest-scoring genuine users down to 0.0 , which collapsed the very separation the system depends on. The fix was to switch to **Global Min-Max Normalization**: computing a single minimum and maximum across the *entire* dataset before scaling either class, which preserves the true variance and relative ranking of every score.

Once corrected, scores are fused with a weighted sum:

```
Fused Score = (0.6 × Face Score) + (0.4 × Fingerprint Score)
```

#### 7c. The Payoff: A Clean Bimodal Separation

With global normalization in place, the fused score distribution becomes strongly **bimodal** : genuine users cluster tightly near the top of the scale, impostors cluster near the bottom, with a wide, clean margin between them. This is exactly what `task7c_comparative_evaluation.py` needs: instead of judging the system against one static Accept/Reject cutoff, it can sweep the decision threshold across that margin and trace out the full FAR/FRR trade-off for the fused system.

**Result:** comparing the fused ROC curve against the face-only baseline shows a substantially lower Equal Error Rate - confirming that fusing two independent biometrics, once correctly normalized, makes the system both more accurate and harder to fool than either modality alone.

> **Why multimodal?** If one biometric underperforms (e.g., a smudged fingerprint or poor lighting on a face), the second modality acts as a fallback - improving both accuracy and resistance to spoofing.

### 8. Security & Encryption

Faces and fingerprints can't be "reset" the way a password can, so the stored templates need strong protection at rest. `task8_template_security.py` applies AES symmetric encryption (via `cryptography.fernet`) to every `.npy` template matrix, locking it into a `.enc` payload. Even if the database is exfiltrated, the templates inside remain cryptographically unreadable without the vault key.

Two protections work together here:

1. **AES (Fernet) encryption**, exposed through a command-line interface built with `argparse`. Separate `--encrypt` and `--decrypt` flags ensure the two operations can never run together, so the database can't accidentally be left in a partially-encrypted or exposed state.
2. **Cancelable biometrics** : templates are passed through a one-way, irreversible transformation before storage. If the database is ever compromised, administrators can revoke the affected templates and re-enroll the user under a new transformation  effectively a "password reset" for biometric credentials.

---

## Performance Metrics

| Threshold | FAR | FRR | Notes |
|---|---|---|---|
| 0.50 | High | Low | Too permissive |
| 0.70 | Medium | Medium | Balanced |
| **EER Point** | **FAR = FRR** | **FAR = FRR** | Optimal operating point |
| 0.90 | Low | High | Too restrictive |

**Unimodal facial baseline EER: 35.80%** — substantially reduced by the fused face + fingerprint system after the normalization and metric-direction fixes described above.

---

## Project Timeline

| Week | Tasks |
|---|---|
| Week 1 | Download datasets, organize data, preprocess images, capture screenshots |
| Week 2 | Extract features, run matching, sweep thresholds |
| Week 3 | Calculate FAR/FRR/EER, generate graphs, build fusion + security layers, write up report |

---

## References

- ORL Face Database : [Kaggle](https://www.kaggle.com/datasets/tavarez/the-orl-database-for-training-and-testing)
- Fingerprint Dataset : [Kaggle](https://www.kaggle.com/datasets/kundurunonieshreddy/finger-print-dataset)
- OpenCV Documentation : [docs.opencv.org](https://docs.opencv.org)
- cryptography (Fernet) : [cryptography.io](https://cryptography.io)

---

## License

This project was developed for academic purposes (CYB-302). Dataset usage is subject to the original dataset license terms (ORL Database, Kaggle Fingerprint Dataset).
