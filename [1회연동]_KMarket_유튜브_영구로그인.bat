@echo off
chcp 65001 > nul
title KTRS Market - YouTube Permanent Login
echo ========================================================
echo   🛒 KTRS Market 유튜브 계정 1회 영구 로그인 도구
echo ========================================================
echo.
cd /d "C:\ktrs_marketing_bot\kmarket-marketing-engine"
"C:\Users\zkfnt\Python311\python.exe" -u brands/kmarket/setup_youtube_profile.py
pause