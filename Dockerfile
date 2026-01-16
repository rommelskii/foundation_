# =============================================================================
# Raspberry Pi 4 Optimized Dockerfile
# Base: ARM64 Python with OpenCV dependencies
# Target: 5-10 FPS face detection using TensorFlow Lite
# =============================================================================

FROM arm64v8/python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for OpenCV, camera, and display
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OpenCV dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libfontconfig1 \
    # Camera support
    libv4l-dev \
    v4l-utils \
    # Build tools (for some pip packages)
    build-essential \
    cmake \
    pkg-config \
    # Image libraries
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    # Video libraries
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    # GPIO and hardware access
    libraspberrypi-bin \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app directory
WORKDIR /app

# Copy requirements first (for Docker cache optimization)
COPY backend/requirements_rpi4.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY app.py ./
COPY assets/ ./assets/

# Note: face_landmarker.task should be downloaded during setup or at runtime
# The setup_rpi4.sh script handles downloading this model

# Expose Flask port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run the application
CMD ["python", "app.py"]
