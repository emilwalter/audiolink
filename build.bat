@echo off
echo Building AudioLink executable...
echo.

REM Check if virtual environment exists, create if not
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install -r requirements-build.txt

REM Build the executable
echo.
echo Building executable...
pyinstaller --onefile --windowed --name AudioLink --icon=NONE --add-data "config.json;." main.py

echo.
echo Build complete! Executable is in the 'dist' folder.
echo You can run AudioLink.exe directly.
pause

