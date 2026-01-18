import tkinter as tk
from tkinter import ttk
import cv2
import requests
import threading
from PIL import Image, ImageTk
import time
from backend.app.utils.pillow_handler import encode_pillow_to_base64, decode_base64_to_pillow
from backend.app.utils.env_helper import EnvVars

# Configuration
envs = EnvVars()
API_URL = f"http://localhost:{envs.API_PORT}/vision/yolo"

class MultiCamVisionClient:
    def __init__(self, window):
        self.window = window
        self.window.title("Foundation Filter - Camera Selector")

        # 1. Camera Management Variables
        self.vid = None
        self.is_running = True
        self.current_cam_index = 0
        self.available_cameras = self.scan_cameras()

        # 2. UI Layout - Control Panel
        self.control_frame = tk.Frame(window)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(self.control_frame, text="Select Camera:").pack(side=tk.LEFT)
        
        self.cam_var = tk.StringVar()
        self.cam_dropdown = ttk.OptionMenu(
            self.control_frame, 
            self.cam_var, 
            self.available_cameras[0] if self.available_cameras else "None",
            *self.available_cameras,
            command=self.change_camera
        )
        self.cam_dropdown.pack(side=tk.LEFT, padx=5)

        # 3. UI Layout - Video Canvas
        self.canvas = tk.Canvas(window, width=640, height=480, bg="black")
        self.canvas.pack()
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW)

        # 4. Initialize first camera
        if self.available_cameras:
            self.change_camera(self.available_cameras[0])

        # Start the background processing thread
        self.thread = threading.Thread(target=self.process_loop, daemon=True)
        self.thread.start()

        self.window.protocol("WM_DELETE_WINDOW", self.quit)
        self.window.mainloop()

    def scan_cameras(self, max_to_test=5):
        """Scans system for available camera indices."""
        available = []
        for i in range(max_to_test):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(f"Camera {i}")
                cap.release()
        return available

    def change_camera(self, selection):
        """Re-initializes the VideoCapture object with the selected index."""
        new_index = int(selection.split()[-1])
        
        # Stop existing capture
        if self.vid:
            self.vid.release()
        
        self.vid = cv2.VideoCapture(new_index)
        
        # Update resolution to match high-res requirements
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Resize canvas to match hardware
        self.canvas.config(width=self.width, height=self.height)
        print(f"Switched to {selection} at {self.width}x{self.height}")

    def process_loop(self):
        while self.is_running:
            if not self.vid or not self.vid.isOpened():
                time.sleep(0.1)
                continue

            ret, frame = self.vid.read()
            if not ret:
                continue

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)

            try:
                b64_input = encode_pillow_to_base64(pil_img)
                payload = {"b64_input": b64_input}
                
                response = requests.post(API_URL, json=payload, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    b64_output = data.get("b64_output")
                    
                    if b64_output:
                        result_pil = decode_base64_to_pillow(b64_output)
                        self.window.after(0, self.update_canvas, result_pil)
                
            except Exception as e:
                print(f"API Error: {e}")
                time.sleep(0.5)

    def update_canvas(self, pil_img):
        self.photo = ImageTk.PhotoImage(image=pil_img)
        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)

    def quit(self):
        self.is_running = False
        if self.vid:
            self.vid.release()
        self.window.destroy()

if __name__ == "__main__":
    MultiCamVisionClient(tk.Tk())
