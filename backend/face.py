"""
file: face.py

This file contains the modules for performing frame generation for identifying faces (if any).
It also contains the helper functions for extracting the face centroids.
"""

from PIL import ImageDraw

def frame_gen(model, frame):
    # Arguments: model (YOLO model), frame (current frame in PIL format)
    # Returns: result tensor from YOLO
    results = model.predict(
        source=frame,
        save=False,
    )
    return results

def get_face_coords(model_results):
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

def draw_circle(coords, r,  frame):
    draw = ImageDraw.Draw(frame)
    for pt in coords:
        x, y = pt
        coords = [x-r, y-r, x+r, y+r]
        draw.ellipse(coords, fill=None, outline="red", width=10)

    return frame



