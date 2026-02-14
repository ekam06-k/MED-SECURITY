import sys
import os
import subprocess
import tkinter as tk

def install_requirements():
    print("Checking dependencies...")
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    try:
        import cv2
        import cv2.face # Check for contrib
        import pynput
        print("Dependencies OK.")
    except ImportError as e:
        print(f"Missing dependency ({e}). Installing from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        print("Dependencies installed. Launching...")

def main():
    from src.config import BASE_DIR
    print(f"Starting MedGuard Sentinel (Lightweight Mode) from {BASE_DIR}")
    
    from src.ui_manager import MedGuardApp
    
    app = MedGuardApp()
    app.mainloop()

if __name__ == "__main__":
    try:
        install_requirements()
        main()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
