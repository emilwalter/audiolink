"""Build script for creating AudioLink executable."""
import PyInstaller.__main__
import os
import sys

def build():
    """Build the AudioLink executable using PyInstaller."""
    # PyInstaller arguments
    args = [
        'main.py',
        '--onefile',  # Create a single executable file
        '--windowed',  # No console window (use --console if you want to see output)
        '--name=AudioLink',  # Name of the executable
        '--clean',  # Clean PyInstaller cache before building
        '--noconfirm',  # Replace output directory without asking
    ]
    
    # Add data files if config.json exists
    if os.path.exists('config.json'):
        args.append('--add-data=config.json;.')
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\nBuild complete! Executable is in the 'dist' folder.")
    print("You can run AudioLink.exe directly.")

if __name__ == '__main__':
    build()

