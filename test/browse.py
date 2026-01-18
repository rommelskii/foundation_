import requests
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import io
from backend.app.utils.pillow_handler import encode_pillow_to_base64, decode_base64_to_pillow
from backend.app.utils.env_helper import EnvVars

envs = EnvVars()
MEDIA_ROUTE = f"http://localhost:{envs.API_PORT}/vision/media"

def browse_and_process():
    # 1. Open File Browser
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    if not file_path:
        return

    try:
        # 2. Process Image locally with PIL
        with Image.open(file_path) as img:
            b64_input = encode_pillow_to_base64(img)
            
        # 3. Send to Flask API
        payload = {"b64_input": b64_input}
        response = requests.post(MEDIA_ROUTE, json=payload)
        
        if response.status_code != 200:
            messagebox.showerror("Error", f"Server returned {response.status_code}")
            return

        # 4. Decode Result
        data = response.json()
        b64_output = data.get("b64_output")
        
        if b64_output:
            result_img = decode_base64_to_pillow(b64_output)
            display_result(result_img)
            
    except Exception as e:
        messagebox.showerror("Exception", str(e))

def display_result(pil_image):
    # Create a new popup window to show the image
    top = tk.Toplevel()
    top.title("Processed Output")
    
    # Resize for display if too large
    pil_image.thumbnail((800, 600))
    
    img_tk = ImageTk.PhotoImage(pil_image)
    label = tk.Label(top, image=img_tk)
    label.image = img_tk  # Keep a reference!
    label.pack(padx=10, pady=10)

# --- Main Window UI ---
root = tk.Tk()
root.title("Foundation Filter - Image Browser")
root.geometry("300x150")

label = tk.Label(root, text="Select an image to process via API")
label.pack(pady=10)

browse_btn = tk.Button(root, text="Browse Image", command=browse_and_process)
browse_btn.pack(pady=20)

root.mainloop()
