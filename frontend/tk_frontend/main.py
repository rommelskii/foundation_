import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import threading

"""
file: main.py

This script contains an object for storing the current frame that is read from a given web camera.
In this approach, we are utilizing Tkinter as the front-end. I would say that this is much easier
to deal with than using a web-based front end (such as React), since we have low-level access to the 
frames themselves. The only trade-off here is that it is much harder to implement the filters on the frontend. 
"""

class FoundationFilterCache:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        
        # 1. Hardware Initialization
        self.video_source = 0 # Default camera (/dev/video0)
        self.vid = cv2.VideoCapture(self.video_source)
        
        if not self.vid.isOpened():
            messagebox.showerror("Error", "Unable to open video source")
            return

        # 2. The Cache Variable
        # This acts as your "buffer" for the backend/inference engine
        self.cache = None
        
        # 3. UI Setup
        self.canvas = tk.Canvas(window, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), 
                                height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

        self.btn_check_cache = tk.Button(window, text="Print Cache Info", width=20, command=self.check_cache)
        self.btn_check_cache.pack(anchor=tk.CENTER, expand=True)

        # 4. Runtime Loop
        self.delay = 15 # Approx 60fps update, though camera may be 24-30
        self.update()

        self.window.mainloop()

    def check_cache(self):
        """Debug function to see if the variable is holding data."""
        if self.cache is not None:
            print(f"Cache Status: Frame stored. Shape: {self.cache.shape}")
        else:
            print("Cache Status: Empty")

    def update(self):
        """The main loop that updates the UI and the cache variable."""
        ret, frame = self.vid.read()

        if ret:
            # Update the 'Persistent Variable' Cache
            # This frame is now available for any other part of the program
            self.cache = frame 

            # Convert OpenCV BGR to RGB for Tkinter
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(self.delay, self.update)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Start the application
FoundationFilterCache(tk.Tk(), "Foundation Filter - Frame Cache")
