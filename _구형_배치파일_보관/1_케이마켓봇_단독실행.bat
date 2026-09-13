@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title KTRS Market Bot
cd /d "%~dp0kmarket-marketing-engine"

echo ========================================================
echo [KTRS 마켓 (KTRS Market)] Bot Starting...
echo ========================================================
python run_kmarket.py
pause
