@echo off
chcp 65001 > nul
title Universal Expat Growth Engine - Control Center

echo ========================================================
echo   Universal Expat Growth Engine (로컬 컨트롤 센터)
echo   마케팅봇 서버를 가동합니다...
echo ========================================================
echo.

cd /d "C:\ktrs_marketing_bot\kmarket-marketing-engine"

rem 1. 이미 서버가 구동 중인지 포트 8080 확인
curl.exe -s -m 1 http://127.0.0.1:8080/api/status > nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] 마케팅봇 서버가 이미 가동 중입니다!
    echo 브라우저 대시보드를 즉시 화면에 띄웁니다...
    goto open_browser
)

rem 2. 충돌 포트 및 이전 프로세스 정리 (8080 및 구버전 8000)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1

rem 3. 마케팅 서버 백그라운드 시작
echo [서버 가동] 컨트롤 센터 백엔드 엔진을 시작합니다...
set NO_AUTO_BROWSER=1
start "마케팅봇 관제 서버 (닫지 마세요)" /min "C:\Users\zkfnt\Python311\python.exe" server.py

rem 4. 서버 정상 기동 확인 대기 루프 (최대 15초)
echo 서버 초기화 및 대시보드 로딩 확인 중...
set RETRIES=0

:check_loop
curl.exe -s -m 1 http://127.0.0.1:8080/api/status > nul 2>&1
if %ERRORLEVEL% equ 0 goto open_browser

set /a RETRIES+=1
if %RETRIES% geq 15 goto boot_timeout

ping 127.0.0.1 -n 2 > nul
goto check_loop

:open_browser
echo.
echo ========================================================
echo   화면에 컨트롤 센터 창이 정상적으로 표시되었습니다!
echo   접속 주소: http://127.0.0.1:8080
echo ========================================================
start http://127.0.0.1:8080
ping 127.0.0.1 -n 2 > nul
exit /b 0

:boot_timeout
echo.
echo ========================================================
echo   서버 응답 대기 시간이 초과되었습니다.
echo   브라우저 접속 시도: http://127.0.0.1:8080
echo ========================================================
start http://127.0.0.1:8080
pause
exit /b 1
