import cv2
import os
import numpy as np

# --- 1. DIRECTORY CONFIGURATION ---
BASE_DIR = "biometric_data"
TEST_DIR = os.path.join(BASE_DIR, "processed_test_set") 
DB_DIR = os.path.join(BASE_DIR, "template_database")    

# Initialize ORB for live probe extraction
orb = cv2.ORB_create(nfeatures=500)

# Initialize Matcher using EUCLIDEAN DISTANCE (L2 Norm)
# crossCheck=True ensures the match is highly strict (mutual nearest neighbors)
bf_matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)

def generate_probe_template(image_path):
    """Simulates a live login by extracting ORB features on the fly."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    _, descriptors = orb.detectAndCompute(img, None)
    return descriptors

def calculate_euclidean_similarity(probe_desc, enrol_desc):
    """
    Calculates the Euclidean distance between template matrices.
    Returns the number of 'good' matches that fall below a strict distance threshold.
    """
    if probe_desc is None or enrol_desc is None:
        return 0
        
    try:
        # Calculate Euclidean distances between vectors
        matches = bf_matcher.match(probe_desc, enrol_desc)
        
        # Sort them by distance (lowest distance = closest match)
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Define a strict Euclidean distance threshold
        # We only count features that are mathematically very close
        euclidean_threshold = 300 
        
        # Filter for good matches
        good_matches = [m for m in matches if m.distance < euclidean_threshold]
        
        # The similarity score is the total count of good matches
        return len(good_matches) 
    except Exception as e:
        return 0

def run_euclidean_matching_engine():
    """Executes the pipeline, logging Genuine vs Impostor Euclidean scores."""
    print("\n[*] Booting Biometric Matching Engine (Euclidean Metric)...")
    
    genuine_scores = []
    impostor_scores = []

    # Map the enrolled database
    if not os.path.exists(DB_DIR):
        print("[-] Error: template_database not found. Run Task 3.")
        return
        
    enrolled_subjects = [d for d in os.listdir(DB_DIR) if os.path.isdir(os.path.join(DB_DIR, d))]
    
    if not enrolled_subjects:
        print("[-] Database is empty.")
        return

    # Loop through the test set (Simulating live probes)
    for probe_subject in os.listdir(TEST_DIR):
        probe_subj_dir = os.path.join(TEST_DIR, probe_subject)
        
        if not os.path.isdir(probe_subj_dir):
            continue
            
        test_images = [f for f in os.listdir(probe_subj_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.pgm'))]
        
        for img_name in test_images:
            probe_path = os.path.join(probe_subj_dir, img_name)
            
            # 1. EXTRACT THE LIVE PROBE
            probe_desc = generate_probe_template(probe_path)
            if probe_desc is None:
                continue

            best_match_score = 0
            best_match_identity = "Unknown"

            # 2. COMPARE AGAINST THE ENTIRE VAULT (1:N Identification)
            for enrol_subject in enrolled_subjects:
                enrol_subj_dir = os.path.join(DB_DIR, enrol_subject)
                templates = [f for f in os.listdir(enrol_subj_dir) if f.endswith('.npy')]
                
                for tpl_name in templates:
                    enrol_path = os.path.join(enrol_subj_dir, tpl_name)
                    
                    # Load the saved .npy mathematical array
                    enrol_desc = np.load(enrol_path)
                    
                    # Calculate Euclidean similarity
                    score = calculate_euclidean_similarity(probe_desc, enrol_desc)
                    
                    # Track the highest score for identification
                    if score > best_match_score:
                        best_match_score = score
                        best_match_identity = enrol_subject

                    # 3. LOGGING FOR TASK 5 & 6
                    if probe_subject == enrol_subject:
                        genuine_scores.append(score)
                    else:
                        impostor_scores.append(score)

            # Print out the decision engine's logic in real-time
            print(f"[+] Probe: {probe_subject} | Best Match: {best_match_identity} | Score: {best_match_score}")

    # --- REPORT GENERATION ---
    print("\n" + "="*45)
    print("TASK 4: EUCLIDEAN MATCHING DISTRIBUTION")
    print("="*45)
    print(f"Total Genuine Comparisons: {len(genuine_scores)}")
    if genuine_scores:
        print(f"  -> Average Genuine Score:  {np.mean(genuine_scores):.2f} valid matches")
        print(f"  -> Minimum Genuine Score:  {np.min(genuine_scores)} valid matches")
    
    print(f"\nTotal Impostor Comparisons: {len(impostor_scores)}")
    if impostor_scores:
        print(f"  -> Average Impostor Score: {np.mean(impostor_scores):.2f} valid matches")
        print(f"  -> Maximum Impostor Score: {np.max(impostor_scores)} valid matches")
    print("="*45)
    
    # Save the raw arrays for Task 5 threshold testing
    np.save("genuine_scores.npy", genuine_scores)
    np.save("impostor_scores.npy", impostor_scores)
    print("[*] Raw score matrices saved to disk for Task 5 analysis.")

if __name__ == "__main__":
    print("=== CYB 302: TASK 4 - EUCLIDEAN MATCHING ENGINE ===")
    run_euclidean_matching_engine()
    