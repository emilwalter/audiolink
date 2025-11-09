"""Windows auto-start functionality."""
import os
import sys
import winreg
from pathlib import Path


def get_startup_folder() -> Path:
    """Get the Windows Startup folder path."""
    startup = Path(os.getenv('APPDATA')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
    return startup


def get_registry_key():
    """Get the registry key for auto-start programs."""
    return winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
    )


def is_auto_start_enabled(app_name: str = "AudioLink") -> bool:
    """Check if the application is set to auto-start."""
    try:
        key = get_registry_key()
        try:
            winreg.QueryValueEx(key, app_name)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception as e:
        print(f"Error checking auto-start: {e}")
        return False


def enable_auto_start(app_name: str = "AudioLink") -> bool:
    """Enable auto-start for the application using registry."""
    try:
        # Get the path to the current Python script
        script_path = Path(sys.executable)
        script_file = Path(__file__).parent / "main.py"
        
        # If running as a script, use pythonw.exe to avoid console window
        if script_path.name.endswith('.exe'):
            # Running as compiled executable
            exe_path = script_path
        else:
            # Running as Python script - use pythonw.exe
            pythonw_path = script_path.parent / "pythonw.exe"
            if not pythonw_path.exists():
                pythonw_path = script_path.parent / "python.exe"
            exe_path = pythonw_path
            script_file = script_file.resolve()
        
        # Build command
        if script_path.name.endswith('.exe'):
            command = f'"{exe_path}"'
        else:
            command = f'"{exe_path}" "{script_file}"'
        
        # Add to registry
        key = get_registry_key()
        try:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
            return True
        finally:
            winreg.CloseKey(key)
    except Exception as e:
        print(f"Error enabling auto-start: {e}")
        return False


def disable_auto_start(app_name: str = "AudioLink") -> bool:
    """Disable auto-start for the application."""
    try:
        key = get_registry_key()
        try:
            winreg.DeleteValue(key, app_name)
            return True
        except FileNotFoundError:
            # Already disabled
            return True
        finally:
            winreg.CloseKey(key)
    except Exception as e:
        print(f"Error disabling auto-start: {e}")
        return False


def toggle_auto_start(app_name: str = "AudioLink") -> bool:
    """Toggle auto-start state. Returns new state."""
    if is_auto_start_enabled(app_name):
        disable_auto_start(app_name)
        return False
    else:
        enable_auto_start(app_name)
        return True

