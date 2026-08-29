@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title K-Market Reddit Session Setup
cd /d "%~dp0kmarket-marketing-engine"

python login_kmarket_session.py
pause
