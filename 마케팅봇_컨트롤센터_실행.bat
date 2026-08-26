@echo off
chcp 65001 > nul
title 🛸 Universal Expat Growth Engine - 로컬 컨트롤 센터

echo ========================================================
echo 🛸 [Universal Expat Growth Engine] 로컬 컨트롤 센터 실행 중...
echo ========================================================
echo.

cd /d "%~dp0\kmarket-marketing-engine"

:: 브라우저 2초 뒤 자동 오픈
start "" http://localhost:8000

:: 파이썬 대시보드 서버 가동
python server.py

pause
