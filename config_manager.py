"""Configuration management for audio device linker."""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple


class ConfigManager:
    """Manages application configuration persistence."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize config manager with config file path."""
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
                self.config = {}
        else:
            self.config = {
                "device1_id": None,
                "device1_name": None,
                "device2_id": None,
                "device2_name": None,
                "linking_enabled": True,
                "auto_start": False
            }
            self.save()
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get_device1(self) -> Tuple[Optional[str], Optional[str]]:
        """Get device 1 ID and name."""
        return (self.config.get("device1_id"), self.config.get("device1_name"))
    
    def set_device1(self, device_id: str, device_name: str) -> None:
        """Set device 1 ID and name."""
        self.config["device1_id"] = device_id
        self.config["device1_name"] = device_name
        self.save()
    
    def get_device2(self) -> Tuple[Optional[str], Optional[str]]:
        """Get device 2 ID and name."""
        return (self.config.get("device2_id"), self.config.get("device2_name"))
    
    def set_device2(self, device_id: str, device_name: str) -> None:
        """Set device 2 ID and name."""
        self.config["device2_id"] = device_id
        self.config["device2_name"] = device_name
        self.save()
    
    def is_linking_enabled(self) -> bool:
        """Check if linking is enabled."""
        return self.config.get("linking_enabled", True)
    
    def set_linking_enabled(self, enabled: bool) -> None:
        """Set linking enabled state."""
        self.config["linking_enabled"] = enabled
        self.save()
    
    def is_auto_start(self) -> bool:
        """Check if auto-start is enabled."""
        return self.config.get("auto_start", False)
    
    def set_auto_start(self, enabled: bool) -> None:
        """Set auto-start enabled state."""
        self.config["auto_start"] = enabled
        self.save()

