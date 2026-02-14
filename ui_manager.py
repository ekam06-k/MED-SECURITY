import tkinter as tk
from tkinter import messagebox
import sys
import os

# Try to enable High DPI visibility on Windows
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Colors
BG_COLOR = "#121212" 
FG_COLOR = "#e0e0e0"
ACCENT_COLOR = "#00adb5"
CARD_COLOR = "#1e1e1e"
WARNING_COLOR = "#ff4d4d"
SUCCESS_COLOR = "#00c853"

class MedGuardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MedGuard Sentinel (Debug Mode)")
        self.geometry("1000x700")
        self.configure(bg=BG_COLOR)
        
        # 1. FORCE UPDATE to ensure window exists
        self.update()
        
        print("DEBUG: Window Created")
        
        # 2. Show Loading Label IMMEDIATELY
        self.loading_label = tk.Label(self, text="System Loading... Please Wait.", font=("Segoe UI", 20), bg=BG_COLOR, fg=ACCENT_COLOR)
        self.loading_label.pack(pady=50)
        self.update()
        
        print("DEBUG: Loading Label Packed")

        # 3. Import Logic (Delayed to show UI first)
        try:
            from .db_manager import DBManager
            from .auth_manager import AuthManager
            from .sentinel import Sentinel
            
            self.db = DBManager()
            self.auth = AuthManager()
            self.sentinel = None
            self.current_user = None
            
            print("DEBUG: Managers Initialized")
            
        except Exception as e:
            messagebox.showerror("Init Error", f"Failed to load modules: {e}")
            return

        # 4. Remove Loading and Show Login
        self.loading_label.destroy()
        self.show_login()

    def show_login(self):
        self.clear_screen()
        
        # DEBUG: Verify we are in this function
        print("DEBUG: Showing Login Screen")
        
        # Header (Direct Pack to Root)
        tk.Label(self, text="MEDGUARD LOGIN", font=("Segoe UI", 28, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=40)
        
        # Frame for inputs
        form = tk.Frame(self, bg=CARD_COLOR, padx=40, pady=40)
        form.pack(pady=10)
        
        tk.Label(form, text="Employee ID", font=("Segoe UI", 10, "bold"), bg=CARD_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.login_eid = tk.Entry(form, font=("Segoe UI", 12), width=30, bg="#333333", fg="white", insertbackground="white", relief="flat")
        self.login_eid.pack(pady=(5, 20), ipady=5)
        
        tk.Label(form, text="Password", font=("Segoe UI", 10, "bold"), bg=CARD_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.login_pass = tk.Entry(form, font=("Segoe UI", 12), show="•", width=30, bg="#333333", fg="white", insertbackground="white", relief="flat")
        self.login_pass.pack(pady=(5, 20), ipady=5)
        
        # Buttons
        tk.Button(self, text="LOGIN", font=("Segoe UI", 12, "bold"), bg=ACCENT_COLOR, fg="white", width=25, relief="flat", command=self.do_login).pack(pady=20)
        tk.Button(self, text="Create New Account", font=("Segoe UI", 10), bg=BG_COLOR, fg=FG_COLOR, activebackground=BG_COLOR, activeforeground=ACCENT_COLOR, relief="flat", command=self.show_signup).pack()

    def show_signup(self):
        self.clear_screen()
        
        tk.Label(self, text="REGISTRATION", font=("Segoe UI", 24, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=30)
        
        form = tk.Frame(self, bg=CARD_COLOR, padx=40, pady=40)
        form.pack(pady=10)
        
        tk.Label(form, text="Full Name", font=("Segoe UI", 10), bg=CARD_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.reg_name = tk.Entry(form, width=30, bg="#333333", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 11))
        self.reg_name.pack(pady=(5, 15), ipady=3)

        tk.Label(form, text="Employee ID", font=("Segoe UI", 10), bg=CARD_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.reg_eid = tk.Entry(form, width=30, bg="#333333", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 11))
        self.reg_eid.pack(pady=(5, 15), ipady=3)

        tk.Label(form, text="Password", font=("Segoe UI", 10), bg=CARD_COLOR, fg=FG_COLOR).pack(anchor="w")
        self.reg_pass = tk.Entry(form, show="•", width=30, bg="#333333", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 11))
        self.reg_pass.pack(pady=(5, 15), ipady=3)
        
        tk.Button(self, text="CAPTURE FACE & REGISTER", bg=ACCENT_COLOR, fg="white", font=("Segoe UI", 11, "bold"), relief="flat", width=30, command=self.start_training).pack(pady=20)
        tk.Button(self, text="Back to Login", bg=BG_COLOR, fg=FG_COLOR, relief="flat", command=self.show_login).pack()

    def start_training(self):
        name = self.reg_name.get()
        eid = self.reg_eid.get()
        pwd = self.reg_pass.get()
        
        if not (name and eid and pwd):
            messagebox.showwarning("Required", "Fill all fields")
            return
            
        import cv2
        self.cap_lbl = tk.Label(self, text="Opening Camera...", font=("Segoe UI", 16), fg="red", bg=BG_COLOR)
        self.cap_lbl.pack(pady=10)
        self.update()
        
        from .auth_manager import AuthManager
        mac = AuthManager.get_mac_address()
        hashed = AuthManager.hash_password(pwd)
        
        uid = self.db.add_user(name, eid, hashed, "training", mac)
        if not uid:
             messagebox.showerror("Error", "ID Exists")
             self.cap_lbl.destroy()
             return

        from PIL import Image, ImageTk

        # Setup Preview Label
        self.preview_lbl = tk.Label(self, bg="black")
        self.preview_lbl.pack(pady=10)
        
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cap.isOpened():
                raise Exception("Cannot open camera")
                
            images = []
            
            # Capture 50 frames (approx 3-5 seconds depending on speed)
            for i in range(50):
                ret, frame = cap.read()
                if ret:
                    images.append(frame)
                    
                    # Live Preview Update
                    # Convert BGR to RGB
                    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                    img = Image.fromarray(cv2image)
                    imgtk = ImageTk.PhotoImage(image=img)
                    
                    self.preview_lbl.imgtk = imgtk # Keep ref
                    self.preview_lbl.configure(image=imgtk)
                    self.cap_lbl.config(text=f"Scanning... {i*2}%")
                    self.update()
                else:
                    break
            
            cap.release()
            self.preview_lbl.destroy() # Remove preview
            
            if len(images) < 10:
                self.db.delete_user(uid)
                messagebox.showerror("Error", "Camera failed to capture enough frames.")
                self.cap_lbl.destroy()
                return

            self.cap_lbl.config(text="Processing Model...")
            self.update()
            
            # Train
            AuthManager.save_face_samples(uid, name, images)
            if AuthManager.train_recognizer():
                # Save Audit Log Image
                try:
                    from .config import SIGNUP_LOG_DIR
                    import os
                    import time
                    import cv2
                    timestamp = int(time.time())
                    safe_name = "".join(x for x in name if x.isalnum())
                    log_path = os.path.join(SIGNUP_LOG_DIR, f"signup_{timestamp}_{safe_name}.jpg")
                    if len(images) > 0:
                        cv2.imwrite(log_path, images[0])
                except Exception as e:
                    print(f"Failed to save signup log: {e}")

                self.cap_lbl.destroy()
                messagebox.showinfo("Done", "Registered!")
                self.show_login()
            else:
                messagebox.showerror("Error", "Training Failed")
                self.db.delete_user(uid)
                self.cap_lbl.destroy()
                self.show_signup()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            if 'uid' in locals():
                self.db.delete_user(uid)
            if hasattr(self, 'cap_lbl'): self.cap_lbl.destroy()
            if hasattr(self, 'preview_lbl'): self.preview_lbl.destroy()

    def do_login(self):
        eid = self.login_eid.get()
        pwd = self.login_pass.get()
        
        try:
            user = self.db.get_user_by_id(eid)
            if user:
                 from .auth_manager import AuthManager
                 if AuthManager.verify_password(user[3], pwd):
                     self.start_dashboard(user)
                 else:
                     messagebox.showerror("No", "Bad Password")
            else:
                messagebox.showerror("No", "User Not Found")
        except Exception as e:
             messagebox.showerror("Error", str(e))

    def start_dashboard(self, user):
        self.current_user = user
        self.clear_screen()
        
        tk.Label(self, text=f"Welcome, {user[1]}", font=("Segoe UI", 24, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(30, 10))
        
        status_frame = tk.Frame(self, bg=CARD_COLOR, padx=20, pady=10)
        status_frame.pack(pady=10)
        tk.Label(status_frame, text="• SENTINEL ACTIVE", fg=SUCCESS_COLOR, font=("Segoe UI", 14, "bold"), bg=CARD_COLOR).pack(side="left")
        tk.Label(status_frame, text=" | LIVE MONITOR", fg=FG_COLOR, font=("Segoe UI", 14), bg=CARD_COLOR).pack(side="left")
        
        # Live Feed Label
        feed_frame = tk.Frame(self, bg="#000000", bd=2, relief="solid")
        feed_frame.pack(pady=20)
        self.feed_label = tk.Label(feed_frame, bg="black")
        self.feed_label.pack()
        
        tk.Button(self, text="LOGOUT", command=self.do_logout, bg=WARNING_COLOR, fg="white", font=("Segoe UI", 12, "bold"), relief="flat", width=20).pack(pady=30)
        
        from .sentinel import Sentinel
        self.sentinel = Sentinel(user[0], self.lockdown_trigger, lambda x: None, self.update_feed_safe)
        self.sentinel.start()

    def update_feed_safe(self, frame):
        # Called from thread, schedule on main loop
        from PIL import Image, ImageTk
        try:
             cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
             # Resize for dashboard (320x240)
             cv2image = cv2.resize(cv2image, (320, 240))
             img = Image.fromarray(cv2image)
             imgtk = ImageTk.PhotoImage(image=img)
             
             # Schedule update
             self.after(0, lambda: self._update_label(imgtk))
        except:
             pass

    def _update_label(self, imgtk):
        if hasattr(self, 'feed_label') and self.feed_label.winfo_exists():
            self.feed_label.imgtk = imgtk
            self.feed_label.configure(image=imgtk)

    def lockdown_trigger(self, reason, path):
         # Simple overlay
         self.after(0, lambda: self.show_lock(reason))

    def show_lock(self, reason):
        top = tk.Toplevel(self)
        top.attributes("-fullscreen", True)
        top.configure(bg="#000000") # Pure black for impact
        
        # Flashing effect or red border could be added, but simple stark text is good
        
        container = tk.Frame(top, bg="#000000")
        container.pack(expand=True)
        
        tk.Label(container, text="⚠ SECURITY LOCKDOWN ⚠", font=("Segoe UI", 48, "bold"), bg="#000000", fg=WARNING_COLOR).pack(pady=(0, 20))
        tk.Label(container, text=reason, font=("Segoe UI", 24), bg="#000000", fg="white").pack(pady=(0, 50))
        
        tk.Label(container, text="Verify Password to Unlock", font=("Segoe UI", 14), bg="#000000", fg="#888888").pack()
        e = tk.Entry(container, font=("Segoe UI", 20), show="•", width=30, bg="#222222", fg="white", insertbackground="white", relief="flat", justify="center")
        e.pack(pady=20, ipady=10)
        e.focus()
        
        def check():
             from .auth_manager import AuthManager
             import time
             
             pwd = e.get()
             if not AuthManager.verify_password(self.current_user[3], pwd):
                  messagebox.showerror("Security Alert", "Invalid Password")
                  return

             # Password OK. Check Biometric with Retries.
             btn.config(state="disabled", text="Verifying...")
             
             def attempt_biometric(start_time):
                 # Check if we have a valid face seen in the last 2 seconds
                 if self.sentinel and ((time.time() - self.sentinel.last_verified_time) < 2.0):
                     top.destroy()
                     self.sentinel.unlock()
                 else:
                     # Retry for 3 seconds
                     elapsed = time.time() - start_time
                     if elapsed < 3.0: 
                         # Show Debug Info on Button for feedback
                         status = self.sentinel.debug_info if self.sentinel else "Init"
                         btn.config(text=f"Scanning... ({status})")
                         top.after(100, lambda: attempt_biometric(start_time))
                     else:
                         btn.config(state="normal", text="UNLOCK")
                         # Show last error context
                         last_status = self.sentinel.debug_info if self.sentinel else "Unknown"
                         messagebox.showerror("Security Alert", f"Biometric Mismatch!\nStatus: {last_status}\n\nAuthorized User Face Required.")

             attempt_biometric(time.time())
        
        btn = tk.Button(container, text="UNLOCK SYSTEM", command=check, font=("Segoe UI", 16, "bold"), bg=ACCENT_COLOR, fg="white", relief="flat", width=20)
        btn.pack(pady=20)

    def do_logout(self):
        if self.sentinel:
            self.sentinel.stop()
        self.show_login()

    def clear_screen(self):
        for w in self.winfo_children():
            w.destroy()

    def on_close(self):
        if hasattr(self, 'sentinel') and self.sentinel:
            self.sentinel.stop()
        self.destroy()
        os._exit(0)
