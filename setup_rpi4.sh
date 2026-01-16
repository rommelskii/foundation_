#!/bin/bash
# =============================================================================
# Raspberry Pi 4 Setup Script
# Optimized for face detection application
# Tested on: Raspberry Pi OS (64-bit), Ubuntu 22.04 ARM64
# =============================================================================

set -e

echo "=============================================="
echo "  Raspberry Pi 4 Setup - Face Detection App"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on ARM64
ARCH=$(uname -m)
if [[ "$ARCH" != "aarch64" && "$ARCH" != "arm64" ]]; then
    echo -e "${RED}Warning: This script is designed for ARM64 (aarch64)${NC}"
    echo "Current architecture: $ARCH"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo -e "${YELLOW}Warning: Running as root. Consider using a regular user with sudo.${NC}"
fi

# -----------------------------------------------------------------------------
# Step 1: System Update
# -----------------------------------------------------------------------------
echo -e "\n${GREEN}[1/7] Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# -----------------------------------------------------------------------------
# Step 2: Install System Dependencies
# -----------------------------------------------------------------------------
echo -e "\n${GREEN}[2/7] Installing system dependencies...${NC}"
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    cmake \
    pkg-config \
    git \
    wget \
    curl \
    # OpenCV dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libfontconfig1 \
    libatlas-base-dev \
    # Camera support
    libv4l-dev \
    v4l-utils \
    # Video/Image libraries
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    # GPIO support
    python3-rpi.gpio

# -----------------------------------------------------------------------------
# Step 3: Enable Camera Interface
# -----------------------------------------------------------------------------
echo -e "\n${GREEN}[3/7] Configuring camera interface...${NC}"

# Check if camera is enabled
if ! grep -q "start_x=1" /boot/config.txt 2>/dev/null; then
    echo "Enabling camera interface..."
    echo "start_x=1" | sudo tee -a /boot/config.txt
    echo "gpu_mem=128" | sudo tee -a /boot/config.txt
    REBOOT_NEEDED=true
fi

# Add user to video group for camera access
sudo usermod -a -G video $USER 2>/dev/null || true

# -----------------------------------------------------------------------------
# Step 4: Create Python Virtual Environment
# -----------------------------------------------------------------------------
echo -e "\n${GREEN}[4/7] Setting up Python virtual environment...${NC}"

VENV_DIR="$HOME/face_detection_venv"

if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
    read -p "Recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_DIR"
        python3 -m venv "$VENV_DIR"
    fi
else
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip wheel setuptools

# -----------------------------------------------------------------------------
# Step 5: Install Python Dependencies
# -----------------------------------------------------------------------------
echo -e "\n${GREEN}[5/7] Installing Python dependencies (RPi4 optimized)...${NC}"

# Check if requirements file exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQ_FILE="$SCRIPT_DIR/backend/requirements_rpi4.txt"

if [ -f "$REQ_FILE" ]; then
    pip install -r "$REQ_FILE"
else
    echo -e "${YELLOW}requirements_rpi4.txt not found. Installing core packages...${NC}"
    pip install \
        flask \
        pillow \
        opencv-python-headless \
        numpy \
        tflite-runtime \
        mediapipe \
        python-dotenv \
        requests
fi

# -----------------------------------------------------------------------------
# Step 6: Download MediaPipe Models
# -----------------------------------------------------------------------------
echo -e "\n${GREEN}[6/7] Downloading face detection models...${NC}"

MODEL_DIR="$SCRIPT_DIR/backend"
mkdir -p "$MODEL_DIR"

# Download face landmarker model if not exists
FACE_LANDMARKER="$MODEL_DIR/face_landmarker.task"
if [ ! -f "$FACE_LANDMARKER" ]; then
    echo "Downloading MediaPipe face landmarker model..."
    wget -O "$FACE_LANDMARKER" \
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
else
    echo "Face landmarker model already exists."
fi

# -----------------------------------------------------------------------------
# Step 7: Performance Optimizations
# -----------------------------------------------------------------------------
echo -e "\n${GREEN}[7/7] Applying performance optimizations...${NC}"

# Increase swap size for models (if needed)
SWAP_SIZE=$(free -m | grep Swap | awk '{print $2}')
if [ "$SWAP_SIZE" -lt 1024 ]; then
    echo "Increasing swap size to 1GB..."
    sudo dphys-swapfile swapoff 2>/dev/null || true
    sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile 2>/dev/null || true
    sudo dphys-swapfile setup 2>/dev/null || true
    sudo dphys-swapfile swapon 2>/dev/null || true
fi

# Set CPU governor to performance (optional, increases power usage)
read -p "Set CPU governor to 'performance' for better inference speed? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || true
    echo "CPU governor set to performance mode."
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "=============================================="
echo -e "${GREEN}  Setup Complete!${NC}"
echo "=============================================="
echo ""
echo "Virtual environment: $VENV_DIR"
echo "Activate with: source $VENV_DIR/bin/activate"
echo ""
echo "To run the application:"
echo "  1. source $VENV_DIR/bin/activate"
echo "  2. cd $SCRIPT_DIR"
echo "  3. python app.py"
echo ""
echo "Expected performance: 5-10 FPS face detection"
echo ""

if [ "$REBOOT_NEEDED" = true ]; then
    echo -e "${YELLOW}IMPORTANT: Camera settings changed. Please reboot:${NC}"
    echo "  sudo reboot"
fi

# -----------------------------------------------------------------------------
# Docker Setup (Optional)
# -----------------------------------------------------------------------------
echo ""
read -p "Install Docker for containerized deployment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${GREEN}Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo ""
    echo "Docker installed. Log out and back in for group changes to take effect."
    echo ""
    echo "Build the container with:"
    echo "  docker build -t face-detection-rpi4 ."
    echo ""
    echo "Run the container with:"
    echo "  docker run --device=/dev/video0 -p 5000:5000 face-detection-rpi4"
fi

echo ""
echo "Setup script finished!"
