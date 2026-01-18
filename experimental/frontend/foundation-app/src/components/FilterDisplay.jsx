import React, { useRef, useEffect, useState } from 'react';
import Webcam from 'react-webcam';

const FilterDisplay = ({ deviceId }) => {
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const [coords, setCoords] = useState([]);

  const videoConstraints = {
    width: 1280,
    height: 720,
    deviceId: deviceId ? { exact: deviceId } : undefined
  };

  useEffect(() => {
    const interval = setInterval(() => {
      if (webcamRef.current) {
        const screenshot = webcamRef.current.getScreenshot();
        if (screenshot) {
          sendFrameToBackend(screenshot);
        }
      }
    }, 100); // Capture every 100ms for ~10 FPS; adjust as needed

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    drawCircles();
  }, [coords]);

  const drawCircles = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'red';
    ctx.lineWidth = 10;
    ctx.fillStyle = 'rgba(255, 0, 0, 0.3)'; // semi-transparent red fill

    const clientWidth = canvas.clientWidth;
    const clientHeight = canvas.clientHeight;
    const videoAspect = 1280 / 720;
    const clientAspect = clientWidth / clientHeight;

    let scale, offsetX = 0, offsetY = 0;
    if (clientAspect > videoAspect) {
      // Client wider, bars on sides
      scale = clientHeight / 720;
      offsetX = (clientWidth - 1280 * scale) / 2;
    } else {
      // Client taller, bars on top bottom
      scale = clientWidth / 1280;
      offsetY = (clientHeight - 720 * scale) / 2;
    }

    const mirrored = true; // Webcam display is mirrored by default

    coords.forEach(([x, y]) => {
      let scaledX = offsetX + x * scale;
      if (mirrored) {
        scaledX = clientWidth - scaledX;
      }
      const scaledY = offsetY + y * scale;
      const scaledRadius = 100 * scale;
      ctx.beginPath();
      ctx.arc(scaledX, scaledY, scaledRadius, 0, 2 * Math.PI);
      ctx.fill();
      ctx.stroke();
    });
  };

  const sendFrameToBackend = async (base64Frame) => {
    try {
      console.log('Sending frame to backend...');
      const response = await fetch('http://localhost:8080/media', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ b64_input: base64Frame }),
      });
      const data = await response.json();
      console.log('Received response:', data);
      if (data.coords) {
        setCoords(data.coords);
      }
    } catch (error) {
      console.error('Error sending frame to backend:', error);
    }
  };

  return (
    <div style={styles.webcamWrapper}>
      <Webcam
        ref={webcamRef}
        audio={false}
        videoConstraints={videoConstraints}
        style={styles.webcam}
      />
      {/* Filter overlay: Applies a visual effect (e.g., tint) over the video */}
      <div style={styles.filterOverlay} />
      {/* Frame overlay: Adds a decorative border/frame around the video */}
      <div style={styles.frameOverlay} />
      {/* Canvas for backend overlays (e.g., YOLOv8 stamps) - remains on top */}
      <canvas
        ref={canvasRef}
        id="overlay-canvas"
        width={1280}
        height={720}
        style={styles.canvas}
      />
    </div>
  );
};

const styles = {
  container: {
    backgroundColor: '#1a1a1a',
    color: '#ffffff',
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    fontFamily: 'sans-serif',
  },
  header: {
    padding: '20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottom: '1px solid #333',
  },
  controls: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px'
  },
  select: {
    padding: '8px',
    borderRadius: '4px',
    backgroundColor: '#333',
    color: 'white',
    border: '1px solid #555'
  },
  main: {
    flex: 1,
    position: 'relative',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden'
  },
  webcamWrapper: {
    position: 'relative',
    width: '100vw', // Full viewport width for responsiveness
    height: '100vh', // Full viewport height for responsiveness
    // Removed fixed pixels to adjust to screen aspect ratio
  },
  webcam: {
    width: '100%',
    height: '100%',
    objectFit: 'contain',
  },
  processedImage: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  },
  // New: Filter overlay (positioned over video, below canvas)
  filterOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    background: 'rgba(0, 100, 255, 0.2)', // Example: Blue tint filter (adjust color/opacity)
    pointerEvents: 'none',
    zIndex: 5 // Above video, below canvas
  },
  // New: Frame overlay (decorative border)
  frameOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    backgroundImage: 'url(/frame.png)', // Replace with your frame image path (place in public/ folder)
    backgroundSize: 'cover', // Adjust to 'contain' if needed for aspect ratio
    backgroundRepeat: 'no-repeat',
    backgroundPosition: 'center',
    pointerEvents: 'none',
    zIndex: 8 // Above filter, below canvas
  },
  canvas: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    pointerEvents: 'none', // Allows clicks to pass through to video if needed
    zIndex: 10
  },
  footer: {
    padding: '10px 20px',
    fontSize: '0.8rem',
    color: '#888'
  }
};

export default FilterDisplay;
