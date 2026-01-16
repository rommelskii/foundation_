# Testing Branch
All branches must be PR'd here to undergo testing. This is also the branch for implementing unit tests.

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

### Quick Start
1. Clone the repository to the local machine.
2. Build the Docker image:
   `docker build -t foundation-filter .`
3. Deploy the systemd service:
   `sudo cp foundation-filter.service /etc/systemd/system/`
4. Enable and start the service:
   `sudo systemctl enable foundation-filter.service --now`
