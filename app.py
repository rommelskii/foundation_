from flask import Flask, jsonify, request

from backend.env_helper import EnvVars 
from backend.pillow_handler import encode_pillow_to_base64, decode_base64_to_pillow

from backend.inference import yolo_extract_faces
from backend.inference import yolo_get_coords
from backend.inference import media_get_coords 
from backend.inference import draw_circle 

from ultralytics import YOLO

import time
import os


app = Flask(__name__)
envs = EnvVars()

os.system("clear")

print(f"FOUNDATION_FILTER backend ver. {envs.PROJECT_VER}")
print(f"Abadiano, Malatag, Sangilan, Ronduen")

time.sleep(1)

#Check if YOLO/Mediapipe models exist
model_path = envs.MODEL_DIR
media_path = envs.MEDIA_DIR
if not os.path.exists(model_path):
    raise FileNotFoundError(f"YOLO model not found at: {os.path.abspath(model_path)}")
if not os.path.exists(media_path):
    raise FileNotFoundError(f"Mediapipe task not found at: {os.path.abspath(model_path)}")

#Load YOLO model into memory
yolo_model = YOLO('models/yolov8n-face.pt')

@app.route('/', methods=['GET']) 
def home():
    return jsonify({"message": f"Running on {envs.FLASK_APP}"}), 200

@app.route('/yolo', methods=['GET', 'POST'])
def yolo_frame_gen():
    """
    Perform a YOLOv8 inference to do frame generation.
    
    This route receives a raw base-64 image digest where it is decoded, transformed to a PIL object,
    and inputted to the YOLO backend for frame generation. The route replies with the base-64 digest
    of the frame-generated image that includes the filters to the frontend.

    Methods: 
    GET - for checking if YOLO is active
    POST - supply a b64 image of the live feed to perform frame gen

    Input payload: 
    {'b64_input': <long string>}
    Output payload:
    {'b64_output': <long string>}
    """
    json_data = request.get_json(silent=True)
    b64_string = json_data.get('b64_input')

    if b64_string is None: 
        return jsonify({'b64_output': ""}), 400

    pil_img = decode_base64_to_pillow(b64_string)

    #inference
    face_data = yolo_extract_faces(yolo_model, pil_img)
    coords = yolo_get_coords(face_data)
    sample_frame_gen = draw_circle(coords, 25, pil_img) # DELETE THIS TO REPLACE TRUE FRAME GENERATION

    #b64 encode
    b64_output = encode_pillow_to_base64(sample_frame_gen)

    #ret
    return jsonify({'b64_output': b64_output}), 200

@app.route("/media", methods=['GET', 'POST'])
def media_frame_gen():
    """
    Performs frame generation using Mediapipe pose estimation.

    This route also receives base-64 strings and transforms them into images that Mediapipe
    can utilize. Once the face centroids are retrieved and frame generation is performed, the
    resulting image is encoded back to base-64 and sent to the frontend.

    Methods: 
    GET - for checking if Mediapipe is active
    POST - supply a b64 image of the live feed to perform frame gen

    Input payload: 
    {'b64_input': <long string>}
    Output payload:
    {'b64_output': <long string>}
    """
    json_data = request.get_json(silent=True)
    b64_string = json_data.get('b64_input')

    if b64_string is None: 
        return jsonify({'b64_output': ""}), 400

    pil_img = decode_base64_to_pillow(b64_string)

    #inference
    coords = media_get_coords(pil_img,envs.MEDIA_DIR)
    sample_frame_gen = draw_circle(coords, 100, pil_img) # DELETE THIS TO REPLACE TRUE FRAME GENERATION

    #b64 encode
    b64_output = encode_pillow_to_base64(sample_frame_gen)

    #ret
    return jsonify({'b64_output': b64_output}), 200
    

if __name__ == "__main__":
    app.run(debug=True, port=envs.API_PORT)
