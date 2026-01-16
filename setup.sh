#! /bin/bash

MEDIA_TASK_URL=https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
YOLO_MODEL_URL=https://huggingface.co/deepghs/yolo-face/resolve/739664f2d00e436a8882238f83175ab0f6497578/yolov8n-face/model.pt

MEDIA_MODEL_DIR=models/media
YOLO_MODEL_DIR=models/yolo
MEDIA_MODEL_NAME=face_landmarker.task
YOLO_MODEL_NAME=yolov8n-face.pt

#build model directory
echo "Building model directory..."
mkdir -p $MEDIA_MODEL_DIR > /dev/null
mkdir -p $YOLO_MODEL_DIR > /dev/null
wget -O "$MEDIA_MODEL_DIR/$MEDIA_MODEL_NAME" "$MEDIA_TASK_URL"
wget -O "$YOLO_MODEL_DIR/$YOLO_MODEL_NAME" "$YOLO_MODEL_URL"
#create python env
ENV_NAME=backend/env
REQ_FILE=backend/requirements.txt

echo "Checking for Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    #install python3 here
    exit 1
fi

echo "Creating Python environment in $ENV_NAME"
python3 -m venv $ENV_NAME

echo "Activating environment..."
source $ENV_NAME/bin/activate

if [ -f "$REQ_FILE" ]; then
    echo "Installing dependencies from ${REQ_FILE}..."
    pip install --upgrade pip
    pip install -r $REQ_FILE
else
    echo "No ${REQ_FILE} found. Skipping installation."
fi

echo "Setup complete! To start working, run: source ${ENV_NAME}/bin/activate"

