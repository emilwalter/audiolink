"""Audio device volume linking logic."""
import time
import threading
from typing import Optional, List, Tuple
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import cast, POINTER


class AudioDevice:
    """Represents an audio device with volume control."""
    
    def __init__(self, device_id: str, device_name: str):
        """Initialize audio device."""
        self.device_id = device_id
        self.device_name = device_name
        self._volume_interface: Optional[IAudioEndpointVolume] = None
        self._device = None
    
    def initialize(self) -> bool:
        """Initialize the device and get volume interface."""
        try:
            devices = AudioUtilities.GetAllDevices()
            for pycaw_device in devices:
                if pycaw_device.id == self.device_id:
                    self._device = pycaw_device
                    try:
                        # Get the volume interface using EndpointVolume property
                        if hasattr(pycaw_device, 'EndpointVolume'):
                            volume_interface = pycaw_device.EndpointVolume
                            if volume_interface:
                                # Cast to IAudioEndpointVolume pointer
                                self._volume_interface = cast(volume_interface, POINTER(IAudioEndpointVolume))
                                if self._volume_interface:
                                    return True
                        else:
                            print(f"Device {self.device_name} does not have EndpointVolume property")
                            return False
                    except AttributeError as e:
                        print(f"Device {self.device_name} does not support volume control: {e}")
                        return False
                    except Exception as e:
                        print(f"Error getting volume interface for {self.device_name}: {e}")
                        import traceback
                        traceback.print_exc()
                        return False
            return False
        except Exception as e:
            print(f"Error initializing device {self.device_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_volume(self) -> Optional[float]:
        """Get current volume level (0.0 to 1.0)."""
        if not self._volume_interface:
            return None
        try:
            # Call methods directly on the pointer
            return self._volume_interface.GetMasterVolumeLevelScalar()
        except Exception as e:
            print(f"Error getting volume for {self.device_name}: {e}")
            return None
    
    def set_volume(self, volume: float) -> bool:
        """Set volume level (0.0 to 1.0)."""
        if not self._volume_interface:
            return False
        try:
            # Clamp volume to valid range
            volume = max(0.0, min(1.0, volume))
            # Call methods directly on the pointer
            self._volume_interface.SetMasterVolumeLevelScalar(volume, None)
            return True
        except Exception as e:
            print(f"Error setting volume for {self.device_name}: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if device is available."""
        return self._volume_interface is not None


class AudioLinker:
    """Links volume between two audio devices."""
    
    def __init__(self, device1: Optional[AudioDevice], device2: Optional[AudioDevice]):
        """Initialize audio linker with two devices."""
        self.device1 = device1
        self.device2 = device2
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._enabled = True
        self._syncing = False  # Flag to prevent feedback loops
    
    def set_devices(self, device1: Optional[AudioDevice], device2: Optional[AudioDevice]) -> None:
        """Update the devices being linked."""
        with self._lock:
            self.device1 = device1
            self.device2 = device2
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable linking."""
        with self._lock:
            self._enabled = enabled
    
    def is_enabled(self) -> bool:
        """Check if linking is enabled."""
        return self._enabled
    
    def start(self) -> None:
        """Start the volume linking thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop the volume linking thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop that synchronizes volumes bidirectionally."""
        last_volume1 = None
        last_volume2 = None
        
        while self._running:
            try:
                with self._lock:
                    if not self._enabled:
                        time.sleep(0.1)
                        continue
                    
                    if not self.device1 or not self.device2:
                        time.sleep(0.1)
                        continue
                    
                    # Reinitialize devices if needed
                    if not self.device1.is_available():
                        if not self.device1.initialize():
                            time.sleep(0.5)
                            continue
                    
                    if not self.device2.is_available():
                        if not self.device2.initialize():
                            time.sleep(0.5)
                            continue
                    
                    # Skip if we're currently syncing to avoid feedback loops
                    if self._syncing:
                        time.sleep(0.1)
                        continue
                    
                    # Get current volumes from both devices
                    current_volume1 = self.device1.get_volume()
                    current_volume2 = self.device2.get_volume()
                    
                    if current_volume1 is None or current_volume2 is None:
                        time.sleep(0.1)
                        continue
                    
                    # Check if device 1 volume changed
                    if last_volume1 is None or abs(current_volume1 - last_volume1) > 0.001:
                        # Device 1 changed, sync to device 2
                        self._syncing = True
                        self.device2.set_volume(current_volume1)
                        last_volume1 = current_volume1
                        last_volume2 = current_volume1  # Update both to prevent feedback
                        self._syncing = False
                    # Check if device 2 volume changed
                    elif last_volume2 is None or abs(current_volume2 - last_volume2) > 0.001:
                        # Device 2 changed, sync to device 1
                        self._syncing = True
                        self.device1.set_volume(current_volume2)
                        last_volume2 = current_volume2
                        last_volume1 = current_volume2  # Update both to prevent feedback
                        self._syncing = False
                    else:
                        # No change detected, update last known volumes
                        last_volume1 = current_volume1
                        last_volume2 = current_volume2
                
                time.sleep(0.1)  # Poll every 100ms
                
            except Exception as e:
                print(f"Error in monitor loop: {e}")
                self._syncing = False
                time.sleep(0.5)


def get_all_audio_devices() -> List[Tuple[str, str]]:
    """Get list of available output audio devices as (id, name) tuples, deduplicated."""
    devices = []
    seen_names = set()
    try:
        all_devices = AudioUtilities.GetAllDevices()
        for device in all_devices:
            # Filter to only output devices (render devices)
            # Check if device has DataFlow property (eRender = output, eCapture = input)
            # Also verify it has EndpointVolume for volume control
            try:
                # Check DataFlow if available (eRender = 0 = output device)
                if hasattr(device, 'DataFlow'):
                    # eRender (0) = output, eCapture (1) = input
                    if device.DataFlow != 0:  # Not eRender, skip input devices
                        continue
                
                # Verify device supports volume control
                if hasattr(device, 'EndpointVolume'):
                    device_name = device.FriendlyName
                    # Deduplicate by name - keep first occurrence of each unique name
                    if device_name not in seen_names:
                        seen_names.add(device_name)
                        devices.append((device.id, device_name))
            except (AttributeError, Exception):
                # Skip devices that don't support volume control or can't be accessed
                continue
    except Exception as e:
        print(f"Error enumerating devices: {e}")
    return devices


def find_device_by_id(device_id: str) -> Optional[AudioDevice]:
    """Find and initialize an audio device by ID."""
    try:
        devices = AudioUtilities.GetAllDevices()
        for device in devices:
            if device.id == device_id:
                audio_device = AudioDevice(device.id, device.FriendlyName)
                if audio_device.initialize():
                    return audio_device
    except Exception as e:
        print(f"Error finding device {device_id}: {e}")
    return None


def find_device_by_name(device_name: str) -> Optional[AudioDevice]:
    """Find and initialize an audio device by name."""
    try:
        devices = AudioUtilities.GetAllDevices()
        for device in devices:
            if device.FriendlyName == device_name:
                audio_device = AudioDevice(device.id, device.FriendlyName)
                if audio_device.initialize():
                    return audio_device
    except Exception as e:
        print(f"Error finding device {device_name}: {e}")
    return None

