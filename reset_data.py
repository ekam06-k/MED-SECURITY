import os
import shutil
import sys

# Add src to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

try:
    from src.config import DB_PATH, FACES_DIR, TRAINER_PATH, LOGS_DIR, BASE_DIR
except ImportError:
    # Fallback if running from root
    from MedGuard_Core.src.config import DB_PATH, FACES_DIR, TRAINER_PATH, LOGS_DIR, BASE_DIR

def reset_system():
    print("WARNING: This will DELETE ALL USERS, FACES, LOGS, and DATABASE ENTRIES.")
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm != "DELETE":
        print("Aborted.")
        return

    print("\n[1/4] Cleaning Database...")
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"  - Deleted {DB_PATH}")
        except Exception as e:
            print(f"  - Error: {e}")
    else:
        print("  - Database not found (skipped).")

    print("\n[2/4] Cleaning Face Dataset...")
    if os.path.exists(FACES_DIR):
        try:
            shutil.rmtree(FACES_DIR)
            os.makedirs(FACES_DIR)
            print(f"  - Wiped {FACES_DIR}")
        except Exception as e:
            print(f"  - Error: {e}")

    print("\n[3/4] Cleaning Logs (Breaches & Signups)...")
    if os.path.exists(LOGS_DIR):
        try:
            shutil.rmtree(LOGS_DIR)
            os.makedirs(LOGS_DIR)
            print(f"  - Wiped {LOGS_DIR}")
        except Exception as e:
             print(f"  - Error: {e}")

    print("\n[4/4] Removing Trained Model...")
    if os.path.exists(TRAINER_PATH):
        try:
            os.remove(TRAINER_PATH)
            print(f"  - Deleted {TRAINER_PATH}")
        except Exception as e:
            print(f"  - Error: {e}")

    print("\nSUCCESS: System Factory Reset Complete.")
    print("You can now restart main.py to register a fresh admin user.")

if __name__ == "__main__":
    reset_system()
