# Building AudioLink

## Local Build (Windows)

### Option 1: Using the batch script (Easiest)
```bash
build.bat
```

This will:
- Create a virtual environment if needed
- Install all dependencies
- Build the executable using PyInstaller
- Output `AudioLink.exe` in the `dist` folder

### Option 2: Using Python script
```bash
python build.py
```

### Option 3: Manual build
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-build.txt

# Build executable
pyinstaller --onefile --windowed --name AudioLink main.py
```

The executable will be in the `dist` folder.

## Running the Executable

After building, you can:
1. Run `dist/AudioLink.exe` directly
2. Copy it anywhere on your system
3. Add it to Windows Startup folder for auto-start

## GitHub Actions Build

The repository includes a GitHub Actions workflow that automatically builds the executable when you:
- Push a tag starting with `v` (e.g., `v1.0.0`)
- Manually trigger the workflow from the Actions tab

The built executable will be available as a release artifact.

## Notes

- The `--windowed` flag creates a GUI application without a console window
- If you want to see debug output, change `--windowed` to `--console` in the build scripts
- The executable is standalone and includes Python and all dependencies
- First run may be slightly slower as Windows extracts the bundled files

