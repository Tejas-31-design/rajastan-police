@echo off
title Fraud Shield - Rajasthan Police Hackathon 2026
echo ========================================================
echo   [Fraud Shield] Detect. Connect. Dismantle.
echo   Rajasthan Police Hackathon 2026 - PS01
echo ========================================================
echo.

cd /d "%~dp0backend"

set "PYEXE=C:\Users\bhada\OneDrive\Desktop\GJ POLICE\python_portable\python.exe"

if not exist "%PYEXE%" (
    set "PYEXE=python"
)

echo [1/2] Launching Fraud Shield server on http://localhost:8000 ...
echo [2/2] Opening browser in 3 seconds...
start "" http://localhost:8000

"%PYEXE%" run.py

pause
