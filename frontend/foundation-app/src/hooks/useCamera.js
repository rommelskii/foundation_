import { useState, useEffect, useCallback } from 'react';

export const useCamera = () => {
  const [devices, setDevices] = useState([]);
  const [activeDeviceId, setActiveDeviceId] = useState('');

  const handleDevices = useCallback((mediaDevices) => {
    const videoDevices = mediaDevices.filter(({ kind }) => kind === "videoinput");
    setDevices(videoDevices);
    if (videoDevices.length > 0 && !activeDeviceId) {
      setActiveDeviceId(videoDevices[0].deviceId);
    }
  }, [activeDeviceId]);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(() => navigator.mediaDevices.enumerateDevices())
      .then(handleDevices)
      .catch(err => console.error("Hardware Error:", err));
  }, [handleDevices]);

  return { devices, activeDeviceId, setActiveDeviceId };
};
