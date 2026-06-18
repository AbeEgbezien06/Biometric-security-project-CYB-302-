import numpy as np
import matplotlib.pyplot as plt
import os

# --- DATA INGESTION ---
GENUINE_FILE = "genuine_scores.npy"
IMPOSTOR_FILE = "impostor_scores.npy"

def load_cached_scores():
    if not os.path.exists(GENUINE_FILE) or not os.path.exists(IMPOSTOR_FILE):
        print("[-] Error: Score caches missing. Please run Task 4 first.")
        return None, None
    return np.load(GENUINE_FILE), np.load(IMPOSTOR_FILE)

def calculate_metrics_and_plot(genuine_scores, impostor_scores):
    print("\n[*] Booting Performance Evaluation Engine...")
    
    total_gen = len(genuine_scores)
    total_imp = len(impostor_scores)
    
    max_score = int(max(np.max(genuine_scores), np.max(impostor_scores)))
    
    # Generate 500 threshold points between 0 and the max score for smooth curves
    thresholds = np.linspace(0, max_score, 500) 
    
    far_list = []
    frr_list = []
    gar_list = [] 

    # Calculate metrics mathematically across the threshold sweep
    for t in thresholds:
        far = np.sum(impostor_scores >= t) / total_imp
        far_list.append(far)
        
        frr = np.sum(genuine_scores < t) / total_gen
        frr_list.append(frr)
        
        gar = np.sum(genuine_scores >= t) / total_gen
        gar_list.append(gar)

    far_array = np.array(far_list)
    frr_array = np.array(frr_list)

    # Pinpoint the Equal Error Rate (EER) where FAR and FRR intersect
    differences = np.abs(far_array - frr_array)
    eer_index = np.argmin(differences) 
    
    eer_threshold = thresholds[eer_index]
    eer_value = (far_array[eer_index] + frr_array[eer_index]) / 2

    print("\n" + "="*50)
    print("TASK 6: SYSTEM PERFORMANCE METRICS")
    print("="*50)
    print(f"[+] Equal Error Rate (EER): {eer_value * 100:.2f}%")
    print(f"[+] Optimal EER Threshold:  {eer_threshold:.2f} matches")
    print("="*50)

    # Plotting the Results
    plt.figure(figsize=(14, 6))

    # PLOT 1: FAR vs FRR over Thresholds
    plt.subplot(1, 2, 1)
    plt.plot(thresholds, far_array, label='FAR (Impostors Accepted)', color='red', linewidth=2)
    plt.plot(thresholds, frr_array, label='FRR (Genuine Locked Out)', color='blue', linewidth=2)
    
    plt.plot(eer_threshold, eer_value, 'ko', markersize=8, label=f'EER ({eer_value*100:.1f}%)')
    plt.axvline(x=eer_threshold, color='k', linestyle='--', alpha=0.5)
    
    plt.title("FAR and FRR vs. Decision Threshold")
    plt.xlabel("Euclidean Matching Score Threshold")
    plt.ylabel("Error Rate")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # PLOT 2: Receiver Operating Characteristic (ROC) Curve
    plt.subplot(1, 2, 2)
    plt.plot(far_array, gar_list, color='green', linewidth=2, label='ROC Curve (System Accuracy)')
    plt.plot([0, 1], [0, 1], color='gray', linestyle='--', label='Random Guess Baseline')
    
    plt.title("Receiver Operating Characteristic (ROC)")
    plt.xlabel("False Acceptance Rate (FAR)")
    plt.ylabel("Genuine Acceptance Rate (GAR)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.suptitle("CYB 302 Lab: Biometric System Evaluation", fontsize=16)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("=== CYB 302: TASK 6 - PERFORMANCE EVALUATION ===")
    g_scores, i_scores = load_cached_scores()
    if g_scores is not None and i_scores is not None:
        calculate_metrics_and_plot(g_scores, i_scores)