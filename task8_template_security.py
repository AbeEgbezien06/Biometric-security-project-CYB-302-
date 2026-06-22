import os
import argparse
from cryptography.fernet import Fernet

# --- CONFIGURATION ---
KEY_FILE = "biometric_vault.key"

# We will encrypt the master score matrices we generated earlier
TARGET_FILES = [
    "genuine_scores.npy", 
    "impostor_scores.npy", 
    "fp_genuine_scores.npy", 
    "fp_impostor_scores.npy",
    "fused_genuine_scores.npy",
    "fused_impostor_scores.npy"
]

def generate_security_key():
    """Generates a master AES encryption key for the biometric database."""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        print(f"[+] Master Security Key generated and saved to {KEY_FILE}")
    else:
        print(f"[*] Security Key already exists at {KEY_FILE}")

def load_key():
    return open(KEY_FILE, "rb").read()

def encrypt_templates():
    print("\n[*] Booting Task 8: Template Encryption Engine...")
    key = load_key()
    fernet = Fernet(key)

    for file_name in TARGET_FILES:
        if os.path.exists(file_name):
            # Read the raw, vulnerable biometric math
            with open(file_name, "rb") as file:
                original_data = file.read()
            
            # Encrypt the data
            encrypted_data = fernet.encrypt(original_data)
            
            # Overwrite the vulnerable file with the encrypted payload
            encrypted_file_name = file_name + ".enc"
            with open(encrypted_file_name, "wb") as file:
                file.write(encrypted_data)
                
            # Delete the original unencrypted file (Strict access control)
            os.remove(file_name)
            print(f"[LOCK] Encrypted and secured: {file_name} -> {encrypted_file_name}")
        else:
            print(f"[-] File not found or already encrypted: {file_name}")

def decrypt_templates():
    """Simulates an authorized system requesting access to the data."""
    print("\n[*] Simulating Authorized Access Request...")
    key = load_key()
    fernet = Fernet(key)

    for file_name in TARGET_FILES:
        encrypted_file_name = file_name + ".enc"
        if os.path.exists(encrypted_file_name):
            with open(encrypted_file_name, "rb") as file:
                encrypted_data = file.read()
                
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Restore the file for processing
            with open(file_name, "wb") as file:
                file.write(decrypted_data)
            
            # Clean up the encrypted file so we don't have duplicates
            os.remove(encrypted_file_name)
            print(f"[UNLOCK] Authorized Decryption successful: {file_name}")
        else:
            print(f"[-] Encrypted file not found or already decrypted: {encrypted_file_name}")

if __name__ == "__main__":
    print("=== CYB 302: TASK 8 - BIOMETRIC DATA PROTECTION ===")
    generate_security_key()
    
    # Build the Command Line Interface (CLI)
    parser = argparse.ArgumentParser(description="Biometric Vault Security Engine")
    parser.add_argument('--encrypt', action='store_true', help='Lock the biometric .npy templates')
    parser.add_argument('--decrypt', action='store_true', help='Unlock the .enc templates')
    
    args = parser.parse_args()

    # Trigger logic based on terminal commands
    if args.encrypt:
        encrypt_templates()
    elif args.decrypt:
        decrypt_templates()
    else:
        print("\n[!] Engine strictly requires a directive.")
        print("[!] To lock the vault run:   python task8_template_security.py --encrypt")
        print("[!] To unlock the vault run: python task8_template_security.py --decrypt")