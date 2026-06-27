import cv2
import os
import numpy as np

# --- 1. DIRECTORY CONFIGURATION ---
BASE_DIR = "biometric_data"
FP_DIR = os.path.join(BASE_DIR, "kaggle_fingerprints")

def run_fingerprint_megascript():
    print("\n[*] Booting Task 7A: Parallel Fingerprint Pipeline...")
    
    if not os.path.exists(FP_DIR) or not os.listdir(FP_DIR):
        print(f"[-] Error: Fingerprint dataset not found at {FP_DIR}")
        print("[-] Please extract your Kaggle fingerprint folders there.")
        return

    # Initialize ORB (Tuned for high-contrast ridge detection)
    orb = cv2.ORB_create(nfeatures=500, edgeThreshold=15, patchSize=15)
    
    # Fingerprints require Hamming distance because ORB outputs binary descriptors
    bf_matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    fp_genuine_scores = []
    fp_impostor_scores = []

    # Get all subjects in the fingerprint dataset
    subjects = [d for d in os.listdir(FP_DIR) if os.path.isdir(os.path.join(FP_DIR, d))]
    
    # We will limit to 20 subjects to ensure the script runs quickly for testing
    subjects = subjects[:20] 

    print(f"[*] Processing {len(subjects)} subjects. Applying Binarization and ORB Extraction...")

    # A dictionary to hold the mathematical template for each subject
    fp_database = {}

    # --- PHASE 1: ENROLMENT (Extracting the baseline) ---
    for subject in subjects:
        subj_dir = os.path.join(FP_DIR, subject)
        images = [f for f in os.listdir(subj_dir) if f.endswith(('.png', '.jpg', '.bmp'))]
        
        if len(images) >= 2:
            # Take the first image as the Enrolment baseline
            enrol_img_path = os.path.join(subj_dir, images[0])
            img = cv2.imread(enrol_img_path, cv2.IMREAD_GRAYSCALE)
            
            # Preprocessing specifically for fingerprints
            # 1. CLAHE to maximize ridge contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            contrasted = clahe.apply(img)
            # 2. Binary Thresholding (Pure black and white)
            _, binarized = cv2.threshold(contrasted, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            
            _, descriptors = orb.detectAndCompute(binarized, None)
            
            if descriptors is not None:
                fp_database[subject] = descriptors

    # --- PHASE 2: MATCHING (Generating Probes and Calculating Scores) ---
    print("[*] Enrolment complete. Commencing matching phase...")
    
    for probe_subject in subjects:
        subj_dir = os.path.join(FP_DIR, probe_subject)
        images = [f for f in os.listdir(subj_dir) if f.endswith(('.png', '.jpg', '.bmp'))]
        
        # Start from the second image (leaving the first for enrolment)
        for img_name in images[1:4]: 
            probe_path = os.path.join(subj_dir, img_name)
            img = cv2.imread(probe_path, cv2.IMREAD_GRAYSCALE)
            
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            contrasted = clahe.apply(img)
            _, binarized = cv2.threshold(contrasted, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            
            _, probe_desc = orb.detectAndCompute(binarized, None)
            if probe_desc is None: continue

            # Compare the probe against the entire fingerprint database
            for enrol_subject, enrol_desc in fp_database.items():
                try:
                    matches = bf_matcher.match(probe_desc, enrol_desc)
                    score = len(matches) # The Hamming match count
                    
                    if probe_subject == enrol_subject:
                        fp_genuine_scores.append(score)
                    else:
                        fp_impostor_scores.append(score)
                except Exception:
                    pass

    # --- PHASE 3: CACHING THE ARRAYS ---
    print("\n" + "="*50)
    print("TASK 7A: FINGERPRINT PIPELINE RESULTS")
    print("="*50)
    print(f"Total FP Genuine Comparisons:  {len(fp_genuine_scores)}")
    if fp_genuine_scores:
        print(f"Average FP Genuine Score:      {np.mean(fp_genuine_scores):.2f} matches")
        
    print(f"Total FP Impostor Comparisons: {len(fp_impostor_scores)}")
    if fp_impostor_scores:
        print(f"Average FP Impostor Score:     {np.mean(fp_impostor_scores):.2f} matches")
    print("="*50)

    np.save("fp_genuine_scores.npy", fp_genuine_scores)
    np.save("fp_impostor_scores.npy", fp_impostor_scores)
    print("[+] Fingerprint score matrices saved to disk. Ready for Fusion.")

if __name__ == "__main__":
    run_fingerprint_megascript()