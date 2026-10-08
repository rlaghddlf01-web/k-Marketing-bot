@echo off
chcp 65001 > nul
title EasyTax Reddit Login
cd /d "%~dp0"
"C:\Users\zkfnt\Python311\python.exe" -u login_easytax_session.py
pause
