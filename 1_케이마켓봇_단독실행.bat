@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title K-Market Bot
cd /d "%~dp0kmarket-marketing-engine"

echo ========================================================
echo [K-Market] Bot Starting...
echo ========================================================
python run_kmarket.py
pause
