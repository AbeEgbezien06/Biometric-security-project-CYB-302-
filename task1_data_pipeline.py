import cv2
import os
import shutil
import time
import random

# --- DIRECTORY CONFIGURATION ---
BASE_DIR = "biometric_data"
LIVE_CAPTURE_DIR = os.path.join(BASE_DIR, "raw_live_captures")
DOWNLOADED_DIR = os.path.join(BASE_DIR, "kaggle_dataset") # Your Kaggle extraction target
ENROLMENT_DIR = os.path.join(BASE_DIR, "enrolment_set")
TEST_DIR = os.path.join(BASE_DIR, "test_set")

def setup_directories():
    """Builds the pipeline folders if they don't exist."""
    print("[*] Initializing directory structure...")
    for directory in [LIVE_CAPTURE_DIR, DOWNLOADED_DIR, ENROLMENT_DIR, TEST_DIR]:
        os.makedirs(directory, exist_ok=True)
    print("[+] Directories ready.")

def capture_live_samples(subject_id, num_samples=10):
    """Hooks into the webcam to collect varying samples for enrolment and testing."""
    print(f"\n[*] Starting live capture for: {subject_id}")
    print("[!] INSTRUCTIONS: Alter your lighting, angle, or distance slightly during capture.")
    time.sleep(2)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[-] Error: Could not access the webcam.")
        return

    subject_dir = os.path.join(LIVE_CAPTURE_DIR, f"subject_{subject_id}")
    os.makedirs(subject_dir, exist_ok=True)

    count = 0
    while count < num_samples:
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2.imshow("Biometric Capture - Press 'c' to capture, 'q' to quit", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            img_path = os.path.join(subject_dir, f"sample_{count+1}.jpg")
            cv2.imwrite(img_path, frame)
            print(f"[+] Captured {img_path}")
            count += 1
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"[+] Live capture complete for {subject_id}.")

def split_data_into_sets(source_directory, split_ratio=0.7):
    """Randomizes and splits data into enrolment and test sets."""
    print(f"\n[*] Partitioning data from {source_directory}...")
    
    if not os.path.exists(source_directory) or not os.listdir(source_directory):
        print(f"[-] No data found in {source_directory}. Skipping.")
        return

    for subject_folder in os.listdir(source_directory):
        subject_path = os.path.join(source_directory, subject_folder)
        
        if os.path.isdir(subject_path):
            images = [f for f in os.listdir(subject_path) if f.endswith(('.png', '.jpg', '.jpeg', '.pgm'))]
            if not images:
                continue
                
            random.shuffle(images)
            
            # Split logic
            split_idx = int(len(images) * split_ratio)
            enrolment_images = images[:split_idx]
            test_images = images[split_idx:]
            
            # Destination folders
            subj_enrol_dir = os.path.join(ENROLMENT_DIR, subject_folder)
            subj_test_dir = os.path.join(TEST_DIR, subject_folder)
            os.makedirs(subj_enrol_dir, exist_ok=True)
            os.makedirs(subj_test_dir, exist_ok=True)
            
            # Copy files over
            for img in enrolment_images:
                shutil.copy(os.path.join(subject_path, img), os.path.join(subj_enrol_dir, img))
            for img in test_images:
                shutil.copy(os.path.join(subject_path, img), os.path.join(subj_test_dir, img))
                
            print(f"[+] {subject_folder} -> {len(enrolment_images)} enrolment | {len(test_images)} test")

if __name__ == "__main__":
    print("=== CYB 302: TASK 1 - DATA PIPELINE ===")
    setup_directories()
    
    # 1. LIVE CAPTURE: Fire up the webcam and grab 10 samples
    capture_live_samples(subject_id="live_user_1", num_samples=10)
    
    # 2. PARTITION LIVE DATA: Split the webcam captures (60% enrol, 40% test)
    split_data_into_sets(LIVE_CAPTURE_DIR, split_ratio=0.6)
    
    # 3. PARTITION KAGGLE DATA: Process the downloaded dataset automatically
    split_data_into_sets(DOWNLOADED_DIR, split_ratio=0.6)
    
    print("\n[+] Task 1 Pipeline Execution Complete. Data is prepped for Phase 2.")