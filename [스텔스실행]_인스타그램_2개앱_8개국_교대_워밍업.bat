@echo off
chcp 65001 > nul
cd /d "%~dp0"
title 📸 인스타그램 2개 앱 8개국 교대 스텔스 워밍업 실행기
echo ========================================================
echo   📸 Universal Expat Growth Engine (인스타그램 듀얼 교대)
echo   1. EasyTax (8개국 독립 계정 순환)
echo   2. K-Market (8개국 독립 계정 순환)
echo   - 2개 앱이 번갈아가며 8개국 전용 프로필로 안전하게 체류 및 좋아요
echo ========================================================
echo.
echo [1] 자동 백그라운드 스텔스 실행 (브라우저 숨김)
echo [2] 화면 직접 보며 실행 (브라우저 표시 - 시각 검증용)
echo [3] 현재 8개국 계정 연동 및 다음 회전 상태만 확인
echo.
set /p CHOICE="👉 모드를 선택하세요 (1 / 2 / 3, 기본값 1): "
if "%CHOICE%"=="" set CHOICE=1

if "%CHOICE%"=="2" (
    echo.
    echo 🖥️ 브라우저 창을 직접 띄워 2개 앱 교대 인큐베이션을 진행합니다...
    python -u "%~dp0core\meta_dual_app_orchestrator.py" --headful
) else if "%CHOICE%"=="3" (
    echo.
    python -u "%~dp0core\meta_dual_app_orchestrator.py" --status
) else (
    echo.
    echo 🚀 백그라운드 스텔스 모드로 2개 앱 교대 인큐베이션을 진행합니다...
    python -u "%~dp0core\meta_dual_app_orchestrator.py"
)

echo.
echo ========================================================
echo   실행이 완료되었습니다.
echo ========================================================
pause
