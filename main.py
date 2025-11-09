"""Main application entry point for Audio Device Volume Linker."""
import sys
import threading
from typing import Optional
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item, Menu

from config_manager import ConfigManager
from audio_linker import AudioLinker, AudioDevice, find_device_by_id, get_all_audio_devices
from auto_start import is_auto_start_enabled, toggle_auto_start


class AudioLinkApp:
    """Main application class for audio device volume linker."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = ConfigManager()
        self.linker: Optional[AudioLinker] = None
        self.device1: Optional[AudioDevice] = None
        self.device2: Optional[AudioDevice] = None
        self.icon: Optional[pystray.Icon] = None
        self._setup_devices()
        self._setup_linker()
        self._setup_auto_start()
    
    def _setup_devices(self) -> None:
        """Load and initialize devices from configuration."""
        device1_id, device1_name = self.config.get_device1()
        device2_id, device2_name = self.config.get_device2()
        
        if device1_id:
            self.device1 = find_device_by_id(device1_id)
            if not self.device1 and device1_name:
                # Try to find by name if ID lookup fails
                self.device1 = AudioDevice(device1_id, device1_name)
                self.device1.initialize()
        
        if device2_id:
            self.device2 = find_device_by_id(device2_id)
            if not self.device2 and device2_name:
                # Try to find by name if ID lookup fails
                self.device2 = AudioDevice(device2_id, device2_name)
                self.device2.initialize()
    
    def _setup_linker(self) -> None:
        """Initialize the audio linker."""
        self.linker = AudioLinker(self.device1, self.device2)
        self.linker.set_enabled(self.config.is_linking_enabled())
        self.linker.start()
    
    def _setup_auto_start(self) -> None:
        """Sync auto-start state with registry."""
        registry_state = is_auto_start_enabled()
        config_state = self.config.is_auto_start()
        
        # If they don't match, update config to match registry
        if registry_state != config_state:
            self.config.set_auto_start(registry_state)
    
    def _create_icon_image(self) -> Image.Image:
        """Create a simple icon image for the system tray."""
        # Create a 64x64 image with transparent background
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw two overlapping circles to represent linked devices
        # Device 1 (left circle)
        draw.ellipse([8, 20, 28, 40], fill=(70, 130, 180, 255), outline=(50, 100, 150, 255), width=2)
        # Device 2 (right circle)
        draw.ellipse([36, 20, 56, 40], fill=(70, 130, 180, 255), outline=(50, 100, 150, 255), width=2)
        # Connection line
        draw.line([28, 30, 36, 30], fill=(70, 130, 180, 255), width=3)
        
        # Draw volume waves
        draw.arc([12, 8, 24, 20], start=0, end=180, fill=(100, 150, 200, 255), width=2)
        draw.arc([40, 8, 52, 20], start=0, end=180, fill=(100, 150, 200, 255), width=2)
        
        return image
    
    def _get_device1_name(self) -> str:
        """Get display name for device 1."""
        if self.device1:
            return self.device1.device_name[:30]
        _, name = self.config.get_device1()
        return name[:30] if name else "Not selected"
    
    def _get_device2_name(self) -> str:
        """Get display name for device 2."""
        if self.device2:
            return self.device2.device_name[:30]
        _, name = self.config.get_device2()
        return name[:30] if name else "Not selected"
    
    def _create_device1_menu(self) -> Menu:
        """Create submenu for device 1 selection."""
        devices = get_all_audio_devices()
        if not devices:
            return Menu(item("No devices found", None))
        
        # Get current device 1 ID for checkmark
        current_device1_id, _ = self.config.get_device1()
        
        device_items = []
        for device_id, device_name in devices:
            def make_handler(did, dname):
                def handler(icon, item):
                    self.device1 = find_device_by_id(did)
                    if self.device1:
                        self.config.set_device1(did, dname)
                        self.linker.set_devices(self.device1, self.device2)
                        self._update_menu()
                return handler
            
            # Check if this device is currently selected
            is_selected = (current_device1_id == device_id)
            checkmark = "✓ " if is_selected else ""
            
            device_items.append(
                item(
                    f"{checkmark}{device_name[:38]}",
                    make_handler(device_id, device_name),
                    checked=lambda item, did=device_id: current_device1_id == did
                )
            )
        
        return Menu(*device_items)
    
    def _create_device2_menu(self) -> Menu:
        """Create submenu for device 2 selection."""
        devices = get_all_audio_devices()
        if not devices:
            return Menu(item("No devices found", None))
        
        # Get current device 2 ID for checkmark
        current_device2_id, _ = self.config.get_device2()
        
        device_items = []
        for device_id, device_name in devices:
            def make_handler(did, dname):
                def handler(icon, item):
                    self.device2 = find_device_by_id(did)
                    if self.device2:
                        self.config.set_device2(did, dname)
                        self.linker.set_devices(self.device1, self.device2)
                        self._update_menu()
                return handler
            
            # Check if this device is currently selected
            is_selected = (current_device2_id == device_id)
            checkmark = "✓ " if is_selected else ""
            
            device_items.append(
                item(
                    f"{checkmark}{device_name[:38]}",
                    make_handler(device_id, device_name),
                    checked=lambda item, did=device_id: current_device2_id == did
                )
            )
        
        return Menu(*device_items)
    
    def _toggle_linking(self, icon, item) -> None:
        """Toggle volume linking on/off."""
        enabled = not self.linker.is_enabled()
        self.linker.set_enabled(enabled)
        self.config.set_linking_enabled(enabled)
        self._update_menu()
    
    def _toggle_auto_start(self, icon, item) -> None:
        """Toggle auto-start on/off."""
        new_state = toggle_auto_start()
        self.config.set_auto_start(new_state)
        self._update_menu()
    
    def _update_menu(self) -> None:
        """Update the system tray menu."""
        if self.icon:
            self.icon.menu = self._create_menu()
    
    def _create_menu(self) -> Menu:
        """Create the system tray menu."""
        linking_state = "✓ " if self.linker.is_enabled() else ""
        auto_start_state = "✓ " if is_auto_start_enabled() else ""
        
        menu_items = [
            item(f"{linking_state}Linking Enabled", self._toggle_linking, checked=lambda item: self.linker.is_enabled()),
            item("---", None),
            item(f"Device 1: {self._get_device1_name()}", self._create_device1_menu()),
            item(f"Device 2: {self._get_device2_name()}", self._create_device2_menu()),
            item("---", None),
            item(f"{auto_start_state}Auto-start", self._toggle_auto_start, checked=lambda item: is_auto_start_enabled()),
            item("---", None),
            item("Exit", self._on_exit)
        ]
        
        return Menu(*menu_items)
    
    def _on_exit(self, icon, item) -> None:
        """Handle application exit."""
        if self.linker:
            self.linker.stop()
        icon.stop()
    
    def run(self) -> None:
        """Run the application."""
        image = self._create_icon_image()
        menu = self._create_menu()
        
        self.icon = pystray.Icon("AudioLink", image, "Audio Device Volume Linker", menu)
        self.icon.run()


def main():
    """Main entry point."""
    try:
        app = AudioLinkApp()
        app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

