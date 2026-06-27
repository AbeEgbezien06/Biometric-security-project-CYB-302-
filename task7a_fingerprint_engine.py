import os
import cv2
import math
import random
import warnings
import numpy as np
import fingerprint_feature_extractor

# --- 0. SILENCE LIBRARY WARNINGS (Clean Terminal) ---
warnings.filterwarnings("ignore", category=FutureWarning)

# --- 1. DIRECTORY CONFIGURATION ---
BASE_DIR = "biometric_data"
FP_DIR = os.path.join(BASE_DIR, "kaggle_fingerprints", "enhace_train")

# --- 2. CORE MATCHING MATH ---
def calculate_minutiae_matches(probe_minutiae, template_minutiae, spatial_tol=15, angle_tol=math.pi/6):
    """Custom Spatial Matcher."""
    matches = 0
    matched_template_indices = set()

    for p in probe_minutiae:
        for i, t in enumerate(template_minutiae):
            if i in matched_template_indices:
                continue

            dist = math.hypot(p.locX - t.locX, p.locY - t.locY)
            
            p_angle = p.Orientation[0] if isinstance(p.Orientation, list) else p.Orientation
            t_angle = t.Orientation[0] if isinstance(t.Orientation, list) else t.Orientation

            angle_diff = abs(p_angle - t_angle)
            angle_diff = min(angle_diff, math.pi - angle_diff)

            if dist < spatial_tol and angle_diff < angle_tol:
                matches += 1
                matched_template_indices.add(i)
                break
                
    return matches

# --- 3. THE API FUNCTION ---
def verify_fingerprint(probe_path, template_path):
    """Takes two image paths, extracts features, and returns the match score."""
    probe_img = cv2.imread(probe_path, cv2.IMREAD_GRAYSCALE)
    template_img = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    p_term, p_bif = fingerprint_feature_extractor.extract_minutiae_features(
        probe_img, spuriousMinutiaeThresh=10, invertImage=False, showResult=False, saveResult=False)
    
    t_term, t_bif = fingerprint_feature_extractor.extract_minutiae_features(
        template_img, spuriousMinutiaeThresh=10, invertImage=False, showResult=False, saveResult=False)

    return calculate_minutiae_matches((p_term + p_bif), (t_term + t_bif))

# --- 4. THE INTERACTIVE DEMONSTRATOR ---
def run_interactive_evaluation():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("==================================================")
    print("  CYB 302: LIVE MINUTIAE EVALUATION ENGINE")
    print("==================================================\n")
    
    if not os.path.exists(FP_DIR) or not os.listdir(FP_DIR):
        print(f"[!] ERROR: Directory '{FP_DIR}' not found.")
        return

    files = sorted([f for f in os.listdir(FP_DIR) if f.endswith(('.png', '.bmp', '.tif'))])
    print(f"[*] Loaded {len(files)} biometric templates from the database.")
    
    # --- CUSTOM USER INPUT ---
    while True:
        try:
            user_input = input("\n[?] How many interactive randomized sets would you like to run? (e.g., 10, 20): ")
            INTERACTIVE_SETS = int(user_input)
            if INTERACTIVE_SETS > 0:
                break
            else:
                print("[!] Please enter a number greater than 0.")
        except ValueError:
            print("[!] Invalid input. Please type a whole number.")

    genuine_scores = []
    impostor_scores = []
    
    print(f"\n[*] Entering Interactive Mode for {INTERACTIVE_SETS} sets...\n")

    for i in range(1, INTERACTIVE_SETS + 1):
        input(f"--- [Press ENTER to run Random Set {i}/{INTERACTIVE_SETS}] ---")
        
        # 1. GENERATE IMPOSTOR (Hackers: 2 completely different files)
        file1, file2 = random.sample(files, 2)
        sub1 = file1.split('_')[1] 
        sub2 = file2.split('_')[1]
        
        print(f"  [IMPOSTOR TEST] Comparing Subject '{sub1}' to Subject '{sub2}'...")
        imp_score = verify_fingerprint(os.path.join(FP_DIR, file1), os.path.join(FP_DIR, file2))
        impostor_scores.append(imp_score)
        print(f"  -> Match Score: {imp_score} (Should be low)\n")

        # 2. GENERATE GENUINE (Real User: Same subject)
        file3 = random.choice(files)
        sub3 = file3.split('_')[1]
        
        print(f"  [GENUINE TEST]  Comparing Subject '{sub3}' to Themselves...")
        gen_score = verify_fingerprint(os.path.join(FP_DIR, file3), os.path.join(FP_DIR, file3))
        genuine_scores.append(gen_score)
        print(f"  -> Match Score: {gen_score} (Should be high)\n")

    print("[*] Interactive demonstration complete.")
    
    # Background batch processing to ensure graph data is thick enough
    BACKGROUND_BATCH = max(0, 20 - INTERACTIVE_SETS)
    if BACKGROUND_BATCH > 0:
        print(f"[*] Running {BACKGROUND_BATCH} more sets silently in the background for graph data...")
        for _ in range(BACKGROUND_BATCH):
            f1, f2 = random.sample(files, 2)
            impostor_scores.append(verify_fingerprint(os.path.join(FP_DIR, f1), os.path.join(FP_DIR, f2)))
            f3 = random.choice(files)
            genuine_scores.append(verify_fingerprint(os.path.join(FP_DIR, f3), os.path.join(FP_DIR, f3)))

    # --- 5. FINAL OUTPUT ---
    print("\n==================================================")
    print("  PHASE 2: FINAL PIPELINE RESULTS")
    print("==================================================")
    print(f"Total FP Genuine Tests:  {len(genuine_scores)}")
    print(f"Average FP Genuine Score: {np.mean(genuine_scores):.2f} matches")
    print(f"Total FP Impostor Tests: {len(impostor_scores)}")
    print(f"Average FP Impostor Score: {np.mean(impostor_scores):.2f} matches")
    print("==================================================")

    np.save("fp_genuine_scores.npy", np.array(genuine_scores))
    np.save("fp_impostor_scores.npy", np.array(impostor_scores))
    print("[+] Matrices saved. Ready for Multimodal Fusion.")

if __name__ == "__main__":
    run_interactive_evaluation()