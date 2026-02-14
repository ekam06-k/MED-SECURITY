import os
import cv2

# Base Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "medguard.db")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
BREACH_DIR = os.path.join(LOGS_DIR, "breach_images")
SIGNUP_LOG_DIR = os.path.join(LOGS_DIR, "signup_images")
TRAINER_PATH = os.path.join(BASE_DIR, "database", "trainer.yml")
FACES_DIR = os.path.join(BASE_DIR, "dataset")

# Ensure directories exist
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(BREACH_DIR, exist_ok=True)
os.makedirs(SIGNUP_LOG_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)

# System Constants
MAX_BUFFER_SIZE = 30
LOCKDOWN_TIMEOUT = 10  # Seconds allowed to re-authenticate
GHOST_INPUT_THRESHOLD = 5  # Seconds of no face before input triggers lock
ABSENCE_LOCK_TIMEOUT = 10 # Seconds of no face before auto-lock
CAMERA_INDEX = 0

# Security
MAC_LOCK_ENABLED = True
CONFIDENCE_THRESHOLD = 125  # Relaxed slightly for smoother unlock

# Resources
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
