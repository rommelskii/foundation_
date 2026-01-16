import React from 'react';

const CameraSelector = ({ devices, activeDeviceId, onCameraChange }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
    <label>Source: </label>
    <select 
      value={activeDeviceId} 
      onChange={(e) => onCameraChange(e.target.value)}
      style={{ padding: '8px', borderRadius: '4px' }}
    >
      {devices.map((device, key) => (
        <option key={key} value={device.deviceId}>
          {device.label || `Camera ${key + 1}`}
        </option>
      ))}
    </select>
  </div>
);

export default CameraSelector;
