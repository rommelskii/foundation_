# Foundation Filter

Foundation Filter is a Raspbian-hosted, containerized application designed to process a live webcam feed and display it on a television via HDMI. The system detects faces in real-time and applies a digital filter overlay onto the detected subjects.

---

## Project Description

The Foundation Filter functions as a locally-hosted service running within a Docker environment. It captures video frames, processes them through an inference engine to locate faces, applies a graphical "filter" stamp, and renders the result through a web-based interface displayed in a full-screen browser.

---

## Project Architecture

The application is built using a containerized approach to ensure environment consistency and ease of deployment across Raspbian installations.

### Technology Stack

| Component | Description |
| :--- | :--- |
| **OpenCV** | Handles frame capture and pre-processing from the live camera feed. |
| **YOLOv8** | The primary inference engine used for real-time face detection. |
| **Mediapipe** | (Optional) Utilized for face pose estimation to improve filter alignment. |
| **React** | The frontend framework used to display the processed live feed. |
| **Chromium** | The browser engine used to run the application in a kiosk-style display. |
| **Docker** | Provides the containerization layer for the entire service. |
| **systemd** | Manages the container lifecycle and ensures the app starts on boot. |

---

## Program Logic

The application follows a structured execution flow to ensure stability and performance.

### 1. Housekeeping Step
Before entering the main loop, the program performs a diagnostic check to verify:
* Hardware access to the camera feed.
* The inference engine is correctly loaded and operational.
* The frontend communication ports are open.

### 2. Runtime Loop
The system processes data at a target rate of **24 frames per second (fps)**:
* **Capture**: Receives a frame from the camera.
* **Inference**: YOLOv8 scans the frame for face coordinates.
* **Processing**: 
    * If faces are found: The filter overlay is stamped onto the detected coordinates.
    * If no faces are found: The inference step is bypassed to conserve resources.
* **Display**: The final frame is sent to the React frontend for HDMI output.

### 3. Shutdown
The application is designed for persistent operation. It monitors the host system state and will perform a graceful shutdown of the containerized processes only when the Raspberry Pi itself is shut down.

---

## Developer Operations

### Containerization
All development testing and deployment utilize Docker containers. The container is configured to:
* Expose specific ports for the React frontend and inference stream.
* Map host video devices (e.g., `/dev/video0`) to the container.
* Allow communication with the display server for HDMI output.

### Deployment and Automation
To automate the application on hardware startup, a **systemd target** is used. This service unit executes the container initialization sequence, ensuring the service is live as soon as the operating system completes its boot sequence.

---

## Installation and Setup

### Prerequisites
* Raspberry Pi running Raspbian (64-bit recommended).
* Docker and Docker Compose installed.
* USB Web Camera.
* HDMI Display.

### Quick Start (x86/Development)
1. Clone the repository to the local machine.
2. Build the Docker image:
   `docker build -t foundation-filter .`
3. Deploy the systemd service:
   `sudo cp foundation-filter.service /etc/systemd/system/`
4. Enable and start the service:
   `sudo systemctl enable foundation-filter.service --now`

---

## Raspberry Pi 4 Deployment

> **Important**: The original PyTorch/YOLOv8 stack is too resource-intensive for RPi4. This section describes the optimized ARM64 deployment using TensorFlow Lite.

### Hardware Requirements (RPi4)

| Component | Minimum | Recommended |
| :--- | :--- | :--- |
| **Raspberry Pi 4** | 4GB RAM | 8GB RAM |
| **Storage** | 16GB microSD | 32GB+ microSD (Class 10) |
| **Camera** | USB Webcam | Raspberry Pi Camera Module v2 |
| **Display** | HDMI Monitor | — |
| **Cooling** | Passive heatsink | Active fan cooling |

### Performance Expectations

| Metric | Original (x86) | RPi4 Lite |
| :--- | :--- | :--- |
| **Target FPS** | 24 fps | 5-10 fps |
| **Inference Time** | ~20ms | ~100-200ms |
| **RAM Usage** | ~4GB | ~1-2GB |
| **ML Framework** | PyTorch + YOLOv8 | TensorFlow Lite + MediaPipe |

### RPi4 Quick Start

#### Option A: Native Installation
```bash
# 1. Clone the repository
git clone <repository-url>
cd mapua_101_rommel

# 2. Run the RPi4 setup script
chmod +x setup_rpi4.sh
./setup_rpi4.sh

# 3. Activate the virtual environment
source ~/face_detection_venv/bin/activate

# 4. Run the application
python app.py
```

#### Option B: Docker (ARM64)
```bash
# 1. Build the ARM64-optimized container
docker build -t foundation-filter-rpi4 .

# 2. Run with camera access
docker run -d \
  --name face-filter \
  --device=/dev/video0 \
  -p 5000:5000 \
  --restart unless-stopped \
  foundation-filter-rpi4
```

### Using the Lightweight Inference Module

The RPi4 version uses `inference_lite.py` instead of the original `inference.py`:

```python
# Import the lightweight detector
from backend.inference_lite import FaceDetectorLite, draw_circle

# Initialize (uses MediaPipe by default - ARM optimized)
detector = FaceDetectorLite(use_mediapipe=True, num_threads=4)

# Detect faces
boxes = detector.detect_faces(frame)
centroids = detector.get_centroids(boxes)

# Draw results
frame = draw_circle(centroids, radius=50, frame=frame)
```

### Optional: Hardware Acceleration

For better performance on RPi4, consider adding a Coral USB Accelerator:

```bash
# Install Coral Edge TPU runtime
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install libedgetpu1-std

# Install PyCoral
pip install pycoral
```

With Coral USB, expect **15-20+ FPS** face detection on RPi4.

### Troubleshooting (RPi4)

| Issue | Solution |
| :--- | :--- |
| Low FPS (<3) | Reduce resolution to 320x240, ensure cooling is adequate |
| Camera not found | Run `ls /dev/video*`, add user to `video` group |
| Out of memory | Use RPi4 8GB model, increase swap to 2GB |
| MediaPipe import error | Install with `pip install mediapipe==0.10.14` |
| TFLite error | Reinstall with `pip install tflite-runtime==2.14.0` |
