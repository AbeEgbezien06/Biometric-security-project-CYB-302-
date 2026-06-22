import numpy as np
import os

# --- DATA INGESTION ---
GENUINE_FILE = "genuine_scores.npy"
IMPOSTOR_FILE = "impostor_scores.npy"

def load_cached_scores():
    if not os.path.exists(GENUINE_FILE) or not os.path.exists(IMPOSTOR_FILE):
        print("[-] Error: Score caches missing. Please run Task 4 first.")
        return None, None
    return np.load(GENUINE_FILE), np.load(IMPOSTOR_FILE)

def classify_accept_reject(genuine_scores, impostor_scores, initial_threshold=15):
    """
    Satisfies Lab Task 5.1 & 5.2: Define initial threshold and classify outcomes.
    """
    print(f"\n[*] PHASE 1: Defining Initial Threshold (T = {initial_threshold})")
    print("[*] Classifying Match Outcomes (Accept / Reject)...")
    
    # Show classification for a small sample of Genuine users
    print("\n--- Genuine User Attempts (Should be ACCEPTED) ---")
    for i, score in enumerate(genuine_scores[:5]): 
        decision = "ACCEPT (Access Granted)" if score >= initial_threshold else "REJECT (False Rejection)"
        print(f"Genuine User {i+1} | Score: {score:>3} | Decision: {decision}")

    # Show classification for a small sample of Impostors
    print("\n--- Impostor User Attempts (Should be REJECTED) ---")
    for i, score in enumerate(impostor_scores[:5]):
        decision = "ACCEPT (False Acceptance Risk)" if score >= initial_threshold else "REJECT (Access Denied)"
        print(f"Impostor {i+1}     | Score: {score:>3} | Decision: {decision}")

def sweep_threshold_range(genuine_scores, impostor_scores):
    """
    Satisfies Lab Task 5.3 & 5.4: Vary threshold and record changes.
    """
    print("\n[*] PHASE 2: Sweeping Threshold Across Defined Range...")
    
    min_score = 0
    max_score = int(max(np.max(genuine_scores), np.max(impostor_scores)))
    
    total_gen = len(genuine_scores)
    total_imp = len(impostor_scores)
    
    print("\n" + "="*75)
    print(f"{'Threshold':<10} | {'Impostors ACCEPTED (FAR Risk)':<32} | {'Genuine REJECTED (FRR Risk)'}")
    print("="*75)

    # Sweep from 0 to the max score, stepping by 2
    for threshold in range(min_score, max_score + 2, 2):
        false_accepts = np.sum(impostor_scores >= threshold)
        false_rejects = np.sum(genuine_scores < threshold)
        
        far_pct = (false_accepts / total_imp) * 100 if total_imp else 0
        frr_pct = (false_rejects / total_gen) * 100 if total_gen else 0
        
        print(f" T = {threshold:<5} | {false_accepts:>4} bypassed gate ({far_pct:>5.1f}%)   | {false_rejects:>4} locked out ({frr_pct:>5.1f}%)")

    print("="*75)
    print("[!] Use Phase 1 output to show classification, and Phase 2 table to show outcome changes.")

if __name__ == "__main__":
    print("=== CYB 302: TASK 5 - THRESHOLD DECISION ANALYSIS ===")
    g_scores, i_scores = load_cached_scores()
    
    if g_scores is not None and i_scores is not None:
        classify_accept_reject(g_scores, i_scores, initial_threshold=15)
        sweep_threshold_range(g_scores, i_scores)