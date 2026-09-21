@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title EasyTax Reddit Profile Pin Publisher
cd /d "%~dp0kmarket-marketing-engine"

python publish_easytax_profile_pinned.py
pause
