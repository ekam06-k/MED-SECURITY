import hashlib
import uuid
import cv2
import os
import numpy as np
from PIL import Image
from .config import TRAINER_PATH, FACES_DIR, CASCADE_PATH

class AuthManager:
    @staticmethod
    def get_mac_address():
        return uuid.getnode()

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(stored_hash, password):
        return stored_hash == hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_mac(registered_mac):
        return uuid.getnode() == registered_mac

    @staticmethod
    def save_face_samples(user_id, name, images):
        """Save captured face images for training"""
        safe_name = "".join(x for x in name if x.isalnum())
        user_dir = os.path.join(FACES_DIR, f"User_{user_id}_{safe_name}")
        os.makedirs(user_dir, exist_ok=True)
        
        detector = cv2.CascadeClassifier(CASCADE_PATH)
        count = 0
        
        for img in images:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.imwrite(os.path.join(user_dir, f"{count}.jpg"), gray[y:y+h,x:x+w])
                count += 1
        
        return count

    @staticmethod
    def train_recognizer():
        """Train LBPH Recognizer on all saved faces"""
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        faces = []
        ids = []
        
        # Walk through FACES_DIR
        for root, dirs, files in os.walk(FACES_DIR):
            for file in files:
                if file.endswith(".jpg"):
                    path = os.path.join(root, file)
                    # Extract ID from folder name 'User_{ID}_{Name}'
                    folder_name = os.path.basename(os.path.dirname(path))
                    try:
                        # Split by underscore, ID is index 1 (User, ID, Name...)
                        id_ = int(folder_name.split('_')[1])
                    except:
                        continue
                        
                    img_pil = Image.open(path).convert('L')
                    image_np = np.array(img_pil, 'uint8')
                    
                    faces.append(image_np)
                    ids.append(id_)
        
        if len(faces) > 0:
            recognizer.train(faces, np.array(ids))
            recognizer.save(TRAINER_PATH)
            return True
        return False
