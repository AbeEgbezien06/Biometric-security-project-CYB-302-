import cv2
import os
import numpy as np
import matplotlib.pyplot as plt

# --- 1. DIRECTORY CONFIGURATION ---
BASE_DIR = "biometric_data"
INPUT_DIRS = {
    "enrolment": os.path.join(BASE_DIR, "enrolment_set"),
    "test": os.path.join(BASE_DIR, "test_set")
}
OUTPUT_DIRS = {
    "enrolment": os.path.join(BASE_DIR, "processed_enrolment_set"),
    "test": os.path.join(BASE_DIR, "processed_test_set")
}

# Target resolution for the entire system
TARGET_SIZE = (128, 128)

def setup_processed_directories():
    """Creates the target directories for the clean data."""
    print("[*] Initializing Task 2 processed directories...")
    for path in OUTPUT_DIRS.values():
        os.makedirs(path, exist_ok=True)
    print("[+] Directories ready.")

def enhance_biometric_image(image_path):
    """
    Executes the exact pre-processing pipeline required by Task 2.
    """
    # 1. Load Image
    img = cv2.imread(image_path)
    if img is None:
        return None

    # 2. Convert to Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Resize to a consistent resolution
    resized = cv2.resize(gray, TARGET_SIZE)

    # 4. Apply Gaussian Blur to reduce noise (3x3 kernel)
    blurred = cv2.GaussianBlur(resized, (3, 3), 0)

    # 5. Apply Histogram Equalization for contrast enhancement
    equalized = cv2.equalizeHist(blurred)

    # 6. Apply Normalization (Scaling intensity values strictly between 0 and 255)
    normalized = cv2.normalize(equalized, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    return normalized

def process_and_save_dataset(dataset_type):
    """Iterates through Task 1 folders, cleans the images, and saves them."""
    input_dir = INPUT_DIRS[dataset_type]
    output_dir = OUTPUT_DIRS[dataset_type]
    
    print(f"\n[*] Booting enhancement pipeline for {dataset_type} set...")
    
    if not os.path.exists(input_dir):
        print(f"[-] Missing input directory: {input_dir}")
        return

    total_processed = 0

    for subject_folder in os.listdir(input_dir):
        subj_input_path = os.path.join(input_dir, subject_folder)
        subj_output_path = os.path.join(output_dir, subject_folder)
        
        if os.path.isdir(subj_input_path):
            os.makedirs(subj_output_path, exist_ok=True)
            
            images = [f for f in os.listdir(subj_input_path) if f.endswith(('.png', '.jpg', '.jpeg', '.pgm'))]
            
            for img_name in images:
                in_path = os.path.join(subj_input_path, img_name)
                out_path = os.path.join(subj_output_path, img_name)
                
                # Push the image through the enhancement pipeline
                clean_img = enhance_biometric_image(in_path)
                
                if clean_img is not None:
                    cv2.imwrite(out_path, clean_img)
                    total_processed += 1

    print(f"[+] Successfully enhanced and saved {total_processed} images to {output_dir}")

def visual_comparison(dataset_type="enrolment"):
    """
    Satisfies Lab Task 2.7: Visually compare original and enhanced images.
    Pulls a random image from Task 1 and compares it to its Task 2 counterpart.
    """
    input_dir = INPUT_DIRS[dataset_type]
    output_dir = OUTPUT_DIRS[dataset_type]
    
    print("\n[*] Generating visual comparison for the lab report...")
    
    # Grab the first subject we can find
    for subject_folder in os.listdir(input_dir):
        subj_input_path = os.path.join(input_dir, subject_folder)
        if os.path.isdir(subj_input_path):
            images = [f for f in os.listdir(subj_input_path) if f.endswith(('.png', '.jpg', '.jpeg', '.pgm'))]
            if images:
                target_img = images[0] # Just grab the first image
                
                raw_path = os.path.join(subj_input_path, target_img)
                clean_path = os.path.join(output_dir, subject_folder, target_img)
                
                raw_img = cv2.imread(raw_path)
                clean_img = cv2.imread(clean_path, cv2.IMREAD_GRAYSCALE)
                
                # Plotting side-by-side using Matplotlib
                plt.figure(figsize=(10, 5))
                
                # Left side: Raw Image
                plt.subplot(1, 2, 1)
                plt.imshow(cv2.cvtColor(raw_img, cv2.COLOR_BGR2RGB))
                plt.title("Original (Raw Capture)")
                plt.axis("off")
                
                # Right side: Processed Image
                plt.subplot(1, 2, 2)
                plt.imshow(clean_img, cmap='gray')
                plt.title("Enhanced (Grayscale, Blur, Equalized)")
                plt.axis("off")
                
                plt.suptitle("CYB 302 Lab: Task 2 Enhancement Comparison")
                plt.show()
                return

if __name__ == "__main__":
    print("=== CYB 302: TASK 2 - PRE-PROCESSING PIPELINE ===")
    setup_processed_directories()
    
    # 1. Process all Enrolment images
    process_and_save_dataset("enrolment")
    
    # 2. Process all Probe/Test images
    process_and_save_dataset("test")
    
    # 3. Trigger the UI pop-up to satisfy the visual comparison requirement
    visual_comparison("enrolment")
    
    print("\n[+] Task 2 Complete. Data matrices are standardized and ready for Phase 3 (Feature Extraction).")