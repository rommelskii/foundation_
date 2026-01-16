"""
file: inference.py

This file contains the modules for performing frame generation for identifying faces (if any).
It also contains the helper functions for extracting the face centroids.
"""

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL import Image, ImageDraw
import numpy as np

def yolo_extract_faces(model, frame):
    # Arguments: model (YOLO model), frame (current frame in PIL format)
    # Returns: result tensor from YOLO
    results = model.predict(
        source=frame,
        save=False,
    )
    return results

def yolo_get_coords(model_results):
    # Arguments: model_results (Result tensor from YOLO), frame (current frame in PIL format)
    # Returns: Array of face centroids
    ret = []
    for result in model_results:
        boxes = result.boxes
        for box in boxes:
            coords = box.xyxy[0]
            x1,y1,x2,y2 = coords.tolist()
            ret.append([(x1+x2)/2,(y1+y2)/2])
    return ret

def media_get_coords(frame, model_path='face_landmarker.task', max_faces=5):
    centroids = []
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options = base_options,
        output_face_blendshapes = False,
        num_faces = max_faces,
        running_mode = vision.RunningMode.IMAGE
    )

    np_frame = np.array(frame)
    mp_frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=np_frame)
    img_w, img_h = frame.size

    with vision.FaceLandmarker.create_from_options(options) as landmarker:
        detection_result = landmarker.detect(mp_frame)

    if detection_result.face_landmarks:
        for landmarks in detection_result.face_landmarks:
            sum_x = sum([lm.x for lm in landmarks])
            sum_y = sum([lm.y for lm in landmarks])
            count = len(landmarks)

            avg_x = sum_x / count
            avg_y = sum_y / count

            cx = int(avg_x * img_w)
            cy = int(avg_y * img_h)    
            centroids.append([cx,cy])
    else:
        print("No faces were detected in the image.")

    return centroids 

def draw_circle(coords, r,  frame):
    draw = ImageDraw.Draw(frame)
    for pt in coords:
        x, y = pt
        coords = [x-r, y-r, x+r, y+r]
        draw.ellipse(coords, fill=None, outline="red", width=10)

    return frame



