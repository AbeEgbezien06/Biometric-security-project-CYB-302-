import cv2
import os
import numpy as np

# --- 1. DIRECTORY CONFIGURATION ---
BASE_DIR = "biometric_data"
PROCESSED_ENROLMENT_DIR = os.path.join(BASE_DIR, "processed_enrolment_set")
TEMPLATE_DB_DIR = os.path.join(BASE_DIR, "template_database")

def setup_database_directory():
    """Creates the vault for our numerical templates."""
    print("[*] Initializing Template Database directory...")
    os.makedirs(TEMPLATE_DB_DIR, exist_ok=True)
    print("[+] Directory ready.")

def extract_and_save_templates():
    """
    Reads clean images, extracts ORB features, and saves them as .npy vectors.
    """
    print("\n[*] Booting Feature Extraction Engine (ORB)...")
    
    if not os.path.exists(PROCESSED_ENROLMENT_DIR):
        print(f"[-] Error: Processed data missing at {PROCESSED_ENROLMENT_DIR}")
        return

    # Initialize the ORB detector to find the top 500 most distinct features per image
    orb = cv2.ORB_create(nfeatures=500)
    total_templates = 0

    for subject_folder in os.listdir(PROCESSED_ENROLMENT_DIR):
        subj_input_path = os.path.join(PROCESSED_ENROLMENT_DIR, subject_folder)
        subj_db_path = os.path.join(TEMPLATE_DB_DIR, subject_folder)
        
        if os.path.isdir(subj_input_path):
            os.makedirs(subj_db_path, exist_ok=True)
            
            images = [f for f in os.listdir(subj_input_path) if f.endswith(('.png', '.jpg', '.jpeg', '.pgm'))]
            
            for img_name in images:
                in_path = os.path.join(subj_input_path, img_name)
                
                # Load the pre-processed grayscale image
                img = cv2.imread(in_path, cv2.IMREAD_GRAYSCALE)
                
                # Extract keypoints and compute the mathematical descriptors
                keypoints, descriptors = orb.detectAndCompute(img, None)
                
                # If the algorithm found features, save the descriptor matrix
                if descriptors is not None:
                    # Strip the image extension and replace with .npy
                    base_name = os.path.splitext(img_name)[0]
                    template_filename = f"{base_name}_template.npy"
                    out_path = os.path.join(subj_db_path, template_filename)
                    
                    # Save the raw mathematical vector to disk
                    np.save(out_path, descriptors)
                    total_templates += 1
                else:
                    print(f"[-] Warning: No features detected in {img_name}")

    print(f"\n[+] Extraction Complete. {total_templates} biometric templates securely generated and saved to {TEMPLATE_DB_DIR}.")

def analyze_template_size():
    """
    Satisfies Lab Task 3.5: Analyze template size and discuss storage implications.
    Compares the file size of a raw image vs its mathematical template.
    """
    print("\n[*] Analyzing Storage Implications for Lab Report...")
    
    # Grab the first subject to compare sizes
    for subject_folder in os.listdir(PROCESSED_ENROLMENT_DIR):
        img_dir = os.path.join(PROCESSED_ENROLMENT_DIR, subject_folder)
        tpl_dir = os.path.join(TEMPLATE_DB_DIR, subject_folder)
        
        if os.path.isdir(img_dir) and os.path.isdir(tpl_dir):
            images = os.listdir(img_dir)
            templates = os.listdir(tpl_dir)
            
            if images and templates:
                img_path = os.path.join(img_dir, images[0])
                tpl_path = os.path.join(tpl_dir, templates[0])
                
                img_size_kb = os.path.getsize(img_path) / 1024
                tpl_size_kb = os.path.getsize(tpl_path) / 1024
                
                print("-" * 50)
                print(f"Processed Image Size: {img_size_kb:.2f} KB")
                print(f"Numerical Template Size (.npy): {tpl_size_kb:.2f} KB")
                print("-" * 50)
                print("Take note of these numbers for your group's final report!")
                return

if __name__ == "__main__":
    print("=== CYB 302: TASK 3 - FEATURE EXTRACTION ===")
    setup_database_directory()
    extract_and_save_templates()
    analyze_template_size()