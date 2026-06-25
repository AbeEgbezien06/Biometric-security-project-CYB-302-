import numpy as np
import os

# --- INGESTION: LOADING BOTH PARALLEL PIPELINES ---
FACE_GEN = "genuine_scores.npy"
FACE_IMP = "impostor_scores.npy"
FP_GEN = "fp_genuine_scores.npy"
FP_IMP = "fp_impostor_scores.npy"

def load_all_scores():
    files = [FACE_GEN, FACE_IMP, FP_GEN, FP_IMP]
    for f in files:
        if not os.path.exists(f):
            print(f"[-] Error: Missing {f}. Ensure Task 4 and Task 7A have been run.")
            return None, None, None, None
            
    return np.load(FACE_GEN), np.load(FACE_IMP), np.load(FP_GEN), np.load(FP_IMP)

def min_max_normalize(scores):
    """Squashes raw scores to a universal 0.0 to 1.0 mathematical scale."""
    min_val = np.min(scores)
    max_val = np.max(scores)
    if max_val == min_val:
        return np.zeros_like(scores)
    return (scores - min_val) / (max_val - min_val)

def align_array_sizes(arr1, arr2):
    """
    Because the Face dataset and Fingerprint dataset might have different numbers 
    of comparisons, we must strictly align their lengths to fuse them accurately.
    """
    min_len = min(len(arr1), len(arr2))
    # We slice both arrays down to the exact same size
    return arr1[:min_len], arr2[:min_len]

def execute_fusion():
    print("\n[*] Booting Task 7B: Multimodal Fusion Engine...")
    
    face_g, face_i, fp_g, fp_i = load_all_scores()
    if face_g is None: return

    # 1. Size Alignment
    print("[*] Aligning dataset matrix sizes...")
    face_g_aligned, fp_g_aligned = align_array_sizes(face_g, fp_g)
    face_i_aligned, fp_i_aligned = align_array_sizes(face_i, fp_i)

    # 2. Min-Max Normalization
    print("[*] Normalizing disparate metrics to 0.0 - 1.0 scale...")
    norm_face_g = min_max_normalize(face_g_aligned)
    norm_face_i = min_max_normalize(face_i_aligned)
    
    norm_fp_g = min_max_normalize(fp_g_aligned)
    norm_fp_i = min_max_normalize(fp_i_aligned)

    # 3. Score-Level Fusion (Weighted Sum)
    # Architecture Decision: We trust the Face pipeline 60%, Fingerprint 40%
    WEIGHT_FACE = 0.6
    WEIGHT_FP = 0.4
    
    fused_genuine = (norm_face_g * WEIGHT_FACE) + (norm_fp_g * WEIGHT_FP)
    fused_impostor = (norm_face_i * WEIGHT_FACE) + (norm_fp_i * WEIGHT_FP)

    # --- REPORT GENERATION ---
    print("\n" + "="*60)
    print("TASK 7: MULTIMODAL SCORE-LEVEL FUSION RESULTS")
    print("="*60)
    print(f"[+] Architecture: Parallel Processing Pipelines")
    print(f"[+] Normalization Algorithm: Min-Max Scaling")
    print(f"[+] Fusion Rule: Weighted Sum ({WEIGHT_FACE*100}% Face | {WEIGHT_FP*100}% Fingerprint)")
    print("-" * 60)
    print(f"Average FUSED Genuine Score:  {np.mean(fused_genuine):.4f} (Closer to 1.0 is better)")
    print(f"Average FUSED Impostor Score: {np.mean(fused_impostor):.4f} (Closer to 0.0 is better)")
    print("="*60)
    
    # Save the final fused arrays so you can plot a new ROC curve if desired
    np.save("fused_genuine_scores.npy", fused_genuine)
    np.save("fused_impostor_scores.npy", fused_impostor)
    print("[+] Fusion complete. Output cached successfully.")

if __name__ == "__main__":
    execute_fusion()