@echo off
title Universal Expat Growth Engine - Control Center

echo ========================================================
echo Universal Expat Growth Engine - Local Control Center
echo ========================================================
echo.

cd /d "%~dp0"
if exist "kmarket-marketing-engine\server.py" cd /d "%~dp0kmarket-marketing-engine"

echo Starting Local Control Center (http://localhost:8000)...
python server.py

pause
