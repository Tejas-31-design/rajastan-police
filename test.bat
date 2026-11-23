@echo off
title Fraud Shield - Tests
cd /d "%~dp0backend"
set "PYEXE=C:\Users\bhada\OneDrive\Desktop\GJ POLICE\python_portable\python.exe"
if not exist "%PYEXE%" (
    set "PYEXE=python"
)
echo Running all 35 tests...
"%PYEXE%" -m pytest tests -v
pause
