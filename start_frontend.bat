@echo off
echo ========================================
echo   ⚡ Patch Scheduler Frontend ⚡
echo   Los Pythones Hackathon Project
echo ========================================
echo.

cd frontend

echo Starting local web server on port 8000...
echo.
echo Once started, open your browser to:
echo   http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python -m http.server 8000

pause

