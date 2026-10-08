@echo off
chcp 65001 > nul
cd /d "%~dp0"
title 💰 EasyTax 8대 국가 인스타그램 영구 로그인 센터
echo ========================================================
echo   💰 [EasyTax / KTRS 세금 환급] 8대 국가 인스타그램 로그인 센터
echo   - 8개 계정을 100% 독립 프로필로 분리하여 섀도우밴 위험 0%
echo   - 베트남, 네팔, 캄보디아, 인도네시아, 태국, 몽골, 미얀마, 우즈벡
echo ========================================================
echo.
python -u "%~dp0brands\easytax\setup_meta_multiprofile.py"
pause
