@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title Universal Expat Growth Engine - Control Center

echo ========================================================
echo [Universal Expat Growth Engine] Local Control Center
echo ========================================================
echo.

if exist "%~dp0kmarket-marketing-engine" (
    cd /d "%~dp0kmarket-marketing-engine"
) else if exist "%~dp0ktrs 마케팅 봇\kmarket-marketing-engine" (
    cd /d "%~dp0ktrs 마케팅 봇\kmarket-marketing-engine"
) else (
    cd /d "C:\Users\zkfnt\Desktop\ktrs 마케팅 봇\kmarket-marketing-engine"
)

:: Port 8000 cleanup
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: 2s delay browser open
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000"

:: Start python server
python server.py

pause
