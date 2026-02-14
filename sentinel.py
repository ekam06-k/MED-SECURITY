import threading
import time
import cv2
import numpy as np
from collections import deque
from pynput import mouse, keyboard
from .config import MAX_BUFFER_SIZE, GHOST_INPUT_THRESHOLD, CAMERA_INDEX, TRAINER_PATH, CASCADE_PATH, CONFIDENCE_THRESHOLD

class Sentinel(threading.Thread):
    def __init__(self, user_id, lock_callback, status_callback, frame_callback=None):
        super().__init__()
        self.user_id = user_id
        self.lock_callback = lock_callback
        self.status_callback = status_callback
        self.frame_callback = frame_callback
        self.running = False
        self.is_locked = False
        self.consecutive_unknowns = 0
        self.last_verified_time = 0
        self.debug_info = "Ready"
        
        # Load Resources
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        try:
            self.recognizer.read(TRAINER_PATH)
            self.model_loaded = True
        except:
            print("WARNING: Model not found. Sentinel running in Detection Only mode.")
            self.model_loaded = False
            
        self.face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
        
        # Timers
        self.last_face_seen_time = time.time()
        self.last_input_time = time.time()
        self.absence_events = 0
        self.start_time = None

        # Input Listeners
        self.mouse_listener = mouse.Listener(on_move=self.on_input, on_click=self.on_input, on_scroll=self.on_input)
        self.key_listener = keyboard.Listener(on_press=self.on_input)

    def on_input(self, *args):
        self.last_input_time = time.time()

    def run(self):
        self.running = True
        self.start_time = time.time()
        self.mouse_listener.start()
        self.key_listener.start()
        
        video_capture = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
        
        while self.running:
            # We CONTINUE reading frames even if locked, to support "Biometric Unlock" check.
            
            ret, frame = video_capture.read()
            if not ret:
                print("Warning: Camera read failed. Retrying...")
                time.sleep(1)
                continue

            # WARMUP: Skip first 30 frames (~1-2s) to let camera exposure settle
            frames_read = getattr(self, "frames_read", 0) + 1
            self.frames_read = frames_read
            if frames_read < 30:
                 self.debug_info = "Camera Warmup..."
                 if self.frame_callback: self.frame_callback(frame)
                 continue

            if self.frame_callback:
                self.frame_callback(frame)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)

            # Instance variable to be accessed by UI
            self.current_face_is_authorized = False
            unauthorized_face_detected = False
            
            if len(faces) > 0:
                for (x,y,w,h) in faces:
                    if self.model_loaded:
                        id_, confidence = self.recognizer.predict(gray[y:y+h,x:x+w])
                        
                        self.debug_info = f"ID:{id_} Conf:{int(confidence)}"
                        
                        # STRICT SECURITY LOGIC:
                        if confidence < CONFIDENCE_THRESHOLD and id_ == self.user_id:
                            self.current_face_is_authorized = True
                            self.debug_info += " [MATCH]"
                        else:
                            unauthorized_face_detected = True
                            self.debug_info += " [INTRUDER]"
                    else:
                        # Fallback (No model loaded yet)
                        self.current_face_is_authorized = True 
            else:
                self.debug_info = "No Face Detected" 

            now = time.time()
            
            # --- UPDATE VERIFICATION STATE ---
            # Only consider user "Verified" if they are present AND NO STRANGERS are present.
            if self.current_face_is_authorized and not unauthorized_face_detected:
                self.last_verified_time = now
                self.consecutive_unknowns = 0
            
            # --- ONLY ACT ON RULES IF NOT LOCKED ---
            if not self.is_locked:
                # 1. IMMEDIATE THREAT: Stranger Detected
                if unauthorized_face_detected:
                    self.consecutive_unknowns += 1
                    print(f"[Sentinel] Warning: Unauthorized Person x{self.consecutive_unknowns}")
                    
                    # Lock faster for intruders (e.g. ~1 second / 10 frames)
                    if self.consecutive_unknowns > 10: 
                        self.trigger_lock("SECURITY ALERT: Unauthorized Person!", frame)
                
                # 2. SAFE STATE: User Present & No Strangers
                elif self.current_face_is_authorized:
                    self.last_face_seen_time = now
                    self.consecutive_unknowns = 0
                    self.status_callback(f"Active - Verified User (Faces: {len(faces)})")
                
                # 3. ABSENCE / GHOST INPUT
                else:
                    # User is gone (and no strangers detected either, just empty or failures)
                    # We don't increment consecutive_unknowns here to avoid mixing "no face" with "intruder"
                    
                    if (now - self.last_face_seen_time) > GHOST_INPUT_THRESHOLD:
                        # Check for strict timeout first
                        from .config import ABSENCE_LOCK_TIMEOUT
                        if (now - self.last_face_seen_time) > ABSENCE_LOCK_TIMEOUT:
                            self.trigger_lock(f"Auto-Lock: Absent for > {ABSENCE_LOCK_TIMEOUT}s", frame)

                        # Check for Ghost Input
                        elif (now - self.last_input_time) < 1.0: 
                            self.trigger_lock("Ghost Input Detected!", frame)
                        else:
                            self.status_callback("Idling - No User")
                    else:
                        self.status_callback("Idling - Warning")

            time.sleep(0.1)

        video_capture.release()
        self.mouse_listener.stop()
        self.key_listener.stop()

    def trigger_lock(self, reason, frame):
        if not self.is_locked:
            self.is_locked = True
            self.absence_events += 1
            print(f"LOCK TRIGGERED: {reason}")
            
            timestamp = int(time.time())
            from .config import BREACH_DIR
            import os
            try:
                filename = os.path.join(BREACH_DIR, f"breach_{timestamp}.jpg")
                cv2.imwrite(filename, frame)
                self.lock_callback(reason, filename)
            except Exception as e:
                print(f"Lock Error: {e}")
                self.lock_callback(reason, "")

    def stop(self):
        self.running = False
        
    def unlock(self):
        self.is_locked = False
        self.last_face_seen_time = time.time()
        self.consecutive_unknowns = 0

