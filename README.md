# Audio Device Volume Linker

A Windows system tray application that links two audio devices together, keeping their volumes synchronized proportionally.

## Features

- **Volume Synchronization**: When you change the volume of Device 1, Device 2 automatically matches it
- **System Tray Integration**: Runs quietly in the background with a system tray icon
- **Configuration Persistence**: Remembers your device selections between sessions
- **Auto-Start**: Option to automatically start with Windows
- **Easy Device Selection**: Simple menu interface to select which devices to link

## Requirements

### For Running the Executable
- Windows 10 or later
- No Python installation needed!

### For Building from Source
- Windows 10 or later
- Python 3.7 or later
- Visual C++ Build Tools (required for pycaw)

## Installation

1. Install Visual C++ Build Tools if not already installed:
   ```bash
   choco install visualcpp-build-tools
   ```
   Or download from [Microsoft's website](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running from Source

1. Run the application:
   ```bash
   python main.py
   ```
   Or use `pythonw.exe` to run without a console window:
   ```bash
   pythonw main.py
   ```

### Running as Executable

Build a standalone executable (see [BUILD.md](BUILD.md) for details):
```bash
build.bat
```

Then run `dist/AudioLink.exe` directly - no Python installation needed!

### Using the Application

1. The application will appear in your system tray. Right-click the icon to:
   - Select Device 1 and Device 2 (bidirectional linking - changes to either device sync to the other)
   - Enable/Disable linking
   - Enable/Disable auto-start
   - Exit the application

2. Once both devices are selected, volume changes on either device will automatically sync to the other proportionally.

## Configuration

The application saves its configuration in `config.json` in the same directory as the script. This includes:
- Selected device IDs and names
- Linking enabled/disabled state
- Auto-start preference

## How It Works

The application uses the Windows Core Audio API (via `pycaw`) to:
1. Enumerate all available audio devices
2. Monitor the volume level of Device 1 every 100ms
3. When a volume change is detected, immediately set Device 2 to the same volume level

## Troubleshooting

- **Devices not found**: If a device is unplugged or unavailable, you'll need to reselect it from the menu
- **Volume not syncing**: Make sure both devices are selected and linking is enabled (checkmark visible in menu)
- **Application won't start**: Ensure all dependencies are installed and Visual C++ Build Tools are available

## License

This project is provided as-is for personal use.

