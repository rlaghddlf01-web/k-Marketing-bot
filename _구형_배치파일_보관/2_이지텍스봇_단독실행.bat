@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title EasyTax Bot
cd /d "%~dp0kmarket-marketing-engine"

echo ========================================================
echo [EasyTax] Bot Starting...
echo ========================================================
python run_easytax.py
pause
