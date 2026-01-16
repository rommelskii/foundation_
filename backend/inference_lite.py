"""
file: inference_lite.py

TensorFlow Lite optimized inference module for Raspberry Pi 4.
Replaces PyTorch/YOLO with lightweight TFLite models for ARM efficiency.
Target: 5-10 FPS face detection on RPi4 (4GB+ RAM recommended)
"""

import numpy as np
from PIL import Image, ImageDraw
import cv2
import os

# Use TFLite runtime (lightweight, ARM-optimized)
try:
    import tflite_runtime.interpreter as tflite
    TFLITE_AVAILABLE = True
except ImportError:
    TFLITE_AVAILABLE = False
    print("Warning: tflite-runtime not available, falling back to MediaPipe only")

# MediaPipe for face landmarks (has native ARM support)
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class FaceDetectorLite:
    """
    Lightweight face detector using TensorFlow Lite or MediaPipe.
    Optimized for Raspberry Pi 4 ARM64 architecture.
    """
    
    def __init__(self, model_path=None, use_mediapipe=True, num_threads=4):
        """
        Initialize the face detector.
        
        Args:
            model_path: Path to TFLite model file (optional)
            use_mediapipe: Use MediaPipe face detection (recommended for RPi4)
            num_threads: Number of CPU threads for inference (default: 4 for RPi4)
        """
        self.use_mediapipe = use_mediapipe
        self.num_threads = num_threads
        self.interpreter = None
        self.mp_detector = None
        
        if use_mediapipe:
            self._init_mediapipe()
        elif model_path and TFLITE_AVAILABLE:
            self._init_tflite(model_path)
        else:
            # Fallback to MediaPipe
            self.use_mediapipe = True
            self._init_mediapipe()
    
    def _init_mediapipe(self):
        """Initialize MediaPipe face detector (ARM-friendly)."""
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_detector = self.mp_face_detection.FaceDetection(
            model_selection=0,  # 0 = short-range (within 2m), faster
            min_detection_confidence=0.5
        )
        print("MediaPipe face detector initialized (ARM-optimized)")
    
    def _init_tflite(self, model_path):
        """Initialize TensorFlow Lite interpreter."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"TFLite model not found: {model_path}")
        
        self.interpreter = tflite.Interpreter(
            model_path=model_path,
            num_threads=self.num_threads
        )
        self.interpreter.allocate_tensors()
        
        # Get input/output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Get input shape
        self.input_shape = self.input_details[0]['shape']
        print(f"TFLite model loaded. Input shape: {self.input_shape}")
    
    def detect_faces(self, frame):
        """
        Detect faces in a frame.
        
        Args:
            frame: PIL Image or numpy array (RGB)
            
        Returns:
            List of face bounding boxes [[x1, y1, x2, y2], ...]
        """
        if self.use_mediapipe:
            return self._detect_mediapipe(frame)
        else:
            return self._detect_tflite(frame)
    
    def _detect_mediapipe(self, frame):
        """Detect faces using MediaPipe."""
        # Convert PIL to numpy if needed
        if isinstance(frame, Image.Image):
            np_frame = np.array(frame)
        else:
            np_frame = frame
        
        # MediaPipe expects RGB
        if len(np_frame.shape) == 3 and np_frame.shape[2] == 3:
            rgb_frame = cv2.cvtColor(np_frame, cv2.COLOR_BGR2RGB) if np_frame.shape[2] == 3 else np_frame
        else:
            rgb_frame = np_frame
        
        results = self.mp_detector.process(rgb_frame)
        
        boxes = []
        if results.detections:
            h, w = np_frame.shape[:2]
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x1 = int(bbox.xmin * w)
                y1 = int(bbox.ymin * h)
                x2 = int((bbox.xmin + bbox.width) * w)
                y2 = int((bbox.ymin + bbox.height) * h)
                boxes.append([x1, y1, x2, y2])
        
        return boxes
    
    def _detect_tflite(self, frame):
        """Detect faces using TensorFlow Lite model."""
        if self.interpreter is None:
            return []
        
        # Convert PIL to numpy if needed
        if isinstance(frame, Image.Image):
            np_frame = np.array(frame)
        else:
            np_frame = frame
        
        original_h, original_w = np_frame.shape[:2]
        
        # Preprocess: resize to model input size
        input_h, input_w = self.input_shape[1], self.input_shape[2]
        resized = cv2.resize(np_frame, (input_w, input_h))
        
        # Normalize and add batch dimension
        input_data = np.expand_dims(resized, axis=0).astype(np.float32)
        if self.input_details[0]['dtype'] == np.uint8:
            input_data = input_data.astype(np.uint8)
        else:
            input_data = input_data / 255.0
        
        # Run inference
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        
        # Get output (format depends on model)
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        
        # Parse detections (simplified - adjust based on actual model output format)
        boxes = self._parse_tflite_output(output_data, original_w, original_h)
        
        return boxes
    
    def _parse_tflite_output(self, output, img_w, img_h, threshold=0.5):
        """Parse TFLite model output to bounding boxes."""
        boxes = []
        # This is a generic parser - adjust based on your specific TFLite model
        # Common format: [batch, num_detections, 4] for boxes
        # or [batch, num_detections, 6] for [x1, y1, x2, y2, class, conf]
        
        if len(output.shape) == 3:
            for detection in output[0]:
                if len(detection) >= 5 and detection[4] > threshold:
                    x1 = int(detection[0] * img_w)
                    y1 = int(detection[1] * img_h)
                    x2 = int(detection[2] * img_w)
                    y2 = int(detection[3] * img_h)
                    boxes.append([x1, y1, x2, y2])
        
        return boxes
    
    def get_centroids(self, boxes):
        """
        Convert bounding boxes to centroids.
        
        Args:
            boxes: List of [x1, y1, x2, y2] bounding boxes
            
        Returns:
            List of [cx, cy] centroids
        """
        centroids = []
        for box in boxes:
            x1, y1, x2, y2 = box
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            centroids.append([cx, cy])
        return centroids
    
    def close(self):
        """Release resources."""
        if self.mp_detector:
            self.mp_detector.close()


class FaceLandmarkerLite:
    """
    Lightweight face landmarker using MediaPipe.
    Compatible with the original inference.py interface.
    """
    
    def __init__(self, model_path='face_landmarker.task', max_faces=5):
        """
        Initialize the face landmarker.
        
        Args:
            model_path: Path to MediaPipe face landmarker model
            max_faces: Maximum number of faces to detect
        """
        self.model_path = model_path
        self.max_faces = max_faces
        
        # Check if model exists
        if not os.path.exists(model_path):
            print(f"Warning: Face landmarker model not found at {model_path}")
            print("Download from: https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task")
            self.landmarker = None
        else:
            self._init_landmarker()
    
    def _init_landmarker(self):
        """Initialize MediaPipe face landmarker."""
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            num_faces=self.max_faces,
            running_mode=vision.RunningMode.IMAGE
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)
        print(f"MediaPipe Face Landmarker initialized (max_faces={self.max_faces})")
    
    def get_landmarks(self, frame):
        """
        Get face landmarks from frame.
        
        Args:
            frame: PIL Image
            
        Returns:
            MediaPipe detection result with face_landmarks
        """
        if self.landmarker is None:
            return None
        
        np_frame = np.array(frame)
        mp_frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=np_frame)
        
        return self.landmarker.detect(mp_frame)
    
    def get_centroids(self, frame):
        """
        Get face centroids from landmarks.
        Compatible with media_get_coords() from original inference.py.
        
        Args:
            frame: PIL Image
            
        Returns:
            List of [cx, cy] centroids
        """
        detection_result = self.get_landmarks(frame)
        
        if detection_result is None:
            return []
        
        centroids = []
        img_w, img_h = frame.size
        
        if detection_result.face_landmarks:
            for landmarks in detection_result.face_landmarks:
                sum_x = sum([lm.x for lm in landmarks])
                sum_y = sum([lm.y for lm in landmarks])
                count = len(landmarks)
                
                avg_x = sum_x / count
                avg_y = sum_y / count
                
                cx = int(avg_x * img_w)
                cy = int(avg_y * img_h)
                centroids.append([cx, cy])
        
        return centroids
    
    def close(self):
        """Release resources."""
        if self.landmarker:
            self.landmarker.close()


# =============================================================================
# Compatibility functions (drop-in replacements for inference.py)
# =============================================================================

def media_get_coords_lite(frame, model_path='face_landmarker.task', max_faces=5):
    """
    Drop-in replacement for media_get_coords() from inference.py.
    Uses MediaPipe face landmarker (ARM-optimized).
    """
    landmarker = FaceLandmarkerLite(model_path, max_faces)
    centroids = landmarker.get_centroids(frame)
    landmarker.close()
    return centroids


def detect_faces_lite(frame, use_mediapipe=True):
    """
    Lightweight face detection for RPi4.
    Returns bounding boxes instead of running YOLO.
    
    Args:
        frame: PIL Image
        use_mediapipe: Use MediaPipe (recommended for RPi4)
        
    Returns:
        List of [cx, cy] centroids
    """
    detector = FaceDetectorLite(use_mediapipe=use_mediapipe)
    boxes = detector.detect_faces(frame)
    centroids = detector.get_centroids(boxes)
    detector.close()
    return centroids


def draw_circle(coords, r, frame):
    """
    Draw circles at coordinates on frame.
    Compatible with original inference.py.
    """
    draw = ImageDraw.Draw(frame)
    for pt in coords:
        x, y = pt
        bbox = [x - r, y - r, x + r, y + r]
        draw.ellipse(bbox, fill=None, outline="red", width=10)
    return frame


def draw_boxes(boxes, frame, color="green", width=3):
    """
    Draw bounding boxes on frame.
    
    Args:
        boxes: List of [x1, y1, x2, y2] boxes
        frame: PIL Image
        color: Box color
        width: Line width
    """
    draw = ImageDraw.Draw(frame)
    for box in boxes:
        x1, y1, x2, y2 = box
        draw.rectangle([x1, y1, x2, y2], outline=color, width=width)
    return frame


# =============================================================================
# Performance monitoring for RPi4
# =============================================================================

import time

class PerformanceMonitor:
    """Track FPS and inference time on RPi4."""
    
    def __init__(self, window_size=30):
        self.times = []
        self.window_size = window_size
    
    def start_frame(self):
        self.frame_start = time.time()
    
    def end_frame(self):
        elapsed = time.time() - self.frame_start
        self.times.append(elapsed)
        if len(self.times) > self.window_size:
            self.times.pop(0)
    
    @property
    def fps(self):
        if not self.times:
            return 0
        avg_time = sum(self.times) / len(self.times)
        return 1.0 / avg_time if avg_time > 0 else 0
    
    @property
    def avg_inference_ms(self):
        if not self.times:
            return 0
        return (sum(self.times) / len(self.times)) * 1000


# =============================================================================
# Example usage for RPi4
# =============================================================================

if __name__ == "__main__":
    import cv2
    
    print("=" * 60)
    print("Face Detection Lite - Raspberry Pi 4 Optimized")
    print("=" * 60)
    
    # Initialize detector
    detector = FaceDetectorLite(use_mediapipe=True, num_threads=4)
    monitor = PerformanceMonitor()
    
    # Open camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("Press 'q' to quit")
    
    try:
        while True:
            monitor.start_frame()
            
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to RGB for detection
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            boxes = detector.detect_faces(rgb_frame)
            
            # Draw boxes
            for box in boxes:
                x1, y1, x2, y2 = box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            monitor.end_frame()
            
            # Display FPS
            fps_text = f"FPS: {monitor.fps:.1f} | Inference: {monitor.avg_inference_ms:.1f}ms"
            cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow("Face Detection (RPi4)", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()
        print(f"Average FPS: {monitor.fps:.1f}")
