@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title Telegram Stealth Account Session Setup
cd /d "%~dp0kmarket-marketing-engine"

python setup_telethon_session.py
pause
