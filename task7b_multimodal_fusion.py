import numpy as np
import os

# --- INGESTION ---
FACE_GEN = "genuine_scores.npy"
FACE_IMP = "impostor_scores.npy"
FP_GEN = "fp_genuine_scores.npy"
FP_IMP = "fp_impostor_scores.npy"

def load_all_scores():
    files = [FACE_GEN, FACE_IMP, FP_GEN, FP_IMP]
    for f in files:
        if not os.path.exists(f):
            print(f"[-] Error: Missing {f}. Ensure Phase 1 and Phase 2 have been run.")
            return None, None, None, None
            
    return np.load(FACE_GEN), np.load(FACE_IMP), np.load(FP_GEN), np.load(FP_IMP)

def align_array_sizes(arr1, arr2):
    min_len = min(len(arr1), len(arr2))
    return arr1[:min_len], arr2[:min_len]

# --- THE GLOBAL NORMALIZATION FIX (NO INVERSION) ---
def global_min_max_normalize(scores, global_min, global_max):
    """Normalizes using the GLOBAL min and max."""
    if global_max == global_min:
        return np.zeros_like(scores)
    return (scores - global_min) / (global_max - global_min)

def execute_fusion():
    print("\n[*] Booting Task 7B: Multimodal Fusion Engine...")
    
    face_g, face_i, fp_g, fp_i = load_all_scores()
    if face_g is None: return

    # 1. Size Alignment
    print("[*] Aligning dataset matrix sizes...")
    face_g_aligned, fp_g_aligned = align_array_sizes(face_g, fp_g)
    face_i_aligned, fp_i_aligned = align_array_sizes(face_i, fp_i)

    # 2. Find GLOBAL Minimums and Maximums
    print("[*] Calculating Global Dataset Bounds...")
    global_face_min = min(np.min(face_g_aligned), np.min(face_i_aligned))
    global_face_max = max(np.max(face_g_aligned), np.max(face_i_aligned))
    
    global_fp_min = min(np.min(fp_g_aligned), np.min(fp_i_aligned))
    global_fp_max = max(np.max(fp_g_aligned), np.max(fp_i_aligned))

    # 3. Normalization (Straight Scaling, NO INVERSIONS)
    print("[*] Applying GLOBAL Min-Max Normalization...")
    
    # Face (ORB Similarity) -> Higher is Better
    norm_face_g = global_min_max_normalize(face_g_aligned, global_face_min, global_face_max)
    norm_face_i = global_min_max_normalize(face_i_aligned, global_face_min, global_face_max)
    
    # Fingerprint (Minutiae Similarity) -> Higher is Better
    norm_fp_g = global_min_max_normalize(fp_g_aligned, global_fp_min, global_fp_max)
    norm_fp_i = global_min_max_normalize(fp_i_aligned, global_fp_min, global_fp_max)

    # 4. Score-Level Fusion (Weighted Sum)
    WEIGHT_FACE = 0.6
    WEIGHT_FP = 0.4
    
    fused_genuine = (norm_face_g * WEIGHT_FACE) + (norm_fp_g * WEIGHT_FP)
    fused_impostor = (norm_face_i * WEIGHT_FACE) + (norm_fp_i * WEIGHT_FP)

    # --- REPORT GENERATION ---
    print("\n" + "="*60)
    print("TASK 7: MULTIMODAL SCORE-LEVEL FUSION RESULTS")
    print("="*60)
    print(f"[+] Architecture: Parallel Processing Pipelines")
    print(f"[+] Normalization Algorithm: GLOBAL Min-Max Scaling")
    print(f"[+] Fusion Rule: Weighted Sum ({WEIGHT_FACE*100}% Face ORB | {WEIGHT_FP*100}% Fingerprint Minutiae)")
    print("-" * 60)
    print(f"Average FUSED Genuine Score:  {np.mean(fused_genuine):.4f} (Closer to 1.0 is better)")
    print(f"Average FUSED Impostor Score: {np.mean(fused_impostor):.4f} (Closer to 0.0 is better)")
    print("="*60)
    
    np.save("fused_genuine_scores.npy", fused_genuine)
    np.save("fused_impostor_scores.npy", fused_impostor)
    print("[+] Fusion complete. Output cached successfully.")

if __name__ == "__main__":
    execute_fusion()