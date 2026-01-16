import React from 'react';
import Webcam from 'react-webcam';

const FilterDisplay = ({ deviceId }) => {
  const videoConstraints = {
    width: 1280,
    height: 720,
    deviceId: deviceId ? { exact: deviceId } : undefined
  };

  return (
    <div style={styles.webcamWrapper}>
      <Webcam
        audio={false}
        videoConstraints={videoConstraints}
        style={styles.webcam}
      />
      {/* This canvas will receive the YOLOv8 stamp overlays */}
      <canvas id="overlay-canvas" style={styles.canvas} />
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
    width: '1280px',
    height: '720px',
    boxShadow: '0 0 50px rgba(0,0,0,0.5)'
  },
  webcam: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
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
