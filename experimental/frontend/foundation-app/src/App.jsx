import React from 'react';
import { useCamera } from './hooks/useCamera';
import CameraSelector from './components/CameraSelector';
import FilterDisplay from './components/FilterDisplay';

/*
 * 
 * file: App.jsx
 *
 * This contains a sample implementation of a web camera using React. We are more flexible
 * when it comes to utilizing the type of camera, its dimensions, and the way we can present
 * frames to the frontend. The only difficulty here is that we have to host this as a separate
 * REST API that will communicate to the backend in the form of base-64 (B64) encoded frames. 
 * Additional overhead will be made when the backend receives the frame, decodes it, processes it, and 
 * sends it back to the front-end for viewing. 
 */

const App = () => {
  const { devices, activeDeviceId, setActiveDeviceId } = useCamera();

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1>Foundation Filter</h1>
        <CameraSelector 
          devices={devices} 
          activeDeviceId={activeDeviceId} 
          onCameraChange={setActiveDeviceId} 
        />
      </header>

      <main style={styles.main}>
        <FilterDisplay deviceId={activeDeviceId} />
      </main>
      
      <footer style={styles.footer}>
        <p>Status: {activeDeviceId ? "System Ready" : "Initializing Hardware..."}</p>
      </footer>
    </div>
  );
};

const styles = {
  container: { backgroundColor: '#1a1a1a', color: '#fff', height: '100vh', display: 'flex', flexDirection: 'column' },
  header: { padding: '20px', display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #333' },
  main: { flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' },
  footer: { padding: '10px', fontSize: '0.8rem', color: '#888' }
};

export default App;
