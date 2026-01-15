from ultralytics import YOLO

# Load the specialized face detection model
model = YOLO('./models/yolov8n-face.pt') 
img_path = './images/faces_image.jpg'

results = model.predict(
    source=img_path,
    save=True,               # Tells YOLO to save the image
    project='./', # The top-level directory
    name='results',     # The sub-directory name
    exist_ok=True            # Overwrites if the folder already exists
)
