@echo off
echo ========================================
echo   ⚡ Patch Scheduler Backend ⚡
echo   Los Pythones Hackathon Project
echo ========================================
echo.

cd BackENd

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Starting Flask server on port 5000...
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python app.py

pause

