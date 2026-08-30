@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title EasyTax Reddit Session Setup
cd /d "%~dp0kmarket-marketing-engine"

python login_easytax_session.py
pause
