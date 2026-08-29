@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title Universal Expat Growth Engine - Control Center

echo ========================================================
echo [Universal Expat Growth Engine] Local Control Center
echo ========================================================
echo.

cd /d "%~dp0kmarket-marketing-engine"

:: Port 8000 cleanup
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: 2s delay browser open (safe ping delay)
start /b cmd /c "ping 127.0.0.1 -n 3 >nul && start http://localhost:8000"

:: Start python server
python server.py

pause
