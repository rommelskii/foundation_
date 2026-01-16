import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt

def run_face_analysis(image_path, model_path='face_landmarker.task', max_faces=5):
    # 1. Setup MediaPipe Landmarker
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=False,
        num_faces=max_faces,
        running_mode=vision.RunningMode.IMAGE
    )

    # 2. Load Image as PIL object and convert for MediaPipe
    try:
        pil_img = Image.open(image_path).convert("RGB")
        numpy_image = np.array(pil_img)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image)
    except FileNotFoundError:
        print(f"Error: Could not find image at {image_path}")
        return

    # 3. Initialize Landmarker and Perform Inference
    with vision.FaceLandmarker.create_from_options(options) as landmarker:
        detection_result = landmarker.detect(mp_image)

    # 4. Process and Draw Coordinates
    if detection_result.face_landmarks:
        draw = ImageDraw.Draw(pil_img)
        img_w, img_h = pil_img.size
        
        # Parameters for the circles
        radius = 3
        thickness = 2
        colors = ["#00FF00", "#FF0000", "#0000FF", "#FFFF00", "#FF00FF"] # Lime, Red, Blue, Yellow, Magenta

        for face_idx, landmarks in enumerate(detection_result.face_landmarks):
            color = colors[face_idx % len(colors)]
            
            for lm in landmarks:
                # Convert normalized (0-1) to pixel coordinates
                px_x = int(lm.x * img_w)
                px_y = int(lm.y * img_h)
                
                # Define bounding box for the circle
                bbox = [px_x - radius, px_y - radius, px_x + radius, px_y + radius]
                
                # Draw the circle
                draw.ellipse(bbox, outline=color, width=thickness)

        print(f"Success! Detected {len(detection_result.face_landmarks)} face(s).")
        
        # 5. Display using Matplotlib GUI
        plt.figure(figsize=(10, 8))
        plt.imshow(pil_img)
        plt.title(f"MediaPipe Face Landmarks ({len(detection_result.face_landmarks)} faces detected)")
        plt.axis('off')
        plt.show()

    else:
        print("No faces were detected in the image.")

# --- Execute ---
# Replace 'test_image.jpg' with your actual file path
run_face_analysis('./images/faces_image.jpg')
