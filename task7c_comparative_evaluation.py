import numpy as np
import matplotlib.pyplot as plt
import os

def calculate_roc_metrics(genuine_scores, impostor_scores):
    """Calculates FAR, FRR, and GAR across a normalized threshold range."""
    thresholds = np.linspace(0, 1, 500)
    far_list = []
    frr_list = []
    gar_list = []
    
    total_gen = len(genuine_scores)
    total_imp = len(impostor_scores)
    
    for t in thresholds:
        # Since scores are normalized 0-1, higher means more genuine match
        far = np.sum(impostor_scores >= t) / total_imp
        frr = np.sum(genuine_scores < t) / total_gen
        gar = 1.0 - frr
        
        far_list.append(far)
        frr_list.append(frr)
        gar_list.append(gar)
        
    far_arr = np.array(far_list)
    frr_arr = np.array(frr_list)
    
    # Calculate EER
    eer_idx = np.argmin(np.abs(far_arr - frr_arr))
    eer_val = (far_arr[eer_idx] + frr_arr[eer_idx]) / 2
    
    return far_arr, gar_list, eer_val

def run_comparison():
    print("\n[*] Booting Task 7C: Comparative Performance Analytics Engine...")
    
    # Check for dependencies
    required_files = ["genuine_scores.npy", "impostor_scores.npy", "fused_genuine_scores.npy", "fused_impostor_scores.npy"]
    for f in required_files:
        if not os.path.exists(f):
            print(f"[-] Missing cache file: {f}. Ensure Tasks 4, 7A, and 7B ran successfully.")
            return

    # Load and normalize original face scores to match the 0-1 scale of fused scores
    face_gen = np.load("genuine_scores.npy")
    face_imp = np.load("impostor_scores.npy")
    
    # Min-max normalize face scores internally for fair baseline graph comparison
    face_gen_norm = (face_gen - np.min(face_gen)) / (np.max(face_gen) - np.min(face_gen))
    face_imp_norm = (face_imp - np.min(face_imp)) / (np.max(face_imp) - np.min(face_imp))
    
    # Load already normalized fused scores
    fused_gen = np.load("fused_genuine_scores.npy")
    fused_imp = np.load("fused_impostor_scores.npy")

    # Compute metrics for both systems
    face_far, face_gar, face_eer = calculate_roc_metrics(face_gen_norm, face_imp_norm)
    fused_far, fused_gar, fused_eer = calculate_roc_metrics(fused_gen, fused_imp)

    print("\n" + "="*55)
    print("SYSTEM METRIC COMPARISON")
    print("="*55)
    print(f"[#] Unimodal (Face Only) EER:  {face_eer * 100:.2f}%")
    print(f"[#] Multimodal (Fused) EER:    {fused_eer * 100:.2f}%")
    print("-" * 55)
    improvement = (face_eer - fused_eer) * 100
    print(f"[+] Security Optimization: EER dropped by {improvement:.2f}%")
    print("="*55)

    # Plotting the comparative ROC Curves
    plt.figure(figsize=(9, 7))
    plt.plot(face_far, face_gar, color='red', linestyle='--', linewidth=2, label=f'Unimodal Face (EER: {face_eer*100:.1f}%)')
    plt.plot(fused_far, fused_gar, color='darkblue', linewidth=3, label=f'Multimodal Fused (EER: {fused_eer*100:.1f}%)')
    plt.plot([0, 1], [0, 1], color='gray', linestyle=':', label='Random Baseline')
    
    plt.title("ROC Performance Upgrade: Unimodal vs. Multimodal Fusion", fontsize=14)
    plt.xlabel("False Acceptance Rate (FAR)", fontsize=11)
    plt.ylabel("Genuine Acceptance Rate (GAR)", fontsize=11)
    plt.legend(loc="lower right", fontsize=11)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_comparison()