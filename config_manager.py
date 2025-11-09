"""Configuration management for audio device linker."""
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Tuple


def get_config_path() -> Path:
    """Get the absolute path to the config file.
    
    When running as an executable, stores config in APPDATA.
    When running as a script, stores config next to the script.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # Store in APPDATA for persistence across different working directories
        appdata = Path(os.getenv('APPDATA', os.path.expanduser('~')))
        config_dir = appdata / 'AudioLink'
        config_dir.mkdir(exist_ok=True)
        return config_dir / 'config.json'
    else:
        # Running as Python script - store next to the script
        script_dir = Path(__file__).parent
        return script_dir / 'config.json'


class ConfigManager:
    """Manages application configuration persistence."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize config manager with config file path.
        
        Args:
            config_file: Optional custom config file path. If None, uses default location.
        """
        if config_file is None:
            self.config_file = get_config_path()
        else:
            self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.load()
    
    def _migrate_old_config(self) -> bool:
        """Try to migrate config from old locations. Returns True if migration succeeded."""
        if getattr(sys, 'frozen', False):
            # When running as executable, check old locations
            old_locations = [
                Path(sys.executable).parent / 'config.json',  # Next to executable
                Path.cwd() / 'config.json',  # Current working directory
            ]
        else:
            # When running as script, check script directory
            old_locations = [
                Path(__file__).parent / 'config.json',
            ]
        
        for old_path in old_locations:
            if old_path.exists() and old_path != self.config_file:
                try:
                    with open(old_path, 'r') as f:
                        old_config = json.load(f)
                    # Migrate the config
                    self.config = old_config
                    self.save()
                    print(f"Migrated config from {old_path} to {self.config_file}")
                    # Optionally remove old config (commented out for safety)
                    # old_path.unlink()
                    return True
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error migrating config from {old_path}: {e}")
        
        return False
    
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
            # Try to migrate from old locations
            if not self._migrate_old_config():
                # No old config found, create default
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
            # Ensure the directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
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

